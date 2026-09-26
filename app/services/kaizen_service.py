from datetime import datetime

from app.core.transaction_manager import TransactionManager
from app.services.base_service import BaseService

from app.repositories.kaizen_repository import (
    KaizenRepository
)

from app.repositories.improvement_repository import (
    ImprovementRepository
)
from app.repositories.problem_repository import (
    ProblemRepository
)

from app.models.kaizen import Kaizen
from app.core.notification_events import (
    NotificationEvent,
)
from app.services.notification_service import (
    NotificationService,
)

class KaizenService(BaseService):
    """
    Service untuk business logic Kaizen.
    """

    def __init__(self):

        self.repository = KaizenRepository()

        self.improvement_repository = (
            ImprovementRepository()
        )
        self.problem_repository = (
            ProblemRepository()
        )
        self.notification_service = (
            NotificationService()
        )

    # ==========================================================
    # PARSE IMPLEMENTATION DATE
    # ==========================================================

    def _parse_implementation_date(
        self,
        implementation_date,
    ):
        """
        Convert implementation_date into
        Python date object.

        Accept:
        - None
        - date
        - datetime
        - YYYY-MM-DD string
        """

        if not implementation_date:

            return None

        # Already datetime
        if isinstance(
            implementation_date,
            datetime
        ):

            return implementation_date.date()

        # Already date
        if hasattr(
            implementation_date,
            "year"
        ) and hasattr(
            implementation_date,
            "month"
        ) and hasattr(
            implementation_date,
            "day"
        ):

            return implementation_date

        # String
        if isinstance(
            implementation_date,
            str
        ):

            implementation_date = (
                implementation_date.strip()
            )

            if not implementation_date:

                return None

            try:

                return datetime.strptime(
                    implementation_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                raise ValueError(
                    "Invalid implementation date. "
                    "Use YYYY-MM-DD format."
                )

        raise ValueError(
            "Invalid implementation date."
        )

    # ==========================================================
    # GENERATE KAIZEN NUMBER
    # ==========================================================

    def generate_kaizen_no(self):

        last_kaizen = self.repository.get_last_by(
            Kaizen.kaizen_no,
            prefix="KZN-"
        )

        if not last_kaizen:

            next_number = 1

        else:

            try:

                last_number = int(
                    last_kaizen.kaizen_no.replace(
                        "KZN-",
                        ""
                    )
                )

                next_number = last_number + 1

            except ValueError:

                next_number = 1

        return f"KZN-{next_number:05d}"

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        improvement_id,
        title,
        description=None,
        kaizen_category_id=None,
        employee_id=None,
        department_id=None,
        before_condition=None,
        before_value=None,
        before_unit=None,
        loss_before=None,
        after_condition=None,
        after_value=None,
        after_unit=None,
        benefit=None,
        cost_saving=None,
        created_by=None,
        implementation_date=None,
    ):
        """
        Membuat Kaizen berdasarkan Improvement.

        Problem akan otomatis mengikuti Problem
        yang terkait dengan Improvement.
        """

        # ==================================================
        # Get Improvement
        # ==================================================

        improvement = (
            self.improvement_repository
            .get_by_id(improvement_id)
        )

        if not improvement:

            return self.failed(
                "Improvement not found."
            )

        # ==================================================
        # Get Related Problem
        # ==================================================

        problem = improvement.problem

        if not problem:

            return self.failed(
                "Related problem not found."
            )

        # ==================================================
        # Validation
        # ==================================================

        validation = self.validate(

            self.validate_required(
                title,
                "Title"
            ),

            self.validate_required(
                kaizen_category_id,
                "Kaizen Category"
            ),

            self.validate_required(
                employee_id,
                "Employee"
            ),

            self.validate_required(
                department_id,
                "Department"
            ),

            self.validate_positive_number(
                before_value,
                "Before value"
            ),

            self.validate_positive_number(
                after_value,
                "After value"
            ),

            self.validate_positive_number(
                cost_saving,
                "Cost saving"
            )
        )

        if not validation.success:

            return validation

        # ==================================================
        # Generate Kaizen Number
        # ==================================================

        kaizen_no = self.generate_kaizen_no()

        # ==================================================
        # Create Entity
        # ==================================================

        kaizen = Kaizen(

            kaizen_no=kaizen_no,

            title=title.strip(),

            description=(
                description.strip()
                if description
                else None
            ),

            kaizen_category_id=kaizen_category_id,

            # Problem otomatis dari Improvement
            problem_id=problem.id,

            # Improvement yang dipilih
            improvement_id=improvement.id,

            # Employee otomatis dari logged-in user
            employee_id=employee_id,

            # Department Kaizen
            department_id=department_id,

            before_condition=(
                before_condition.strip()
                if before_condition
                else None
            ),

            before_value=before_value,

            before_unit=(
                before_unit.strip()
                if before_unit
                else None
            ),

            loss_before=(
                loss_before.strip()
                if loss_before
                else None
            ),

            after_condition=(
                after_condition.strip()
                if after_condition
                else None
            ),

            after_value=after_value,

            after_unit=(
                after_unit.strip()
                if after_unit
                else None
            ),

            benefit=(
                benefit.strip()
                if benefit
                else None
            ),

            cost_saving=cost_saving,

            created_by=created_by,

            implementation_date=(
                self._parse_implementation_date(
                    implementation_date
                )
            ),
        )

        # ==================================================
        # Save
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.create(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            return self.success(
                "Kaizen created successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        kaizen_id,
        title=None,
        description=None,
        kaizen_category_id=None,
        department_id=None,
        before_condition=None,
        before_value=None,
        before_unit=None,
        loss_before=None,
        after_condition=None,
        after_value=None,
        after_unit=None,
        benefit=None,
        cost_saving=None,
        implementation_date=None,
    ):
        """
        Update data Kaizen.

        Improvement dan Problem tidak diubah dari form.
        Relasi tetap mengikuti Improvement awal.
        """

        # ==================================================
        # Get Kaizen
        # ==================================================

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        # ==================================================
        # Only Draft / Rejected can be edited
        # ==================================================

        if kaizen.status not in (
            "Draft",
            "Rejected",
        ):

            return self.failed(
                "Only Draft or Rejected Kaizen can be edited."
            )

        # ==================================================
        # Validation
        # ==================================================

        validation = self.validate(

            self.validate_required(
                title,
                "Title"
            ),

            self.validate_required(
                kaizen_category_id,
                "Kaizen Category"
            ),

            self.validate_required(
                department_id,
                "Department"
            ),

            self.validate_positive_number(
                before_value,
                "Before value"
            ),

            self.validate_positive_number(
                after_value,
                "After value"
            ),

            self.validate_positive_number(
                cost_saving,
                "Cost saving"
            )
        )

        if not validation.success:

            return validation

        # ==================================================
        # Update Fields
        # ==================================================

        kaizen.title = title.strip()

        kaizen.description = (
            description.strip()
            if description
            else None
        )

        # ==================================================
        # Kaizen Category
        # ==================================================

        kaizen.kaizen_category_id = (
            kaizen_category_id
        )

        # ==================================================
        # Department
        # ==================================================

        kaizen.department_id = department_id

        # ==================================================
        # Before
        # ==================================================

        kaizen.before_condition = (
            before_condition.strip()
            if before_condition
            else None
        )

        kaizen.before_value = before_value

        kaizen.before_unit = (
            before_unit.strip()
            if before_unit
            else None
        )

        kaizen.loss_before = (
            loss_before.strip()
            if loss_before
            else None
        )

        # ==================================================
        # After
        # ==================================================

        kaizen.after_condition = (
            after_condition.strip()
            if after_condition
            else None
        )

        kaizen.after_value = after_value

        kaizen.after_unit = (
            after_unit.strip()
            if after_unit
            else None
        )

        # ==================================================
        # Benefit
        # ==================================================

        kaizen.benefit = (
            benefit.strip()
            if benefit
            else None
        )

        kaizen.cost_saving = cost_saving

        # ==================================================
        # Implementation Date
        # ==================================================

        kaizen.implementation_date = (
            self._parse_implementation_date(
                implementation_date
            )
        )

        # ==================================================
        # Save
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            return self.success(
                "Kaizen updated successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # SUBMIT PROPOSAL
    # ==========================================================

    def submit_proposal(
        self,
        kaizen_id
    ):

        # ==================================================
        # Get Kaizen
        # ==================================================

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        # ==================================================
        # Check Status
        # ==================================================

        if kaizen.status not in (
            "Draft",
            "Rejected",
        ):

            return self.failed(
                "Only Draft or Rejected Kaizen can be submitted."
            )

        # ==================================================
        # Required Validation
        # ==================================================

        validation = self.validate(

            self.validate_required(
                kaizen.title,
                "Kaizen title"
            ),

            self.validate_required(
                kaizen.kaizen_category_id,
                "Kaizen Category"
            ),

            self.validate_required(
                kaizen.employee_id,
                "Creator employee"
            ),

            self.validate_required(
                kaizen.department_id,
                "Department"
            ),
        )

        if not validation.success:

            return validation

        # ==================================================
        # Clear Previous Rejection
        # ==================================================

        kaizen.rejection_reason = None

        kaizen.rejected_by_employee_id = None

        kaizen.rejected_at = None

        # ==================================================
        # Change Status
        # ==================================================

        kaizen.status = "Proposal"

        # ==================================================
        # Save
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            # ==================================================
            # DATABASE COMMIT SUCCESS
            # ==================================================
            #
            # Kaizen sudah berhasil berubah menjadi Proposal.
            #
            # Notification TIDAK dikirim langsung di sini.
            # Notification akan diproses oleh Celery Worker.
            # ==================================================

            try:

                from app.tasks.notification_tasks import (
                    send_kaizen_submitted_notification
                )

                task = (
                    send_kaizen_submitted_notification
                    .delay(
                        kaizen.id
                    )
                )

                print(
                    "=========================================="
                )

                print(
                    "KAIZEN SUBMITTED NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
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
                    "Task ID:",
                    task.id
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                # --------------------------------------------------
                # Celery queue failure
                #
                # Kaizen sudah berhasil disimpan sebagai Proposal.
                # Jangan rollback database hanya karena notification
                # gagal masuk ke queue.
                # --------------------------------------------------

                print(
                    "KAIZEN SUBMITTED CELERY "
                    "NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

            # ==================================================
            # Return Success
            # ==================================================

            return self.success(
                "Kaizen submitted successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )
   
    # ==========================================================
    # APPROVE KAIZEN
    # ==========================================================

    # ==========================================================
    # APPROVE KAIZEN
    # ==========================================================

    def approve(
        self,
        kaizen_id,
        employee_id
    ):

        # ==================================================
        # Get Kaizen
        # ==================================================

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        # ==================================================
        # Check Status
        # ==================================================

        if kaizen.status != "Proposal":

            return self.failed(
                "Only Proposal Kaizen can be approved."
            )

        # ==================================================
        # Validate Approver
        # ==================================================

        validation = self.validate(

            self.validate_required(
                employee_id,
                "Approving employee"
            ),
        )

        if not validation.success:

            return validation

        # ==================================================
        # Update Approval Data
        # ==================================================

        kaizen.status = "Approved"

        kaizen.approved_by_employee_id = employee_id

        kaizen.approved_at = datetime.utcnow()

        # ==================================================
        # Clear Previous Rejection
        # ==================================================

        kaizen.rejection_reason = None

        kaizen.rejected_by_employee_id = None

        kaizen.rejected_at = None

        # ==================================================
        # Save Database
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            # ==================================================
            # DATABASE COMMIT SUCCESS
            # ==================================================
            #
            # Kaizen sudah berhasil menjadi Approved.
            #
            # Notification tidak dikirim langsung.
            # Notification dimasukkan ke Celery Queue.
            # ==================================================

            try:

                from app.tasks.notification_tasks import (
                    send_kaizen_approved_notification
                )

                task = (
                    send_kaizen_approved_notification
                    .delay(
                        kaizen.id
                    )
                )

                print(
                    "=========================================="
                )

                print(
                    "KAIZEN APPROVED NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
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
                    "Approved By:",
                    kaizen.approved_by_employee_id
                )

                print(
                    "Task ID:",
                    task.id
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                print(
                    "KAIZEN APPROVED CELERY "
                    "NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

            # ==================================================
            # Return Success
            # ==================================================

            return self.success(
                "Kaizen approved successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # REJECT
    # ==========================================================

    # ==========================================================
    # REJECT KAIZEN
    # ==========================================================

    def reject(
        self,
        kaizen_id,
        employee_id,
        rejection_reason
    ):

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:
            return self.failed(
                "Kaizen not found."
            )

        if kaizen.status != "Proposal":
            return self.failed(
                "Only Proposal Kaizen can be rejected."
            )

        validation = self.validate(

            self.validate_required(
                employee_id,
                "Rejecting employee"
            ),

            self.validate_required(
                rejection_reason,
                "Rejection reason"
            ),
        )

        if not validation.success:
            return validation

        rejection_reason = rejection_reason.strip()

        if not rejection_reason:
            return self.failed(
                "Rejection reason is required."
            )

        # ==================================================
        # Update Rejection Data
        # ==================================================

        kaizen.status = "Rejected"

        kaizen.rejected_by_employee_id = employee_id

        kaizen.rejected_at = datetime.utcnow()

        kaizen.rejection_reason = rejection_reason

        # ==================================================
        # Clear Previous Approval
        # ==================================================

        kaizen.approved_by_employee_id = None

        kaizen.approved_at = None

        # ==================================================
        # Save Database
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            # ==================================================
            # QUEUE CELERY NOTIFICATION
            # ==================================================

            try:

                from app.tasks.notification_tasks import (
                    send_kaizen_rejected_notification
                )

                task = (
                    send_kaizen_rejected_notification
                    .delay(
                        kaizen.id
                    )
                )

                print(
                    "=========================================="
                )

                print(
                    "KAIZEN REJECTED NOTIFICATION "
                    "SUCCESSFULLY QUEUED"
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
                    "Rejected By:",
                    kaizen.rejected_by_employee_id
                )

                print(
                    "Task ID:",
                    task.id
                )

                print(
                    "=========================================="
                )

            except Exception as ex:

                print(
                    "KAIZEN REJECTED CELERY "
                    "NOTIFICATION QUEUE ERROR:",
                    str(ex)
                )

            return self.success(
                "Kaizen rejected successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )
    # ==========================================================
    # MARK AS IMPLEMENTED
    # ==========================================================

    def mark_implemented(
        self,
        kaizen_id,
        implementation_date=None
    ):
        """
        Mengubah Kaizen Approved menjadi Implemented.
        """

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        if kaizen.status != "Approved":

            return self.failed(
                "Only Approved Kaizen can be implemented."
            )

        kaizen.status = "Implemented"

        kaizen.implementation_date = (
            implementation_date
            or datetime.utcnow().date()
        )

        try:

            with TransactionManager() as transaction:

                self.repository.update(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            return self.success(
                "Kaizen marked as implemented.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # GET BY AWARD PERIOD
    # ==========================================================

    def get_by_award_period(
        self,
        start_date,
        end_date
    ):
        return self.repository.find_by_approved_date_range(
            start_date=start_date,
            end_date=end_date
        )

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        kaizen_id
    ):

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        return self.success(
            data=kaizen
        )

    # ==========================================================
    # GET BY KAIZEN NO
    # ==========================================================

    def get_by_kaizen_no(
        self,
        kaizen_no
    ):

        kaizen = self.repository.find_by_kaizen_no(
            kaizen_no
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        return self.success(
            data=kaizen
        )

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(
        self,
        keyword=None,
        status=None,
        department_id=None,
        date_from=None,
        date_to=None,
        employee_id=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):

        result = self.repository.get_all(

            keyword=keyword,

            status=status,

            department_id=department_id,

            date_from=date_from,

            date_to=date_to,

            employee_id=employee_id,

            is_active=is_active,

            page=page,

            per_page=per_page,

            sort_by=sort_by,

            sort_order=sort_order,
        )

        return self.success(
            data=result
        )

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        kaizen_id
    ):
        """
        Soft delete Kaizen.
        """

        kaizen = self.repository.get_by_id(
            kaizen_id
        )

        if not kaizen:

            return self.failed(
                "Kaizen not found."
            )

        try:

            with TransactionManager() as transaction:

                self.repository.delete(
                    kaizen
                )

                transaction.flush()

            return self.success(
                "Kaizen deleted successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )

    # ==========================================================
    # CREATE FROM PROBLEM
    # ==========================================================

    def create_from_problem(
        self,
        problem_id,
        title,
        description=None,
        kaizen_category_id=None,
        employee_id=None,
        department_id=None,
        before_condition=None,
        before_value=None,
        before_unit=None,
        loss_before=None,
        after_condition=None,
        after_value=None,
        after_unit=None,
        benefit=None,
        cost_saving=None,
        implementation_date=None,
    ):
        """
        Membuat Kaizen berdasarkan Problem.

        Improvement tidak diisi.

        problem_id akan langsung menggunakan
        Problem yang dipilih.
        """

        # ==================================================
        # Get Problem
        # ==================================================

        problem = (
            self.problem_repository
            .get_by_id(problem_id)
        )

        if not problem:

            return self.failed(
                "Problem not found."
            )

        # ==================================================
        # Validation
        # ==================================================

        validation = self.validate(

            self.validate_required(
                title,
                "Title"
            ),

            self.validate_required(
                kaizen_category_id,
                "Kaizen Category"
            ),

            self.validate_required(
                employee_id,
                "Employee"
            ),

            self.validate_required(
                department_id,
                "Department"
            ),

            self.validate_positive_number(
                before_value,
                "Before value"
            ),

            self.validate_positive_number(
                after_value,
                "After value"
            ),

            self.validate_positive_number(
                cost_saving,
                "Cost saving"
            )
        )

        if not validation.success:

            return validation

        # ==================================================
        # Generate Kaizen Number
        # ==================================================

        kaizen_no = self.generate_kaizen_no()

        # ==================================================
        # Create Entity
        # ==================================================

        kaizen = Kaizen(

            kaizen_no=kaizen_no,

            title=(
                title.strip()
                if title
                else None
            ),

            description=(
                description.strip()
                if description
                else None
            ),

            kaizen_category_id=(
                kaizen_category_id
            ),

            # ==============================================
            # Problem yang dipilih
            # ==============================================

            problem_id=problem.id,

            # ==============================================
            # Create from Problem
            # Improvement harus NULL
            # ==============================================

            improvement_id=None,

            employee_id=employee_id,

            department_id=department_id,

            before_condition=(
                before_condition.strip()
                if before_condition
                else None
            ),

            before_value=before_value,

            before_unit=(
                before_unit.strip()
                if before_unit
                else None
            ),

            loss_before=(
                loss_before.strip()
                if loss_before
                else None
            ),

            after_condition=(
                after_condition.strip()
                if after_condition
                else None
            ),

            after_value=after_value,

            after_unit=(
                after_unit.strip()
                if after_unit
                else None
            ),

            benefit=(
                benefit.strip()
                if benefit
                else None
            ),

            cost_saving=cost_saving,

            implementation_date=(
                self._parse_implementation_date(
                    implementation_date
                )
            )
        )

        # ==================================================
        # Save
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.create(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            return self.success(
                "Kaizen created successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )


    # ==========================================================
    # CREATE DIRECTLY
    # ==========================================================

    def create_direct(
        self,
        title,
        description=None,
        kaizen_category_id=None,
        employee_id=None,
        department_id=None,
        before_condition=None,
        before_value=None,
        before_unit=None,
        loss_before=None,
        after_condition=None,
        after_value=None,
        after_unit=None,
        benefit=None,
        cost_saving=None,
        implementation_date=None,
    ):
        """
        Membuat Kaizen secara langsung.

        Tidak menggunakan Improvement
        dan tidak menggunakan Problem.
        """

        # ==================================================
        # Validation
        # ==================================================

        validation = self.validate(

            self.validate_required(
                title,
                "Title"
            ),

            self.validate_required(
                kaizen_category_id,
                "Kaizen Category"
            ),

            self.validate_required(
                employee_id,
                "Employee"
            ),

            self.validate_required(
                department_id,
                "Department"
            ),

            self.validate_positive_number(
                before_value,
                "Before value"
            ),

            self.validate_positive_number(
                after_value,
                "After value"
            ),

            self.validate_positive_number(
                cost_saving,
                "Cost saving"
            )
        )

        if not validation.success:
            return validation

        # ==================================================
        # Generate Kaizen Number
        # ==================================================

        kaizen_no = self.generate_kaizen_no()

        # ==================================================
        # Create Entity
        # ==================================================

        kaizen = Kaizen(

            kaizen_no=kaizen_no,

            title=(
                title.strip()
                if title
                else None
            ),

            description=(
                description.strip()
                if description
                else None
            ),

            kaizen_category_id=(
                kaizen_category_id
            ),

            # ==================================================
            # Direct Creation
            # ==================================================

            problem_id=None,

            improvement_id=None,

            employee_id=employee_id,

            department_id=department_id,

            before_condition=(
                before_condition.strip()
                if before_condition
                else None
            ),

            before_value=before_value,

            before_unit=(
                before_unit.strip()
                if before_unit
                else None
            ),

            loss_before=(
                loss_before.strip()
                if loss_before
                else None
            ),

            after_condition=(
                after_condition.strip()
                if after_condition
                else None
            ),

            after_value=after_value,

            after_unit=(
                after_unit.strip()
                if after_unit
                else None
            ),

            benefit=(
                benefit.strip()
                if benefit
                else None
            ),

            cost_saving=cost_saving,

            implementation_date=(
                self._parse_implementation_date(
                    implementation_date
                )
            )
        )

        # ==================================================
        # Save
        # ==================================================

        try:

            with TransactionManager() as transaction:

                self.repository.create(
                    kaizen
                )

                transaction.flush()

                transaction.refresh(
                    kaizen
                )

            return self.success(
                "Kaizen created successfully.",
                kaizen
            )

        except Exception as exception:

            return self.handle_exception(
                exception
            )