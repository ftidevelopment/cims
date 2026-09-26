from celery_app import celery

from app.repositories.problem_repository import ProblemRepository
from app.services.notification_service import NotificationService
from app.core.notification_events import NotificationEvent
from app.repositories.improvement_repository import ImprovementRepository
from app.repositories.kaizen_repository import (
    KaizenRepository
)
from app.repositories.kaizen_award_period_repository import (
    KaizenAwardPeriodRepository
)

from app.repositories.kaizen_award_score_repository import (
    KaizenAwardScoreRepository
)
from app.repositories.issue_clarification_repository import (
    IssueClarificationRepository,
)

@celery.task
def test_celery_task():

    print(
        "CIMS Celery test task executed successfully."
    )

    return "CIMS Celery is working."


# ==========================================
# Problem Created Notification
# ==========================================

@celery.task
def send_problem_created_notification(
    problem_id,
):
    """
    Send Problem Created notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Repository
        # ==========================================

        problem_repository = ProblemRepository()

        # ==========================================
        # Reload Problem
        # ==========================================

        problem = problem_repository.get_by_id(
            problem_id
        )

        if not problem:

            print(
                "PROBLEM CREATED CELERY NOTIFICATION: "
                "Problem not found:",
                problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        notification_service.problem_created(
            problem=problem,
        )

        print(
            "PROBLEM CREATED CELERY NOTIFICATION: "
            "SUCCESS -",
            problem.problem_no,
        )

        return True

    except Exception as ex:

        print(
            "PROBLEM CREATED CELERY "
            "NOTIFICATION ERROR:",
            str(ex),
        )

        raise

# ==========================================
# Problem Updated Notification
# ==========================================

@celery.task
def send_problem_updated_notification(
    problem_id,
):
    """
    Send Problem Updated notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Repository
        # ==========================================

        problem_repository = ProblemRepository()

        # ==========================================
        # Reload Problem
        # ==========================================

        problem = problem_repository.get_by_id(
            problem_id
        )

        if not problem:

            print(
                "PROBLEM UPDATED CELERY NOTIFICATION: "
                "Problem not found:",
                problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        notification_service.problem_updated(
            problem=problem,
        )

        print(
            "PROBLEM UPDATED CELERY NOTIFICATION: "
            "SUCCESS -",
            problem.problem_no,
        )

        return True

    except Exception as ex:

        print(
            "PROBLEM UPDATED CELERY "
            "NOTIFICATION ERROR:",
            str(ex),
        )

        raise

# ==========================================
# Problem Assigned Notification
# ==========================================

@celery.task
def send_problem_assigned_notification(
    problem_id,
):
    """
    Send Problem Assigned notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Get Problem
        # ==========================================

        problem_repository = ProblemRepository()

        problem = problem_repository.get_by_id(
            problem_id
        )

        if not problem:

            print(
                "PROBLEM ASSIGNED CELERY NOTIFICATION: "
                "Problem not found:",
                problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        # ==========================================
        # Prepare Additional Employees
        # ==========================================
        #
        # Reporter + seluruh PIC
        #
        # NotificationService akan melakukan
        # deduplication dengan Notification Rules.
        #
        # Reporter dan PIC mendapatkan:
        #
        # EMAIL = ON
        # LINE  = ON
        #
        # ==========================================

        additional_employees = []

        # ------------------------------------------
        # Reporter
        # ------------------------------------------

        if problem.reporter:

            additional_employees.append(
                problem.reporter
            )

        # ------------------------------------------
        # All Problem PIC
        # ------------------------------------------

        for problem_pic in problem.problem_pics:

            employee = problem_pic.employee

            if not employee:
                continue

            if employee.id not in [
                item.id
                for item in additional_employees
            ]:

                additional_employees.append(
                    employee
                )

        # ==========================================
        # Email Subject
        # ==========================================

        subject = (
            f"[CIMS] Problem Assigned - "
            f"{problem.problem_no}"
        )

        # ==========================================
        # Render Email
        # ==========================================

        body = (
            notification_service
            .render_email_template(
                "emails/problem/assigned.html",
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ==========================================
        # Send Notification
        # ==========================================

        result = notification_service.notify(

            module=NotificationEvent.PROBLEM,

            event=(
                NotificationEvent.PROBLEM_ASSIGNED
            ),

            department_id=(
                problem.department_id
            ),

            subject=subject,

            body=body,

            html=True,

            additional_employees=(
                additional_employees
            ),

            line_context={
                "problem": problem,
            },
        )

        # ==========================================
        # Result
        # ==========================================

        print(
            "=========================================="
        )

        print(
            "PROBLEM ASSIGNED CELERY NOTIFICATION"
        )

        print(
            "Problem No:",
            problem.problem_no
        )

        print(
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ]
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "PROBLEM ASSIGNED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise


# ==========================================
# Improvement Created Notification
# ==========================================

@celery.task
def send_improvement_created_notification(
    improvement_id,
):
    """
    Send Improvement Created notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Get Improvement
        # ==========================================

        improvement_repository = (
            ImprovementRepository()
        )

        improvement = (
            improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            print(
                "IMPROVEMENT CREATED CELERY "
                "NOTIFICATION: Improvement not found:",
                improvement_id,
            )

            return False

        # ==========================================
        # Get Related Problem
        # ==========================================

        problem_repository = (
            ProblemRepository()
        )

        problem = (
            problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            print(
                "IMPROVEMENT CREATED CELERY "
                "NOTIFICATION: Related Problem not found:",
                improvement.problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        # ==========================================
        # Prepare Additional Employees
        # ==========================================
        #
        # Improvement Owner
        # +
        # Active Improvement PIC
        #
        # NotificationService akan melakukan
        # deduplication dengan Notification Rules.
        #
        # ==========================================

        additional_employees = []

        # ------------------------------------------
        # Improvement Owner
        # ------------------------------------------

        if improvement.owner_employee:

            additional_employees.append(
                improvement.owner_employee
            )

        # ------------------------------------------
        # Improvement PIC
        # ------------------------------------------

        for pic in improvement.improvement_pics:

            if not pic.is_active:
                continue

            if not pic.employee:
                continue

            if pic.employee.id not in [
                employee.id
                for employee in additional_employees
            ]:

                additional_employees.append(
                    pic.employee
                )

        # ==========================================
        # Email Subject
        # ==========================================

        subject = (
            f"[CIMS] New Improvement Created - "
            f"{improvement.improvement_no}"
        )

        # ==========================================
        # Render Email
        # ==========================================

        body = (
            notification_service
            .render_email_template(
                "emails/improvement/created.html",
                improvement=improvement,
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ==========================================
        # Send Notification
        # ==========================================

        result = (
            notification_service.notify(

                module=NotificationEvent.IMPROVEMENT,

                event=(
                    NotificationEvent
                    .IMPROVEMENT_CREATED
                ),

                department_id=(
                    problem.department_id
                ),

                subject=subject,

                body=body,

                html=True,

                additional_employees=(
                    additional_employees
                ),

                line_context={
                    "improvement": improvement,
                    "problem": problem,
                },
            )
        )

        # ==========================================
        # Result
        # ==========================================

        print(
            "=========================================="
        )

        print(
            "IMPROVEMENT CREATED CELERY NOTIFICATION"
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
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ]
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "IMPROVEMENT CREATED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

# ==========================================
# Improvement Updated Notification
# ==========================================

@celery.task
def send_improvement_updated_notification(
    improvement_id,
):
    """
    Send Improvement Updated notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Get Improvement
        # ==========================================

        improvement_repository = (
            ImprovementRepository()
        )

        improvement = (
            improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            print(
                "IMPROVEMENT UPDATED CELERY "
                "NOTIFICATION: Improvement not found:",
                improvement_id,
            )

            return False

        # ==========================================
        # Get Related Problem
        # ==========================================

        problem_repository = (
            ProblemRepository()
        )

        problem = (
            problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            print(
                "IMPROVEMENT UPDATED CELERY "
                "NOTIFICATION: Related Problem not found:",
                improvement.problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        # ==========================================
        # Prepare Additional Employees
        # ==========================================

        additional_employees = []

        # ------------------------------------------
        # Improvement Owner
        # ------------------------------------------

        if improvement.owner_employee:

            additional_employees.append(
                improvement.owner_employee
            )

        # ------------------------------------------
        # Improvement PIC
        # ------------------------------------------

        for pic in improvement.improvement_pics:

            if not pic.is_active:
                continue

            if not pic.employee:
                continue

            if pic.employee.id not in [
                employee.id
                for employee in additional_employees
            ]:

                additional_employees.append(
                    pic.employee
                )

        # ==========================================
        # Email Subject
        # ==========================================

        subject = (
            f"[CIMS] Improvement Updated - "
            f"{improvement.improvement_no}"
        )

        # ==========================================
        # Render Email
        # ==========================================

        body = (
            notification_service
            .render_email_template(
                "emails/improvement/updated.html",
                improvement=improvement,
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ==========================================
        # Send Notification
        # ==========================================

        result = (
            notification_service.notify(

                module=NotificationEvent.IMPROVEMENT,

                event=(
                    NotificationEvent
                    .IMPROVEMENT_UPDATED
                ),

                department_id=(
                    problem.department_id
                ),

                subject=subject,

                body=body,

                html=True,

                additional_employees=(
                    additional_employees
                ),

                line_context={
                    "improvement": improvement,
                    "problem": problem,
                },
            )
        )

        # ==========================================
        # Result
        # ==========================================

        print(
            "=========================================="
        )

        print(
            "IMPROVEMENT UPDATED CELERY NOTIFICATION"
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
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ]
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "IMPROVEMENT UPDATED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

# ==========================================
# Improvement Implemented Notification
# ==========================================

@celery.task
def send_improvement_implemented_notification(
    improvement_id,
):
    """
    Send Improvement Implemented notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Get Improvement
        # ==========================================

        improvement_repository = (
            ImprovementRepository()
        )

        improvement = (
            improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            print(
                "IMPROVEMENT IMPLEMENTED CELERY "
                "NOTIFICATION: Improvement not found:",
                improvement_id,
            )

            return False

        # ==========================================
        # Get Related Problem
        # ==========================================

        problem_repository = (
            ProblemRepository()
        )

        problem = (
            problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            print(
                "IMPROVEMENT IMPLEMENTED CELERY "
                "NOTIFICATION: Related Problem not found:",
                improvement.problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        # ==========================================
        # Prepare Additional Employees
        # ==========================================

        additional_employees = []

        # ------------------------------------------
        # Improvement Owner
        # ------------------------------------------

        if improvement.owner_employee:

            additional_employees.append(
                improvement.owner_employee
            )

        # ------------------------------------------
        # Improvement PIC
        # ------------------------------------------

        for pic in improvement.improvement_pics:

            if not pic.is_active:
                continue

            if not pic.employee:
                continue

            if pic.employee.id not in [
                employee.id
                for employee in additional_employees
            ]:

                additional_employees.append(
                    pic.employee
                )

        # ==========================================
        # Email Subject
        # ==========================================

        subject = (
            f"[CIMS] Improvement Implemented - "
            f"{improvement.improvement_no}"
        )

        # ==========================================
        # Render Email
        # ==========================================

        body = (
            notification_service
            .render_email_template(
                "emails/improvement/implemented.html",
                improvement=improvement,
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ==========================================
        # Send Notification
        # ==========================================

        result = (
            notification_service.notify(

                module=NotificationEvent.IMPROVEMENT,

                event=(
                    NotificationEvent
                    .IMPROVEMENT_IMPLEMENTED
                ),

                department_id=(
                    problem.department_id
                ),

                subject=subject,

                body=body,

                html=True,

                additional_employees=(
                    additional_employees
                ),

                line_context={
                    "improvement": improvement,
                    "problem": problem,
                },
            )
        )

        # ==========================================
        # Result
        # ==========================================

        print(
            "=========================================="
        )

        print(
            "IMPROVEMENT IMPLEMENTED "
            "CELERY NOTIFICATION"
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
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ]
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "IMPROVEMENT IMPLEMENTED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise


# ==========================================
# Improvement Verified Notification
# ==========================================

@celery.task
def send_improvement_verified_notification(
    improvement_id,
):
    """
    Send Improvement Verified notification
    through Celery Worker.
    """

    try:

        # ==========================================
        # Get Improvement
        # ==========================================

        improvement_repository = (
            ImprovementRepository()
        )

        improvement = (
            improvement_repository
            .get_by_id(
                improvement_id
            )
        )

        if not improvement:

            print(
                "IMPROVEMENT VERIFIED CELERY "
                "NOTIFICATION: Improvement not found:",
                improvement_id,
            )

            return False

        # ==========================================
        # Get Related Problem
        # ==========================================

        problem_repository = (
            ProblemRepository()
        )

        problem = (
            problem_repository
            .get_by_id(
                improvement.problem_id
            )
        )

        if not problem:

            print(
                "IMPROVEMENT VERIFIED CELERY "
                "NOTIFICATION: Related Problem not found:",
                improvement.problem_id,
            )

            return False

        # ==========================================
        # Notification Service
        # ==========================================

        notification_service = (
            NotificationService()
        )

        # ==========================================
        # Prepare Additional Employees
        # ==========================================

        additional_employees = []

        # ------------------------------------------
        # Improvement Owner
        # ------------------------------------------

        if improvement.owner_employee:

            additional_employees.append(
                improvement.owner_employee
            )

        # ------------------------------------------
        # Improvement PIC
        # ------------------------------------------

        for pic in improvement.improvement_pics:

            if not pic.is_active:
                continue

            if not pic.employee:
                continue

            if pic.employee.id not in [
                employee.id
                for employee in additional_employees
            ]:

                additional_employees.append(
                    pic.employee
                )

        # ==========================================
        # Email Subject
        # ==========================================

        subject = (
            f"[CIMS] Improvement Verified - "
            f"{improvement.improvement_no}"
        )

        # ==========================================
        # Render Email
        # ==========================================

        body = (
            notification_service
            .render_email_template(
                "emails/improvement/verified.html",
                improvement=improvement,
                problem=problem,
                cims_url="http://localhost:5000",
            )
        )

        # ==========================================
        # Send Notification
        # ==========================================

        result = (
            notification_service.notify(

                module=NotificationEvent.IMPROVEMENT,

                event=(
                    NotificationEvent
                    .IMPROVEMENT_VERIFIED
                ),

                department_id=(
                    problem.department_id
                ),

                subject=subject,

                body=body,

                html=True,

                additional_employees=(
                    additional_employees
                ),

                line_context={
                    "improvement": improvement,
                    "problem": problem,
                },
            )
        )

        # ==========================================
        # Result
        # ==========================================

        print(
            "=========================================="
        )

        print(
            "IMPROVEMENT VERIFIED "
            "CELERY NOTIFICATION"
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
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ]
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "IMPROVEMENT VERIFIED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

@celery.task
def send_improvement_approved_notification(improvement_id):
    try:
        improvement_repository = ImprovementRepository()

        improvement = improvement_repository.get_by_id(improvement_id)

        if not improvement:
            print(
                "IMPROVEMENT APPROVED CELERY NOTIFICATION: "
                "Improvement not found:",
                improvement_id,
            )
            return False

        # Get related Problem
        problem_repository = ProblemRepository()

        problem = problem_repository.get_by_id(
            improvement.problem_id
        )

        if not problem:
            print(
                "IMPROVEMENT APPROVED CELERY NOTIFICATION: "
                "Related Problem not found:",
                improvement.problem_id,
            )
            return False

        notification_service = NotificationService()

        # -------------------------------------------------
        # Prepare additional employees
        # -------------------------------------------------

        additional_employees = []

        # Improvement Owner
        if improvement.owner_employee:
            additional_employees.append(
                improvement.owner_employee
            )

        # Improvement PIC
        for pic in improvement.improvement_pics:

            if not pic.is_active:
                continue

            if not pic.employee:
                continue

            # Avoid duplicate employee
            if pic.employee.id not in [
                employee.id
                for employee in additional_employees
            ]:
                additional_employees.append(
                    pic.employee
                )

        # -------------------------------------------------
        # Email
        # -------------------------------------------------

        subject = (
            f"[CIMS] Improvement Approved - "
            f"{improvement.improvement_no}"
        )

        body = notification_service.render_email_template(
            "emails/improvement/approved.html",
            improvement=improvement,
            problem=problem,
            cims_url="http://localhost:5000",
        )

        # -------------------------------------------------
        # Send Notification
        # -------------------------------------------------

        result = notification_service.notify(
            module=NotificationEvent.IMPROVEMENT,
            event=NotificationEvent.IMPROVEMENT_APPROVED,
            department_id=problem.department_id,
            subject=subject,
            body=body,
            html=True,
            additional_employees=additional_employees,
            line_context={
                "improvement": improvement,
                "problem": problem,
            },
        )

        # -------------------------------------------------
        # Debug Information
        # -------------------------------------------------

        print("==========================================")
        print(
            "IMPROVEMENT APPROVED CELERY NOTIFICATION"
        )
        print("Improvement ID:", improvement.id)
        print("Improvement No:", improvement.improvement_no)
        print(
            "Approved By:",
            improvement.approved_by_employee_id,
        )
        print(
            "Additional Employees:",
            [
                employee.id
                for employee in additional_employees
            ],
        )
        print("Notification Result:", result)
        print("==========================================")

        return result

    except Exception as ex:

        print(
            "IMPROVEMENT APPROVED CELERY "
            "NOTIFICATION ERROR:",
            str(ex),
        )

        raise

@celery.task
def send_kaizen_submitted_notification(kaizen_id):

    try:

        # ==================================================
        # Get Kaizen
        # ==================================================

        from app.repositories.kaizen_repository import (
            KaizenRepository
        )

        kaizen_repository = KaizenRepository()

        kaizen = (
            kaizen_repository
            .get_by_id(kaizen_id)
        )

        if not kaizen:

            print(
                "KAIZEN SUBMITTED CELERY NOTIFICATION: "
                "Kaizen not found:",
                kaizen_id
            )

            return False

        # ==================================================
        # Notification Service
        # ==================================================

        notification_service = NotificationService()

        # ==================================================
        # Subject
        # ==================================================

        subject = (
            f"[CIMS] Kaizen Submitted - "
            f"{kaizen.kaizen_no}"
        )

        # ==================================================
        # Email Body
        # ==================================================

        body = (
            notification_service
            .render_email_template(
                "emails/kaizen/submitted.html",
                kaizen=kaizen,
                cims_url="http://localhost:5000",
            )
        )

        # ==================================================
        # Business Recipient
        #
        # Kaizen Owner / Creator
        # ==================================================

        additional_employees = []

        if kaizen.employee:

            additional_employees.append(
                kaizen.employee
            )

        # ==================================================
        # Send Notification
        # ==================================================

        result = notification_service.notify(

            module=NotificationEvent.KAIZEN,

            event=(
                NotificationEvent
                .KAIZEN_SUBMITTED
            ),

            department_id=(
                kaizen.department_id
            ),

            subject=subject,

            body=body,

            html=True,

            additional_employees=(
                additional_employees
            ),

            line_context={
                "kaizen": kaizen,
            },
        )

        # ==================================================
        # Debug Information
        # ==================================================

        print(
            "=========================================="
        )

        print(
            "KAIZEN SUBMITTED CELERY NOTIFICATION"
        )

        print(
            "Kaizen ID:",
            kaizen.id
        )

        print(
            "Kaizen No:",
            kaizen.kaizen_no
        )

        print(
            "Employee:",
            kaizen.employee_id
        )

        print(
            "Department:",
            kaizen.department_id
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "KAIZEN SUBMITTED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

# ==========================================================
# KAIZEN APPROVED NOTIFICATION
# ==========================================================

@celery.task
def send_kaizen_approved_notification(kaizen_id):

    try:

        # ==================================================
        # Get Kaizen
        # ==================================================

        kaizen_repository = KaizenRepository()

        kaizen = kaizen_repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            print(
                "KAIZEN APPROVED CELERY NOTIFICATION: "
                "Kaizen not found:",
                kaizen_id
            )

            return False

        # ==================================================
        # Notification Service
        # ==================================================

        notification_service = NotificationService()

        # ==================================================
        # Subject
        # ==================================================

        subject = (
            f"[CIMS] Kaizen Approved - "
            f"{kaizen.kaizen_no}"
        )

        # ==================================================
        # Email Body
        # ==================================================

        body = notification_service.render_email_template(

            "emails/kaizen/approved.html",

            kaizen=kaizen,

            cims_url="http://localhost:5000",
        )

        # ==================================================
        # Additional Employees
        # ==================================================
        #
        # Kaizen creator receives notification.
        # ==================================================

        additional_employees = []

        if kaizen.employee:

            additional_employees.append(
                kaizen.employee
            )

        # ==================================================
        # Send Notification
        # ==================================================

        result = notification_service.notify(

            module=NotificationEvent.KAIZEN,

            event=NotificationEvent.KAIZEN_APPROVED,

            department_id=kaizen.department_id,

            subject=subject,

            body=body,

            html=True,

            additional_employees=additional_employees,

            line_context={
                "kaizen": kaizen
            },
        )

        # ==================================================
        # Log
        # ==================================================

        print(
            "=========================================="
        )

        print(
            "KAIZEN APPROVED CELERY NOTIFICATION"
        )

        print(
            "Kaizen ID:",
            kaizen.id
        )

        print(
            "Kaizen No:",
            kaizen.kaizen_no
        )

        print(
            "Employee:",
            kaizen.employee_id
        )

        print(
            "Department:",
            kaizen.department_id
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "KAIZEN APPROVED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

# ==========================================================
# KAIZEN REJECTED NOTIFICATION
# ==========================================================

@celery.task
def send_kaizen_rejected_notification(kaizen_id):

    try:

        # ==================================================
        # Get Kaizen
        # ==================================================

        kaizen_repository = KaizenRepository()

        kaizen = kaizen_repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            print(
                "KAIZEN REJECTED CELERY NOTIFICATION: "
                "Kaizen not found:",
                kaizen_id
            )

            return False

        # ==================================================
        # Notification Service
        # ==================================================

        notification_service = NotificationService()

        # ==================================================
        # Subject
        # ==================================================

        subject = (
            f"[CIMS] Kaizen Rejected - "
            f"{kaizen.kaizen_no}"
        )

        # ==================================================
        # Email Body
        # ==================================================

        body = notification_service.render_email_template(

            "emails/kaizen/rejected.html",

            kaizen=kaizen,

            cims_url="http://localhost:5000",
        )

        # ==================================================
        # Additional Employees
        # ==================================================
        #
        # Kaizen creator receives notification.
        # ==================================================

        additional_employees = []

        if kaizen.employee:

            additional_employees.append(
                kaizen.employee
            )

        # ==================================================
        # Send Notification
        # ==================================================

        result = notification_service.notify(

            module=NotificationEvent.KAIZEN,

            event=NotificationEvent.KAIZEN_REJECTED,

            department_id=kaizen.department_id,

            subject=subject,

            body=body,

            html=True,

            additional_employees=additional_employees,

            line_context={
                "kaizen": kaizen
            },
        )

        # ==================================================
        # Log
        # ==================================================

        print(
            "=========================================="
        )

        print(
            "KAIZEN REJECTED CELERY NOTIFICATION"
        )

        print(
            "Kaizen ID:",
            kaizen.id
        )

        print(
            "Kaizen No:",
            kaizen.kaizen_no
        )

        print(
            "Employee:",
            kaizen.employee_id
        )

        print(
            "Department:",
            kaizen.department_id
        )

        print(
            "Rejected By:",
            kaizen.rejected_by_employee_id
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "KAIZEN REJECTED CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise


# ==========================================================
# KAIZEN AWARD NOTIFICATION
# ==========================================================

@celery.task
def send_kaizen_award_notification(award_period_id):

    try:

        # ==================================================
        # GET AWARD PERIOD
        # ==================================================

        award_period_repository = (
            KaizenAwardPeriodRepository()
        )

        award_period = (
            award_period_repository.get_by_id(
                award_period_id
            )
        )

        if not award_period:

            print(
                "KAIZEN AWARD CELERY NOTIFICATION: "
                "Award period not found:",
                award_period_id
            )

            return False

        # ==================================================
        # CHECK STATUS
        # ==================================================

        if award_period.status != "Closed":

            print(
                "KAIZEN AWARD CELERY NOTIFICATION: "
                "Award period is not closed:",
                award_period.award_code
            )

            return False

        # ==================================================
        # GET TOP 5 KAIZEN
        # ==================================================

        kaizen_award_score_repository = (
            KaizenAwardScoreRepository()
        )

        top_5_result = (
            kaizen_award_score_repository
            .get_summary_by_award_period(
                award_period_id=award_period.id,
                start_date=award_period.start_date,
                end_date=award_period.end_date,
                page=1,
                per_page=5,
            )
        )

        top_5 = top_5_result.items

        # ==================================================
        # NOTIFICATION SERVICE
        # ==================================================

        notification_service = (
            NotificationService()
        )

        # ==================================================
        # SUBJECT
        # ==================================================

        subject = (
            f"[CIMS] Kaizen Award Result - "
            f"{award_period.award_name}"
        )

        # ==================================================
        # EMAIL BODY
        # ==================================================

        body = (
            notification_service
            .render_email_template(
                "emails/kaizen/awarded.html",
                award_period=award_period,
                top_5=top_5,
                cims_url=(
                    "http://localhost:5000"
                ),
            )
        )

        # ==================================================
        # SEND TO ALL ACTIVE EMPLOYEES
        # ==================================================

        result = (
            notification_service
            .notify_all_employees(
                event=NotificationEvent.KAIZEN_AWARDED,
                subject=subject,
                body=body,
                html=True,
                line_context={
                    "award_period": award_period,
                    "top_5": top_5,
                },
            )
        )

        # ==================================================
        # LOG
        # ==================================================

        print(
            "=========================================="
        )

        print(
            "KAIZEN AWARD CELERY NOTIFICATION"
        )

        print(
            "Award Period ID:",
            award_period.id
        )

        print(
            "Award Code:",
            award_period.award_code
        )

        print(
            "Award Name:",
            award_period.award_name
        )

        print(
            "Top 5 Count:",
            len(top_5)
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "KAIZEN AWARD CELERY "
            "NOTIFICATION ERROR:",
            str(ex)
        )

        raise

@celery.task
def send_issue_clarification_requested_notification(
    clarification_id,
):
    """
    Send Issue Clarification Requested notification
    through Celery Worker.
    """

    try:

        clarification_repository = (
            IssueClarificationRepository()
        )

        clarification = (
            clarification_repository.get_by_id(
                clarification_id
            )
        )

        if not clarification:

            print(
                "ISSUE CLARIFICATION REQUESTED "
                "CELERY NOTIFICATION: "
                "Clarification not found:",
                clarification_id,
            )

            return False

        notification_service = NotificationService()

        result = (
            notification_service
            .issue_clarification_requested(
                clarification
            )
        )

        print(
            "=========================================="
        )

        print(
            "ISSUE CLARIFICATION REQUESTED "
            "CELERY NOTIFICATION"
        )

        print(
            "Clarification ID:",
            clarification.id
        )

        print(
            "Issue No:",
            clarification.issue.issue_no
            if clarification.issue
            else None
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "ISSUE CLARIFICATION REQUESTED "
            "CELERY NOTIFICATION ERROR:",
            str(ex),
        )

        raise

@celery.task
def send_issue_clarification_responded_notification(
    clarification_id,
):
    """
    Send Issue Clarification Responded notification
    through Celery Worker.
    """

    try:

        clarification_repository = (
            IssueClarificationRepository()
        )

        clarification = (
            clarification_repository.get_by_id(
                clarification_id
            )
        )

        if not clarification:

            print(
                "ISSUE CLARIFICATION RESPONDED "
                "CELERY NOTIFICATION: "
                "Clarification not found:",
                clarification_id,
            )

            return False

        notification_service = NotificationService()

        result = (
            notification_service
            .issue_clarification_responded(
                clarification
            )
        )

        print(
            "=========================================="
        )

        print(
            "ISSUE CLARIFICATION RESPONDED "
            "CELERY NOTIFICATION"
        )

        print(
            "Clarification ID:",
            clarification.id
        )

        print(
            "Issue No:",
            clarification.issue.issue_no
            if clarification.issue
            else None
        )

        print(
            "Notification Result:",
            result
        )

        print(
            "=========================================="
        )

        return result

    except Exception as ex:

        print(
            "ISSUE CLARIFICATION RESPONDED "
            "CELERY NOTIFICATION ERROR:",
            str(ex),
        )

        raise