from datetime import datetime

from app.models.problem_pic import ProblemPIC
from app.models.improvement_pic import ImprovementPIC

from app.repositories.problem_repository import ProblemRepository
from app.repositories.problem_pic_repository import ProblemPICRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.improvement_repository import ImprovementRepository
from app.repositories.improvement_pic_repository import ImprovementPICRepository

from app.services.base_service import BaseService

from app.core.transaction_manager import TransactionManager

from app.core.choices.problem import (
    PROBLEM_PRIORITY,
    ProblemStatus,
    PICStatus,
)


class ProblemAssignmentService(BaseService):

    def __init__(self):
        super().__init__()

        self.problem_repository = ProblemRepository()
        self.problem_pic_repository = ProblemPICRepository()
        self.employee_repository = EmployeeRepository()

        self.improvement_repository = ImprovementRepository()
        self.improvement_pic_repository = ImprovementPICRepository()

    # =============================================================
    # ASSIGN PROBLEM
    # =============================================================

    def assign(
        self,
        problem_id,
        priority,
        employee_ids,
        target_date,
        assigned_by=None,
    ):

        try:

            # =====================================================
            # GET PROBLEM
            # =====================================================

            problem = self.problem_repository.get_by_id(
                problem_id
            )

            self.validate_exists(
                problem,
                "Problem"
            )

            # =====================================================
            # VALIDATE PRIORITY
            # =====================================================

            valid_priorities = [
                value
                for value, label in PROBLEM_PRIORITY
            ]

            if priority not in valid_priorities:

                return self.failed(
                    "Invalid problem priority."
                )

            # =====================================================
            # VALIDATE TARGET DATE
            # =====================================================

            if not target_date:

                return self.failed(
                    "Target Date is required."
                )

            try:

                target_date = datetime.strptime(
                    target_date,
                    "%Y-%m-%d"
                ).date()

            except (ValueError, TypeError):

                return self.failed(
                    "Invalid Target Date."
                )

            # =====================================================
            # VALIDATE PIC
            # =====================================================

            if not employee_ids:

                return self.failed(
                    "Please select at least one PIC."
                )

            try:

                employee_ids = list(
                    dict.fromkeys(
                        int(employee_id)
                        for employee_id in employee_ids
                    )
                )

            except (ValueError, TypeError):

                return self.failed(
                    "Invalid employee selection."
                )

            # =====================================================
            # GET EMPLOYEES
            # =====================================================

            employees = []

            for employee_id in employee_ids:

                employee = (
                    self.employee_repository
                    .get_by_id(employee_id)
                )

                if not employee:

                    return self.failed(
                        f"Employee ID {employee_id} not found."
                    )

                if not employee.is_active:

                    return self.failed(
                        f"Employee ID {employee_id} is inactive."
                    )

                employees.append(employee)

            # =====================================================
            # LEADER
            # =====================================================

            leader_employee = employees[0]

            # =====================================================
            # GET RELATED IMPROVEMENTS
            # =====================================================

            improvements = (
                self.improvement_repository
                .find_by_problem_id(problem_id)
            )

            # =====================================================
            # UPDATE ASSIGNMENT
            # =====================================================

            with TransactionManager():

                # -------------------------------------------------
                # Update Problem
                # -------------------------------------------------

                problem.priority = priority
                problem.target_date = target_date
                problem.status = ProblemStatus.IN_PROGRESS
                problem.updated_by = assigned_by

                self.problem_repository.update(
                    problem
                )

                # -------------------------------------------------
                # Delete existing Improvement PIC
                # -------------------------------------------------

                if improvements:

                    (
                        self.improvement_pic_repository
                        .delete_by_problem_id(problem_id)
                    )

                # -------------------------------------------------
                # Delete existing Problem PIC
                # -------------------------------------------------

                (
                    self.problem_pic_repository
                    .delete_by_problem_id(problem_id)
                )

                # -------------------------------------------------
                # Create new Problem PIC
                # -------------------------------------------------

                for index, employee in enumerate(
                    employees
                ):

                    problem_pic = ProblemPIC()

                    problem_pic.problem_id = problem_id
                    problem_pic.employee_id = employee.id

                    problem_pic.is_leader = (
                        index == 0
                    )

                    problem_pic.status = (
                        PICStatus.ASSIGNED
                    )

                    problem_pic.created_by = assigned_by
                    problem_pic.updated_by = assigned_by

                    self.problem_pic_repository.create(
                        problem_pic
                    )

                # -------------------------------------------------
                # Update related Improvements
                # -------------------------------------------------

                for improvement in improvements:

                    improvement.owner_employee_id = (
                        leader_employee.id
                    )

                    improvement.updated_by = assigned_by

                    self.improvement_repository.update(
                        improvement
                    )

                    # ---------------------------------------------
                    # Create Improvement PIC
                    # ---------------------------------------------

                    for index, employee in enumerate(
                        employees
                    ):

                        improvement_pic = ImprovementPIC()

                        improvement_pic.improvement_id = (
                            improvement.id
                        )

                        improvement_pic.employee_id = (
                            employee.id
                        )

                        improvement_pic.is_leader = (
                            index == 0
                        )

                        improvement_pic.status = "ASSIGNED"

                        improvement_pic.created_by = (
                            assigned_by
                        )

                        improvement_pic.updated_by = (
                            assigned_by
                        )

                        self.improvement_pic_repository.create(
                            improvement_pic
                        )

            # =====================================================
            # QUEUE NOTIFICATION TO CELERY
            # =====================================================
            #
            # Transaction di atas sudah selesai / COMMIT.
            #
            # Celery hanya menerima problem_id.
            #
            # Worker nantinya akan mengambil kembali Problem
            # dari database dan menjalankan notification.
            #
            # =====================================================

            try:

                from app.tasks.notification_tasks import (
                    send_problem_assigned_notification,
                )

                task = (
                    send_problem_assigned_notification.delay(
                        problem.id
                    )
                )

                print(
                    "=========================================="
                )

                print(
                    "PROBLEM ASSIGNED NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
                )

                print(
                    "Problem ID:",
                    problem.id
                )

                print(
                    "Celery Task ID:",
                    task.id
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                # -------------------------------------------------
                # Notification queue failure must NOT make
                # Problem Assignment fail.
                # -------------------------------------------------

                print(
                    "=========================================="
                )

                print(
                    "PROBLEM ASSIGNED "
                    "CELERY NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

                print(
                    "=========================================="
                )

            # =====================================================
            # SUCCESS
            # =====================================================

            return self.success(
                "Problem assigned successfully.",
                problem
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )