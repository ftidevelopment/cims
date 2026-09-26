from decimal import Decimal, InvalidOperation
from datetime import date, datetime

from app.extensions import db

from app.models.improvement import (
    Improvement,
)

from app.models.improvement_pic import (
    ImprovementPIC,
)

from app.repositories.improvement_repository import (
    ImprovementRepository,
)

from app.repositories.improvement_pic_repository import (
    ImprovementPICRepository,
)

from app.repositories.problem_repository import (
    ProblemRepository,
)

from app.repositories.problem_pic_repository import (
    ProblemPICRepository,
)

from app.services.number_sequence_service import (
    NumberSequenceService,
)

from app.core.transaction_manager import (
    TransactionManager,
)
from app.services.notification_service import (
    NotificationService,
)
from app.core.notification_events import (
    NotificationEvent,
)


class ImprovementService:

    def __init__(self):

        self.improvement_repository = (
            ImprovementRepository()
        )

        self.improvement_pic_repository = (
            ImprovementPICRepository()
        )

        self.problem_repository = (
            ProblemRepository()
        )

        self.problem_pic_repository = (
            ProblemPICRepository()
        )

        self.number_sequence_service = (
            NumberSequenceService()
        )

        self.notification_service = (
            NotificationService()
        )

    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(
        self,
        keyword=None,
        approval=None,
        date_from=None,
        date_to=None,
        created_by=None,
        page=1,
        per_page=10,
        sort_order="desc",
        sort_by=None,
    ):

        return self.improvement_repository.get_all(
            keyword=keyword,
            approval=approval,
            date_from=date_from,
            date_to=date_to,
            created_by=created_by,
            page=page,
            per_page=per_page,
            sort_order=sort_order,
            sort_by=sort_by,
        )
    # ==================================================
    # GET BY ID
    # ==================================================

    def get_by_id(
        self,
        improvement_id
    ):

        return (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

    # ==================================================
    # GET BY PROBLEM
    # ==================================================

    def get_by_problem(
        self,
        problem_id
    ):

        return (
            self.improvement_repository
            .find_by_problem_id(
                problem_id
            )
        )

    # ==================================================
    # CREATE IMPROVEMENT
    # ==================================================

    # ==================================================
    # CREATE IMPROVEMENT
    # ==================================================

    def create_improvement(
        self,
        problem_id,
        title,
        description,
        created_by_employee_id,
        root_cause=None,
        improvement_plan=None,
        improvement_cost=0,
        estimated_time_saving=0,
        estimated_cost_saving=0,
        estimated_benefit=0
    ):

        # ==========================================
        # Validate Creator Employee
        # ==========================================

        if not created_by_employee_id:

            raise ValueError(
                "Logged-in user is not linked "
                "to an employee."
            )

        # ==========================================
        # Get Problem
        # ==========================================

        problem = (
            self.problem_repository
            .get_by_id(
                problem_id
            )
        )

        if not problem:

            raise ValueError(
                "Problem not found."
            )

        # ==========================================
        # Check Problem Status
        # ==========================================

        if problem.status == "Closed":

            raise ValueError(
                "Cannot create improvement "
                "for a closed problem."
            )

        # ==========================================
        # Get Problem PIC
        # ==========================================

        problem_pics = (
            self.problem_pic_repository
            .get_by_problem_id(
                problem_id
            )
        )

        if not problem_pics:

            raise ValueError(
                "Problem must have at least one PIC."
            )

        # ==========================================
        # Get Active Problem PIC
        # ==========================================

        active_problem_pics = [
            pic
            for pic in problem_pics
            if pic.is_active
        ]

        if not active_problem_pics:

            raise ValueError(
                "Problem must have at least one "
                "active PIC."
            )

        # ==========================================
        # Find Problem PIC Leader
        # ==========================================

        leader_pic = next(
            (
                pic
                for pic in active_problem_pics
                if pic.is_leader
            ),
            None,
        )

        if not leader_pic:

            raise ValueError(
                "Problem PIC Leader is not defined. "
                "Please assign a Problem PIC Leader "
                "first."
            )

        # ==========================================
        # Validate Required Fields
        # ==========================================

        if not title or not title.strip():

            raise ValueError(
                "Improvement title is required."
            )

        if not description or not description.strip():

            raise ValueError(
                "Improvement description is required."
            )

        # ==========================================
        # Generate Improvement Number
        # ==========================================

        today = (
            datetime.now()
            .strftime("%Y%m%d")
        )

        improvement_no = (
            self.number_sequence_service
            .get_next_number(
                sequence_name="improvement",
                prefix=f"I{today[2:6]}",
                digit=4
            )
        )

        # ==========================================
        # Convert Numeric Values
        # ==========================================

        improvement_cost = (
            self._to_decimal(
                improvement_cost
            )
        )

        estimated_time_saving = (
            self._to_integer(
                estimated_time_saving
            )
        )

        estimated_cost_saving = (
            self._to_decimal(
                estimated_cost_saving
            )
        )

        estimated_benefit = (
            self._to_decimal(
                estimated_benefit
            )
        )

        # ==========================================
        # Create Improvement
        # ==========================================

        improvement = Improvement(

            problem_id=problem_id,

            improvement_no=improvement_no,

            title=title.strip(),

            description=description.strip(),

            root_cause=(
                root_cause.strip()
                if root_cause
                else None
            ),

            improvement_plan=(
                improvement_plan.strip()
                if improvement_plan
                else None
            ),

            improvement_cost=(
                improvement_cost
            ),

            estimated_time_saving=(
                estimated_time_saving
            ),

            estimated_cost_saving=(
                estimated_cost_saving
            ),

            estimated_benefit=(
                estimated_benefit
            ),

            # ======================================
            # Improvement Owner
            # ======================================

            owner_employee_id=(
                created_by_employee_id
            ),
        )

        # ==========================================
        # Save Improvement + PIC
        #
        # Everything is saved in ONE transaction.
        # ==========================================

        with TransactionManager():

            # --------------------------------------
            # Create Improvement
            # --------------------------------------

            self.improvement_repository.create(
                improvement
            )

            # --------------------------------------
            # Force INSERT
            # --------------------------------------

            db.session.flush()

            # --------------------------------------
            # Safety Check
            # --------------------------------------

            if not improvement.id:

                raise ValueError(
                    "Failed to generate Improvement ID."
                )

            # --------------------------------------
            # Create Improvement PIC
            # --------------------------------------

            for problem_pic in active_problem_pics:

                improvement_pic = (
                    ImprovementPIC()
                )

                # ----------------------------------
                # Improvement ID
                # ----------------------------------

                improvement_pic.improvement_id = (
                    improvement.id
                )

                # ----------------------------------
                # Employee
                # ----------------------------------

                improvement_pic.employee_id = (
                    problem_pic.employee_id
                )

                # ----------------------------------
                # Preserve Leader
                # ----------------------------------

                improvement_pic.is_leader = (
                    problem_pic.is_leader
                )

                # ----------------------------------
                # Status
                # ----------------------------------

                improvement_pic.status = (
                    "ASSIGNED"
                )

                # ----------------------------------
                # Active
                # ----------------------------------

                improvement_pic.is_active = True

                # ----------------------------------
                # Audit fields
                # ----------------------------------

                improvement_pic.created_by = None
                improvement_pic.updated_by = None

                # ----------------------------------
                # Save Improvement PIC
                # ----------------------------------

                self.improvement_pic_repository.create(
                    improvement_pic
                )

        # ==================================================
        # QUEUE NOTIFICATION TO CELERY
        # ==================================================
        #
        # Transaction di atas sudah selesai / COMMIT.
        #
        # Jangan kirim object Improvement atau Problem
        # ke Celery.
        #
        # Celery hanya menerima improvement.id.
        #
        # Worker akan mengambil kembali Improvement
        # dan Problem dari database.
        #
        # ==================================================

        try:

            from app.tasks.notification_tasks import (
                send_improvement_created_notification,
            )

            task = (
                send_improvement_created_notification.delay(
                    improvement.id
                )
            )

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT CREATED NOTIFICATION "
                "SUCCESSFULLY QUEUED"
            )

            print(
                "Improvement ID:",
                improvement.id
            )

            print(
                "Improvement No:",
                improvement.improvement_no
            )

            print(
                "Celery Task ID:",
                task.id
            )

            print(
                "=========================================="
            )

        except Exception as ex:

            # --------------------------------------------------
            # Notification queue failure must NOT make
            # Improvement creation fail.
            # --------------------------------------------------

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT CREATED "
                "CELERY NOTIFICATION QUEUE ERROR:",
                str(ex)
            )

            print(
                "=========================================="
            )

        # ==========================================
        # Return
        # ==========================================

        return improvement
    
    # ==================================================
    # ASSIGN OWNER
    # ==================================================

    def assign_owner(
        self,
        improvement_id,
        owner_employee_id,
        assigned_by_employee_id=None,
    ):

        # ==========================================
        # Get Improvement
        # ==========================================

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # ==========================================
        # Validate Owner
        # ==========================================

        if not owner_employee_id:

            raise ValueError(
                "Improvement Owner is required."
            )

        # ==========================================
        # Get Employee
        # ==========================================

        from app.models.employee import Employee

        owner = (
            Employee.query
            .filter(
                Employee.id
                == owner_employee_id
            )
            .filter(
                Employee.status
                == "ACTIVE"
            )
            .filter(
                Employee.user.has()
            )
            .first()
        )

        if not owner:

            raise ValueError(
                "Selected employee is not an "
                "active employee with a User Account."
            )

        # ==========================================
        # Save
        # ==========================================

        improvement.owner_employee_id = (
            owner_employee_id
        )

        if assigned_by_employee_id:

            improvement.updated_by = (
                assigned_by_employee_id
            )

        self.improvement_repository.update(
            improvement
        )

        db.session.commit()

        return improvement

    # ==================================================
    # UPDATE IMPROVEMENT
    # ==================================================

    # ==================================================
    # UPDATE IMPROVEMENT
    # ==================================================

    def update_improvement(
        self,
        improvement_id,
        title,
        description,
        root_cause=None,
        improvement_plan=None,
        improvement_cost=0,
        estimated_time_saving=0,
        estimated_cost_saving=0,
        estimated_benefit=0
    ):

        # --------------------------------------------------
        # Get Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Get Problem
        # --------------------------------------------------

        problem = (
            self.problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            raise ValueError(
                "Related problem not found."
            )

        # --------------------------------------------------
        # Check Problem Status
        # --------------------------------------------------

        if problem.status == "Closed":

            raise ValueError(
                "Cannot edit improvement "
                "because the problem is closed."
            )

        # --------------------------------------------------
        # Validate Required Fields
        # --------------------------------------------------

        if not title or not title.strip():

            raise ValueError(
                "Improvement title is required."
            )

        if not description or not description.strip():

            raise ValueError(
                "Improvement description is required."
            )

        # --------------------------------------------------
        # Convert Numeric Values
        # --------------------------------------------------

        improvement_cost = (
            self._to_decimal(
                improvement_cost
            )
        )

        estimated_cost_saving = (
            self._to_decimal(
                estimated_cost_saving
            )
        )

        estimated_benefit = (
            self._to_decimal(
                estimated_benefit
            )
        )

        estimated_time_saving = (
            self._to_integer(
                estimated_time_saving
            )
        )

        # --------------------------------------------------
        # Update
        # --------------------------------------------------

        improvement.title = (
            title.strip()
        )

        improvement.description = (
            description.strip()
        )

        improvement.root_cause = (
            root_cause.strip()
            if root_cause
            else None
        )

        improvement.improvement_plan = (
            improvement_plan.strip()
            if improvement_plan
            else None
        )

        improvement.improvement_cost = (
            improvement_cost
        )

        improvement.estimated_time_saving = (
            estimated_time_saving
        )

        improvement.estimated_cost_saving = (
            estimated_cost_saving
        )

        improvement.estimated_benefit = (
            estimated_benefit
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        self.improvement_repository.update(
            improvement
        )

        db.session.commit()

        # ==================================================
        # QUEUE NOTIFICATION TO CELERY
        # ==================================================
        #
        # Database sudah berhasil COMMIT.
        #
        # Celery hanya menerima improvement_id.
        #
        # Worker akan mengambil kembali Improvement
        # dan Related Problem dari database.
        #
        # ==================================================

        try:

            from app.tasks.notification_tasks import (
                send_improvement_updated_notification,
            )

            task = (
                send_improvement_updated_notification.delay(
                    improvement.id
                )
            )

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT UPDATED NOTIFICATION "
                "SUCCESSFULLY QUEUED"
            )

            print(
                "Improvement ID:",
                improvement.id
            )

            print(
                "Improvement No:",
                improvement.improvement_no
            )

            print(
                "Celery Task ID:",
                task.id
            )

            print(
                "=========================================="
            )

        except Exception as ex:

            # --------------------------------------------------
            # Notification queue failure must NOT make
            # Improvement update fail.
            # --------------------------------------------------

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT UPDATED "
                "CELERY NOTIFICATION QUEUE ERROR:",
                str(ex)
            )

            print(
                "=========================================="
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return improvement

    # ==================================================
    # UPDATE IMPLEMENTATION
    # ==================================================

    def update_implementation(
        self,
        improvement_id,
        implementation_result
    ):

        # --------------------------------------------------
        # Get Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Validate Implementation Result
        # --------------------------------------------------

        if not implementation_result:

            raise ValueError(
                "Implementation result is required."
            )

        implementation_result = (
            implementation_result.strip()
        )

        if not implementation_result:

            raise ValueError(
                "Implementation result is required."
            )

        # --------------------------------------------------
        # Get Related Problem
        # --------------------------------------------------

        problem = (
            self.problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            raise ValueError(
                "Related problem not found."
            )

        # --------------------------------------------------
        # Update Implementation Result
        # --------------------------------------------------

        improvement.implementation_result = (
            implementation_result
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        self.improvement_repository.update(
            improvement
        )

        db.session.commit()

        # ==================================================
        # QUEUE NOTIFICATION TO CELERY
        # ==================================================
        #
        # Database sudah berhasil COMMIT.
        #
        # Celery hanya menerima improvement_id.
        #
        # Worker akan mengambil kembali Improvement
        # dan Related Problem dari database.
        #
        # ==================================================

        try:

            from app.tasks.notification_tasks import (
                send_improvement_implemented_notification,
            )

            task = (
                send_improvement_implemented_notification.delay(
                    improvement.id
                )
            )

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT IMPLEMENTED NOTIFICATION "
                "SUCCESSFULLY QUEUED"
            )

            print(
                "Improvement ID:",
                improvement.id
            )

            print(
                "Improvement No:",
                improvement.improvement_no
            )

            print(
                "Celery Task ID:",
                task.id
            )

            print(
                "=========================================="
            )

        except Exception as ex:

            # --------------------------------------------------
            # Notification queue failure must NOT make
            # implementation update fail.
            # --------------------------------------------------

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT IMPLEMENTED "
                "CELERY NOTIFICATION QUEUE ERROR:",
                str(ex)
            )

            print(
                "=========================================="
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return improvement

    
 
    # ==================================================
    # VERIFY IMPROVEMENT
    # ==================================================

    def verify_improvement(
        self,
        improvement_id,
        verification_result
    ):

        # --------------------------------------------------
        # Get Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Validate Verification Result
        # --------------------------------------------------

        if not verification_result:

            raise ValueError(
                "Verification result is required."
            )

        verification_result = (
            verification_result.strip()
        )

        if not verification_result:

            raise ValueError(
                "Verification result is required."
            )

        # --------------------------------------------------
        # Check Implementation
        # --------------------------------------------------

        if not improvement.implementation_result:

            raise ValueError(
                "Implementation result must be "
                "completed before verification."
            )

        # --------------------------------------------------
        # Get Related Problem
        # --------------------------------------------------

        problem = (
            self.problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            raise ValueError(
                "Related problem not found."
            )

        # --------------------------------------------------
        # Update Verification Result
        # --------------------------------------------------

        improvement.verification_result = (
            verification_result
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        self.improvement_repository.update(
            improvement
        )

        db.session.commit()

        # ==================================================
        # QUEUE NOTIFICATION TO CELERY
        # ==================================================
        #
        # Database sudah berhasil COMMIT.
        #
        # Celery hanya menerima improvement_id.
        #
        # Worker akan mengambil kembali Improvement
        # dan Related Problem dari database.
        #
        # ==================================================

        try:

            from app.tasks.notification_tasks import (
                send_improvement_verified_notification,
            )

            task = (
                send_improvement_verified_notification.delay(
                    improvement.id
                )
            )

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT VERIFIED NOTIFICATION "
                "SUCCESSFULLY QUEUED"
            )

            print(
                "Improvement ID:",
                improvement.id
            )

            print(
                "Improvement No:",
                improvement.improvement_no
            )

            print(
                "Celery Task ID:",
                task.id
            )

            print(
                "=========================================="
            )

        except Exception as ex:

            # --------------------------------------------------
            # Notification queue failure must NOT make
            # verification fail.
            # --------------------------------------------------

            print(
                "=========================================="
            )

            print(
                "IMPROVEMENT VERIFIED "
                "CELERY NOTIFICATION QUEUE ERROR:",
                str(ex)
            )

            print(
                "=========================================="
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return improvement

    # ==================================================
    # APPROVE IMPROVEMENT
    # ==================================================
    def approve_improvement(
        self,
        improvement_id,
        approved_by_employee_id
    ):

        # --------------------------------------------------
        # Get Improvement
        # --------------------------------------------------

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        # --------------------------------------------------
        # Get Related Problem
        # --------------------------------------------------

        problem = (
            self.problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            raise ValueError(
                "Related problem not found."
            )

        # --------------------------------------------------
        # Check Problem Status
        # --------------------------------------------------

        if problem.status == "Closed":

            raise ValueError(
                "Problem is already closed."
            )

        # --------------------------------------------------
        # Check Verification
        # --------------------------------------------------

        if not improvement.verification_result:

            raise ValueError(
                "Improvement must be verified "
                "before approval."
            )

        # --------------------------------------------------
        # Validate Approver
        # --------------------------------------------------

        if not approved_by_employee_id:

            raise ValueError(
                "Approving employee is required."
            )

        # ==================================================
        # APPROVAL
        # ==================================================

        improvement.approved_by_employee_id = (
            approved_by_employee_id
        )

        improvement.approved_date = (
            date.today()
        )

        # --------------------------------------------------
        # Close Problem
        # --------------------------------------------------

        problem.status = "Closed"

        problem.closed_date = (
            date.today()
        )

        # --------------------------------------------------
        # Save Improvement
        # --------------------------------------------------

        self.improvement_repository.update(
            improvement
        )

        # --------------------------------------------------
        # Save Problem
        # --------------------------------------------------

        self.problem_repository.update(
            problem
        )

        # --------------------------------------------------
        # Commit Database
        # --------------------------------------------------

        db.session.commit()

        # ==================================================
        # QUEUE NOTIFICATION
        # AFTER DATABASE COMMIT
        # ==================================================

        try:

            from app.tasks.notification_tasks import (
                send_improvement_approved_notification
            )

            task = (
                send_improvement_approved_notification
                .delay(
                    improvement.id
                )
            )

            print(
                "IMPROVEMENT APPROVED NOTIFICATION "
                "SUCCESSFULLY QUEUED",
                improvement.id,
                improvement.improvement_no,
                task.id,
            )

        except Exception as ex:

            # --------------------------------------------------
            # Notification Queue Failure
            #
            # Approval database sudah berhasil.
            # Jangan rollback approval.
            # --------------------------------------------------

            print(
                "IMPROVEMENT APPROVED CELERY "
                "NOTIFICATION QUEUE ERROR:",
                str(ex)
            )

        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return improvement
    # ==================================================
    # BENEFIT CALCULATION
    # ==================================================

    def calculate_benefit(
        self,
        improvement_id
    ):

        improvement = (
            self.improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            raise ValueError(
                "Improvement not found."
            )

        cost = Decimal(
            improvement.improvement_cost or 0
        )

        cost_saving = Decimal(
            improvement.estimated_cost_saving or 0
        )

        benefit = Decimal(
            improvement.estimated_benefit or 0
        )

        net_benefit = (
            benefit - cost
        )

        roi = Decimal("0")

        if cost > 0:

            roi = (
                net_benefit
                / cost
                * Decimal("100")
            )

        return {
            "improvement_cost": cost,

            "estimated_cost_saving": (
                cost_saving
            ),

            "estimated_time_saving": (
                improvement
                .estimated_time_saving
                or 0
            ),

            "estimated_benefit": (
                benefit
            ),

            "net_benefit": (
                net_benefit
            ),

            "roi": roi
        }

    # ==================================================
    # HELPER - DECIMAL
    # ==================================================

    @staticmethod
    def _to_decimal(
        value
    ):

        if value in (
            None,
            "",
        ):

            return Decimal("0")

        try:

            return Decimal(
                str(value)
            )

        except (
            InvalidOperation,
            ValueError
        ):

            raise ValueError(
                "Invalid monetary value."
            )

    # ==================================================
    # HELPER - INTEGER
    # ==================================================

    @staticmethod
    def _to_integer(
        value
    ):

        if value in (
            None,
            "",
        ):

            return 0

        try:

            return int(value)

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Invalid time saving value."
            )


    # ==================================================
    # GET IMPROVEMENT PIC
    # ==================================================

    def get_pics(
        self,
        improvement_id,
    ):
        """
        Get active PICs assigned to an Improvement.
        """

        return (
            self.improvement_pic_repository
            .find_by_improvement_id(
                improvement_id
            )
        )