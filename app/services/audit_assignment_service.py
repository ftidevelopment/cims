from app.models.audit_assignment import AuditAssignment

from app.repositories.audit_assignment_repository import (
    AuditAssignmentRepository,
)
from app.repositories.audit_repository import AuditRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository

from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult


class AuditAssignmentService:
    """
    Service untuk mengelola assignment Auditor, Department,
    dan Location pada sebuah Audit.

    Business Rule:
    - Satu Audit dapat memiliki banyak Department.
    - Satu Department dapat memiliki banyak Location.
    - Satu Audit dapat memiliki banyak Auditor.
    - Satu Location dapat memiliki banyak Auditor.
    - Satu Auditor dapat ditugaskan ke banyak Location.
    - Kombinasi Audit + Auditor + Location harus unik.
    """

    def __init__(self):
        self.repository = AuditAssignmentRepository()
        self.audit_repository = AuditRepository()
        self.department_repository = DepartmentRepository()
        self.employee_repository = EmployeeRepository()
        self.transaction = TransactionManager()

    # ==========================================================
    # GET
    # ==========================================================

    def get_by_id(self, assignment_id):
        return self.repository.get_by_id(assignment_id)

    def get_by_audit(self, audit_id):
        return self.repository.get_by_audit(audit_id)

    def get_by_auditor(self, auditor_employee_id):
        return self.repository.get_by_auditor(
            auditor_employee_id
        )

    def get_by_location(self, audit_id, location):
        return self.repository.get_by_location(
            audit_id,
            location,
        )

    def get_auditors_by_location(
        self,
        audit_id,
        location,
    ):
        return self.repository.get_auditors_by_location(
            audit_id,
            location,
        )

    def get_locations_by_auditor(
        self,
        audit_id,
        auditor_employee_id,
    ):
        return self.repository.get_locations_by_auditor(
            audit_id,
            auditor_employee_id,
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        audit_id,
        department_id,
        auditor_employee_id,
        location,
    ):
        """
        Create one auditor-department-location assignment.
        """

        # ------------------------------------------------------
        # Validate Audit
        # ------------------------------------------------------

        audit = self.audit_repository.get_by_id(
            audit_id
        )

        if not audit:
            raise ValueError(
                "Audit not found."
            )

        # ------------------------------------------------------
        # Validate Department
        # ------------------------------------------------------

        department = self.department_repository.get_by_id(
            department_id
        )

        if not department:
            raise ValueError(
                "Department not found."
            )

        if not department.is_active:
            raise ValueError(
                "Selected department is inactive."
            )

        # ------------------------------------------------------
        # Validate Auditor
        # ------------------------------------------------------

        auditor = self.employee_repository.get_by_id(
            auditor_employee_id
        )

        if not auditor:
            raise ValueError(
                "Auditor not found."
            )

        if not auditor.is_active:
            raise ValueError(
                "Selected auditor is inactive."
            )

        # ------------------------------------------------------
        # Validate Location
        # ------------------------------------------------------

        location = (location or "").strip()

        if not location:
            raise ValueError(
                "Location is required."
            )

        # ------------------------------------------------------
        # Check Duplicate
        # ------------------------------------------------------

        if self.repository.exists_assignment(
            audit_id=audit_id,
            auditor_employee_id=auditor_employee_id,
            location=location,
        ):
            raise ValueError(
                "This auditor is already assigned "
                "to this location for the selected audit."
            )

        # ------------------------------------------------------
        # Create Assignment
        # ------------------------------------------------------

        assignment = AuditAssignment(
            audit_id=audit_id,
            department_id=department_id,
            auditor_employee_id=auditor_employee_id,
            location=location,
        )

        self.repository.create(
            assignment
        )

        self.transaction.commit()

        return assignment

    # ==========================================================
    # CREATE MULTIPLE AUDITORS
    # ==========================================================

    def create_multiple(
        self,
        audit_id,
        department_id,
        auditor_employee_ids,
        location,
    ):
        """
        Assign multiple auditors to one location.

        Example:

        Audit:
            AUD20260001

        Department:
            Production

        Location:
            Production Line A

        Auditors:
            Employee 1001
            Employee 1002
            Employee 1003
        """

        # ------------------------------------------------------
        # Validate Audit
        # ------------------------------------------------------

        audit = self.audit_repository.get_by_id(
            audit_id
        )

        if not audit:
            raise ValueError(
                "Audit not found."
            )

        # ------------------------------------------------------
        # Validate Department
        # ------------------------------------------------------

        department = self.department_repository.get_by_id(
            department_id
        )

        if not department:
            raise ValueError(
                "Department not found."
            )

        if not department.is_active:
            raise ValueError(
                "Selected department is inactive."
            )

        # ------------------------------------------------------
        # Validate Location
        # ------------------------------------------------------

        location = (location or "").strip()

        if not location:
            raise ValueError(
                "Location is required."
            )

        # ------------------------------------------------------
        # Validate Auditor List
        # ------------------------------------------------------

        if not auditor_employee_ids:
            raise ValueError(
                "At least one auditor is required."
            )

        created_assignments = []

        # ------------------------------------------------------
        # Process Each Auditor
        # ------------------------------------------------------

        for auditor_employee_id in auditor_employee_ids:

            auditor = self.employee_repository.get_by_id(
                auditor_employee_id
            )

            if not auditor:
                raise ValueError(
                    f"Auditor with ID "
                    f"{auditor_employee_id} not found."
                )

            if not auditor.is_active:
                raise ValueError(
                    f"Auditor "
                    f"{auditor_employee_id} is inactive."
                )

            # --------------------------------------------------
            # Check Duplicate
            # --------------------------------------------------

            if self.repository.exists_assignment(
                audit_id=audit_id,
                auditor_employee_id=auditor_employee_id,
                location=location,
            ):
                continue

            # --------------------------------------------------
            # Create Assignment
            # --------------------------------------------------

            assignment = AuditAssignment(
                audit_id=audit_id,
                department_id=department_id,
                auditor_employee_id=auditor_employee_id,
                location=location,
            )

            self.repository.create(
                assignment
            )

            created_assignments.append(
                assignment
            )

        # ------------------------------------------------------
        # Commit Once
        # ------------------------------------------------------

        if created_assignments:
            self.transaction.commit()

        return created_assignments

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        assignment,
        department_id,
        auditor_employee_id,
        location,
    ):
        """
        Update an existing assignment.
        """

        if not assignment:
            raise ValueError(
                "Audit Assignment not found."
            )

        # ------------------------------------------------------
        # Validate Department
        # ------------------------------------------------------

        department = self.department_repository.get_by_id(
            department_id
        )

        if not department:
            raise ValueError(
                "Department not found."
            )

        if not department.is_active:
            raise ValueError(
                "Selected department is inactive."
            )

        # ------------------------------------------------------
        # Validate Auditor
        # ------------------------------------------------------

        auditor = self.employee_repository.get_by_id(
            auditor_employee_id
        )

        if not auditor:
            raise ValueError(
                "Auditor not found."
            )

        if not auditor.is_active:
            raise ValueError(
                "Selected auditor is inactive."
            )

        # ------------------------------------------------------
        # Validate Location
        # ------------------------------------------------------

        location = (location or "").strip()

        if not location:
            raise ValueError(
                "Location is required."
            )

        # ------------------------------------------------------
        # Check Duplicate
        # ------------------------------------------------------

        existing = self.repository.get_assignment(
            audit_id=assignment.audit_id,
            auditor_employee_id=auditor_employee_id,
            location=location,
        )

        if existing and existing.id != assignment.id:
            raise ValueError(
                "This auditor is already assigned "
                "to this location for the selected audit."
            )

        # ------------------------------------------------------
        # Update
        # ------------------------------------------------------

        assignment.department_id = department_id

        assignment.auditor_employee_id = (
            auditor_employee_id
        )

        assignment.location = location

        self.repository.update(
            assignment
        )

        self.transaction.commit()

        return assignment

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(self, assignment):
        """
        Delete an audit assignment.
        """

        if not assignment:
            raise ValueError(
                "Audit Assignment not found."
            )

        self.repository.delete(
            assignment
        )

        self.transaction.commit()

    # ==========================================================
    # DELETE BY AUDIT
    # ==========================================================

    def delete_by_audit(self, audit_id):
        """
        Delete all assignments belonging to an Audit.
        """

        assignments = self.repository.get_by_audit(
            audit_id
        )

        for assignment in assignments:
            self.repository.delete(
                assignment
            )

        if assignments:
            self.transaction.commit()

        return len(assignments)

    # ==========================================================
    # DELETE BY ID
    # ==========================================================

    def delete_by_id(self, assignment_id):

        assignment = self.repository.get_by_id(
            assignment_id
        )

        if not assignment:
            return ServiceResult(
                success=False,
                message="Audit Assignment not found.",
            )

        self.repository.delete(
            assignment
        )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Audit Assignment deleted successfully.",
        )