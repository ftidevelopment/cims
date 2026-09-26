from app.repositories.problem_assignment_authority_repository import (
    ProblemAssignmentAuthorityRepository,
)

from app.repositories.improvement_assignment_authority_repository import (
    ImprovementAssignmentAuthorityRepository,
)

from app.repositories.improvement_approval_authority_repository import (
    ImprovementApprovalAuthorityRepository,
)
from app.repositories.improvement_pic_repository import (
    ImprovementPICRepository,
)
from app.repositories.kaizen_approval_authority_repository import (
    KaizenApprovalAuthorityRepository,
)


class AuthorizationService:
    """
    Centralized authorization service.

    Handles:

    - Permission
    - Ownership
    - Problem Assignment Authority
    - Improvement Assignment Authority
    - Improvement Approval Authority
    """

    def __init__(self):

        # ==================================================
        # PROBLEM
        # ==================================================

        self.problem_assignment_authority_repository = (
            ProblemAssignmentAuthorityRepository()
        )

        # ==================================================
        # IMPROVEMENT
        # ==================================================

        self.improvement_assignment_authority_repository = (
            ImprovementAssignmentAuthorityRepository()
        )

        self.improvement_approval_authority_repository = (
            ImprovementApprovalAuthorityRepository()
        )
        self.improvement_pic_repository = (
            ImprovementPICRepository()
        )
        self.kaizen_approval_authority_repository = (
            KaizenApprovalAuthorityRepository()
        )

    # ======================================================
    # COMMON USER VALIDATION
    # ======================================================

    def _is_authenticated(
        self,
        user,
    ):
        """
        Check whether user is authenticated.
        """

        if not user:

            return False

        return bool(
            getattr(
                user,
                "is_authenticated",
                False,
            )
        )

    # ======================================================
    # ADMIN CHECK
    # ======================================================

    def _is_admin(
        self,
        user,
    ):
        """
        Check whether the current user is an Administrator.

        Admin is determined by role_code = ADMIN.
        """

        if not user:
            return False

        # ==============================================
        # Check role_code
        # ==============================================

        role_code = getattr(
            user,
            "role_code",
            None,
        )

        if role_code:
            role_code = role_code.strip().upper()

        if role_code == "ADMIN":
            return True

        # ==============================================
        # Fallback: is_admin property
        # ==============================================

        return bool(
            getattr(
                user,
                "is_admin",
                False,
            )
        )

    # ======================================================
    # PROBLEM - ASSIGN
    # ======================================================

    def can_assign_problem(
        self,
        user=None,
        problem=None,
        employee_id=None,
        role_code=None,
    ):
        """
        Check whether a user/employee can assign
        PIC for a Problem.

        Supports the existing Problem authorization
        calling style:

            employee_id
            role_code
            problem

        and the new style:

            user
            problem

        Authorization requires:

        1. Problem exists
        2. Employee exists
        3. PROBLEM_ASSIGN permission
        when User object is available
        4. Problem Assignment Authority exists
        for the Problem department

        role_code is accepted for compatibility with
        the existing Problem authorization flow.
        """

        # ==================================================
        # Validate Problem
        # ==================================================

        if not problem:

            return False

        # ==================================================
        # Resolve Employee ID
        # ==================================================

        if employee_id is None and user is not None:

            employee_id = getattr(
                user,
                "employee_id",
                None,
            )

        if not employee_id:

            return False

        # ==================================================
        # Authentication & Permission
        # ==================================================

        if user is not None:

            if not self._is_authenticated(
                user
            ):

                return False

            if not user.has_permission(
                "PROBLEM_ASSIGN"
            ):

                return False

        # ==================================================
        # ADMIN
        # ==================================================

        if user is not None:

            if self._is_admin(
                user
            ):

                return True

        # ==================================================
        # Department
        # ==================================================

        department_id = getattr(
            problem,
            "department_id",
            None,
        )

        if not department_id:

            return False

        # ==================================================
        # Problem Assignment Authority
        # ==================================================

        has_authority = (
            self
            .problem_assignment_authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

        if not has_authority:

            return False

        # ==================================================
        # Role Code
        # ==================================================

        # role_code is intentionally accepted here
        # for compatibility with the existing
        # Problem authorization flow.
        #
        # The actual authority is determined by:
        #
        # department_id + employee_id
        #
        # not by role_code alone.

        return True
    # ======================================================
    # IMPROVEMENT - ASSIGNMENT
    # ======================================================

    def can_assign_improvement(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can access
        Improvement Assignment.

        Required:

        1. Authenticated user
        2. IMPROVEMENT_ASSIGN permission
        3. Improvement Assignment Authority
           for the department of the related Problem
        """

        # ==============================================
        # User
        # ==============================================

        if not self._is_authenticated(
            user
        ):

            return False

        # ==============================================
        # Improvement
        # ==============================================

        if not improvement:

            return False

        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_ASSIGN"
        ):

            return False

        # ==============================================
        # Admin
        # ==============================================

        if self._is_admin(
            user
        ):

            return True

        # ==============================================
        # Employee
        # ==============================================

        employee_id = (
            getattr(
                user,
                "employee_id",
                None,
            )
        )

        if not employee_id:

            return False

        # ==============================================
        # Related Problem
        # ==============================================

        problem = (
            getattr(
                improvement,
                "problem",
                None,
            )
        )

        if not problem:

            return False

        # ==============================================
        # Department
        # ==============================================

        department_id = (
            getattr(
                problem,
                "department_id",
                None,
            )
        )

        if not department_id:

            return False

        # ==============================================
        # Assignment Authority
        # ==============================================

        return (
            self
            .improvement_assignment_authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ======================================================
    # IMPROVEMENT - APPROVE
    # ======================================================

    def can_approve_improvement(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can approve
        an Improvement.

        Admin:
            Always allowed.

        Normal user:
            Required:
            1. Authenticated user
            2. IMPROVEMENT_APPROVE permission
            3. Improvement Approval Authority
            for the department of the related Problem
        """

        # ==============================================
        # User
        # ==============================================

        if not self._is_authenticated(
            user
        ):

            return False


        # ==============================================
        # Improvement
        # ==============================================

        if not improvement:

            return False


        # ==============================================
        # ADMIN
        # ==============================================

        if self._is_admin(
            user
        ):

            return True


        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_APPROVE"
        ):

            return False


        # ==============================================
        # Employee
        # ==============================================

        employee_id = (
            getattr(
                user,
                "employee_id",
                None,
            )
        )

        if not employee_id:

            return False


        # ==============================================
        # Related Problem
        # ==============================================

        problem = (
            getattr(
                improvement,
                "problem",
                None,
            )
        )

        if not problem:

            return False


        # ==============================================
        # Department
        # ==============================================

        department_id = (
            getattr(
                problem,
                "department_id",
                None,
            )
        )

        if not department_id:

            return False


        # ==============================================
        # Approval Authority
        # ==============================================

        return (
            self
            .improvement_approval_authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ======================================================
    # IMPROVEMENT - OWNER
    # ======================================================

    def is_improvement_owner(
        self,
        user,
        improvement,
    ):
        """
        Check whether user is the Owner
        of the Improvement.
        """

        if not self._is_authenticated(
            user
        ):

            return False

        if not improvement:

            return False

        employee_id = (
            getattr(
                user,
                "employee_id",
                None,
            )
        )

        if not employee_id:

            return False

        return (
            improvement.owner_employee_id
            == employee_id
        )

    # ==================================================
    # IMPROVEMENT EDIT
    # ==================================================

    def can_edit_improvement(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can edit an Improvement.

        Rules:
        1. ADMIN can edit all Improvements.
        2. Normal user must have IMPROVEMENT_EDIT.
        3. Owner can edit his/her own Improvement.
        4. Active Improvement PIC can edit the Improvement.
        5. Other users cannot edit.
        """

        # ==============================================
        # Authentication
        # ==============================================

        if not user:

            return False

        if not user.is_authenticated:

            return False

        # ==============================================
        # Improvement
        # ==============================================

        if not improvement:

            return False

        # ==============================================
        # ADMIN
        # ==============================================

        is_admin = (
            getattr(
                user,
                "is_admin",
                False,
            )
            or getattr(
                user,
                "role_code",
                None,
            ) == "ADMIN"
        )

        if is_admin:

            return True

        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_EDIT"
        ):

            return False

        # ==============================================
        # Employee
        # ==============================================

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:

            return False

        # ==============================================
        # OWNER
        # ==============================================

        if (
            improvement.owner_employee_id
            == employee_id
        ):

            return True

        # ==============================================
        # ACTIVE IMPROVEMENT PIC
        # ==============================================

        if self.improvement_pic_repository.is_pic(
            improvement_id=improvement.id,
            employee_id=employee_id,
        ):

            return True

        # ==============================================
        # NOT AUTHORIZED
        # ==============================================

        return False
    # ======================================================
    # IMPROVEMENT - DELETE
    # ======================================================

    def can_delete_improvement(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can delete
        an Improvement.

        Required:

        - IMPROVEMENT_DELETE permission
        - User must be Owner
        """

        if not self._is_authenticated(
            user
        ):

            return False

        if not improvement:

            return False

        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_DELETE"
        ):

            return False

        # ==============================================
        # Admin
        # ==============================================

        if self._is_admin(
            user
        ):

            return True

        # ==============================================
        # Ownership
        # ==============================================

        return self.is_improvement_owner(
            user=user,
            improvement=improvement,
        )

    # ======================================================
    # PROBLEM - EDIT
    # ======================================================

    def can_edit_problem(
        self,
        user=None,
        problem=None,
        employee_id=None,
        role_code=None,
    ):
        """
        Check whether an employee/user can edit a Problem.

        Allowed:
            1. Admin
            2. Problem Reporter / Owner

        Reporter and Owner are treated as the same
        business owner of the Problem.

        role_code is kept for backward compatibility.
        """

        # ==============================================
        # Validate Problem
        # ==============================================

        if not problem:

            return False

        # ==============================================
        # Resolve Employee ID
        # ==============================================

        if employee_id is None and user is not None:

            employee_id = getattr(
                user,
                "employee_id",
                None,
            )

        if not employee_id:

            return False

        # ==============================================
        # Authentication
        # ==============================================

        if user is not None:

            if not self._is_authenticated(
                user
            ):

                return False

            # ==========================================
            # Admin
            # ==========================================

            if self._is_admin(
                user
            ):

                return True

            # ==========================================
            # Permission
            # ==========================================

            if not user.has_permission(
                "PROBLEM_EDIT"
            ):

                return False

        # ==============================================
        # Problem Reporter / Owner
        # ==============================================

        reporter_employee_id = getattr(
            problem,
            "reporter_employee_id",
            None,
        )

        if (
            reporter_employee_id
            and employee_id == reporter_employee_id
        ):

            return True

        # ==============================================
        # Not Authorized
        # ==============================================

        return False

    # ==================================================
    # IMPROVEMENT IMPLEMENTATION RESULT
    # ==================================================

    def can_update_implementation_result(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can add/update
        Improvement Implementation Result.

        Allowed:
        - ADMIN
        - Improvement Owner
        - Active Improvement PIC

        Normal user must also have:
        IMPROVEMENT_EDIT
        """

        # ==============================================
        # Authentication
        # ==============================================

        if not user:

            return False

        if not user.is_authenticated:

            return False

        # ==============================================
        # Improvement
        # ==============================================

        if not improvement:

            return False

        # ==============================================
        # ADMIN
        # ==============================================

        is_admin = (
            getattr(
                user,
                "is_admin",
                False,
            )
            or getattr(
                user,
                "role_code",
                None,
            ) == "ADMIN"
        )

        if is_admin:

            return True

        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_EDIT"
        ):

            return False

        # ==============================================
        # Employee
        # ==============================================

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:

            return False

        # ==============================================
        # OWNER
        # ==============================================

        if (
            improvement.owner_employee_id
            == employee_id
        ):

            return True

        # ==============================================
        # ACTIVE PIC
        # ==============================================

        if self.improvement_pic_repository.is_pic(
            improvement_id=improvement.id,
            employee_id=employee_id,
        ):

            return True

        # ==============================================
        # DENY
        # ==============================================

        return False

    # ==================================================
    # IMPROVEMENT VERIFY
    # ==================================================

    # ==================================================
    # IMPROVEMENT VERIFY
    # ==================================================

    def can_verify_improvement(
        self,
        user,
        improvement,
    ):
        """
        Check whether user can verify an Improvement.

        Allowed:
        - ADMIN
        - Improvement Owner
        - Active Improvement PIC

        Normal user must have:
        IMPROVEMENT_EDIT
        """

        # ==============================================
        # Authentication
        # ==============================================

        if not user:

            return False

        if not user.is_authenticated:

            return False

        # ==============================================
        # Improvement
        # ==============================================

        if not improvement:

            return False

        # ==============================================
        # ADMIN
        # ==============================================

        is_admin = (
            getattr(
                user,
                "is_admin",
                False,
            )
            or getattr(
                user,
                "role_code",
                None,
            ) == "ADMIN"
        )

        if is_admin:

            return True

        # ==============================================
        # Permission
        # ==============================================

        if not user.has_permission(
            "IMPROVEMENT_EDIT"
        ):

            return False

        # ==============================================
        # Employee
        # ==============================================

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:

            return False

        # ==============================================
        # OWNER
        # ==============================================

        if (
            improvement.owner_employee_id
            == employee_id
        ):

            return True

        # ==============================================
        # ACTIVE IMPROVEMENT PIC
        # ==============================================

        if self.improvement_pic_repository.is_pic(
            improvement_id=improvement.id,
            employee_id=employee_id,
        ):

            return True

        # ==============================================
        # NOT AUTHORIZED
        # ==============================================

        return False

    def can_edit_kaizen(
        self,
        user,
        kaizen,
    ):
        """
        Check whether user can edit a Kaizen.

        Admin:
            Can edit all Kaizen.

        Normal user:
            Can only edit Kaizen created by himself.

        Kaizen creator is stored in:
            kaizen.employee_id
        """

        # ==============================================
        # Authentication
        # ==============================================

        if not self._is_authenticated(
            user
        ):

            return False


        # ==============================================
        # Kaizen
        # ==============================================

        if not kaizen:

            return False


        # ==============================================
        # ADMIN
        # ==============================================

        if self._is_admin(
            user
        ):

            return True


        # ==============================================
        # Current Employee
        # ==============================================

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:

            return False


        # ==============================================
        # Kaizen Creator / PIC
        # ==============================================

        return (
            kaizen.employee_id
            == employee_id
        )

    # ==========================================================
    # KAIZEN APPROVAL
    # ==========================================================

    def can_approve_kaizen(
        self,
        user,
        kaizen,
    ):
        """
        Check whether user can approve a Kaizen.

        Required for normal user:

        1. Authenticated user
        2. KAIZEN_APPROVE permission
        3. Kaizen Approval Authority
        for the Kaizen department

        ADMIN:
            Always allowed.
        """

        # ==================================================
        # Authentication
        # ==================================================

        if not self._is_authenticated(
            user
        ):

            return False


        # ==================================================
        # Kaizen
        # ==================================================

        if not kaizen:

            return False


        # ==================================================
        # Permission
        # ==================================================

        if not user.has_permission(
            "KAIZEN_APPROVE"
        ):

            return False


        # ==================================================
        # ADMIN
        # ==================================================

        if self._is_admin(
            user
        ):

            return True


        # ==================================================
        # Employee
        # ==================================================

        employee_id = (
            getattr(
                user,
                "employee_id",
                None,
            )
        )

        if not employee_id:

            return False


        # ==================================================
        # Kaizen Department
        # ==================================================

        department_id = (
            getattr(
                kaizen,
                "department_id",
                None,
            )
        )

        if not department_id:

            return False


        # ==================================================
        # Approval Authority
        # ==================================================

        return (
            self
            .kaizen_approval_authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ==========================================================
    # KAIZEN REJECTION
    # ==========================================================

    def can_reject_kaizen(
        self,
        user,
        kaizen,
    ):
        """
        Check whether user can reject a Kaizen.

        Uses the same authority as Kaizen Approval.

        Required for normal user:

        1. Authenticated user
        2. KAIZEN_APPROVE permission
        3. Kaizen Approval Authority
        for the Kaizen department

        ADMIN:
            Always allowed.
        """

        # ==================================================
        # Authentication
        # ==================================================

        if not self._is_authenticated(
            user
        ):

            return False


        # ==================================================
        # Kaizen
        # ==================================================

        if not kaizen:

            return False


        # ==================================================
        # Permission
        # ==================================================

        if not user.has_permission(
            "KAIZEN_APPROVE"
        ):

            return False


        # ==================================================
        # ADMIN
        # ==================================================

        if self._is_admin(
            user
        ):

            return True


        # ==================================================
        # Employee
        # ==================================================

        employee_id = (
            getattr(
                user,
                "employee_id",
                None,
            )
        )

        if not employee_id:

            return False


        # ==================================================
        # Kaizen Department
        # ==================================================

        department_id = (
            getattr(
                kaizen,
                "department_id",
                None,
            )
        )

        if not department_id:

            return False


        # ==================================================
        # Approval Authority
        # ==================================================

        return (
            self
            .kaizen_approval_authority_repository
            .has_authority(
                department_id=department_id,
                employee_id=employee_id,
            )
        )

    # ==========================================================
    # KAIZEN - AWARD JUDGE ASSIGN
    # ==========================================================

    def can_assign_award_judge(self, user):
        """
        Check whether user can assign an Award Judge.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_JUDGE_ASSIGN permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_JUDGE_ASSIGN"
        )


    # ==========================================================
    # KAIZEN - AWARD JUDGE REMOVE
    # ==========================================================

    def can_remove_award_judge(self, user):
        """
        Check whether user can remove an Award Judge.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_JUDGE_REMOVE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_JUDGE_REMOVE"
        )


    # ==========================================================
    # KAIZEN - AWARD PERIOD CREATE
    # ==========================================================

    def can_create_award_period(self, user):
        """
        Check whether user can create a Kaizen Award Period.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_PERIOD_CREATE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_PERIOD_CREATE"
        )


    # ==========================================================
    # KAIZEN - AWARD PERIOD CLOSE
    # ==========================================================

    def can_close_award_period(self, user):
        """
        Check whether user can close a Kaizen Award Period.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_PERIOD_CLOSE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_PERIOD_CLOSE"
        )


    # ==========================================================
    # KAIZEN - AWARD SCORE EDIT
    # ==========================================================

    def can_edit_award_score(self, user):
        """
        Check whether user can edit an Award Score.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_SCORE_EDIT permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_SCORE_EDIT"
        )


    # ==========================================================
    # KAIZEN - AWARD SCORE CREATE
    # ==========================================================

    def can_create_award_score(self, user):
        """
        Check whether user can create an Award Score.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_AWARD_SCORE_CREATE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_AWARD_SCORE_CREATE"
        )


    # ==========================================================
    # KAIZEN - REPORTING PERIOD CREATE
    # ==========================================================

    def can_create_reporting_period(self, user):
        """
        Check whether user can create a Kaizen Reporting Period.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_REPORTING_PERIOD_CREATE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_REPORTING_PERIOD_CREATE"
        )


    # ==========================================================
    # KAIZEN - REPORTING PERIOD EDIT
    # ==========================================================

    def can_edit_reporting_period(self, user):
        """
        Check whether user can edit a Kaizen Reporting Period.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_REPORTING_PERIOD_EDIT permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_REPORTING_PERIOD_EDIT"
        )


    # ==========================================================
    # KAIZEN - REPORTING PERIOD DELETE
    # ==========================================================

    def can_delete_reporting_period(self, user):
        """
        Check whether user can delete a Kaizen Reporting Period.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_REPORTING_PERIOD_DELETE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_REPORTING_PERIOD_DELETE"
        )


    # ==========================================================
    # KAIZEN - DEPARTMENT TARGET CREATE
    # ==========================================================

    def can_create_department_target(self, user):
        """
        Check whether user can create a Kaizen Department Target.

        Allowed:
            1. ADMIN
            2. User with KAIZEN_DEPARTMENT_TARGET_CREATE permission
        """

        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission(
            "KAIZEN_DEPARTMENT_TARGET_CREATE"
        )

    def can_edit_award_period(self, user):
        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission("KAIZEN_AWARD_PERIOD_EDIT")


    def can_delete_award_period(self, user):
        if not self._is_authenticated(user):
            return False

        if self._is_admin(user):
            return True

        return user.has_permission("KAIZEN_AWARD_PERIOD_DELETE")

    # ==========================================================
    # ISSUE - EDIT
    # ==========================================================

    def can_edit_issue(
        self,
        user,
        issue,
    ):
        """
        Check whether user can edit an Issue.

        Allowed:
        1. ADMIN
        2. Issue creator / requestor

        Other users:
            Read only
        """

        # ==================================================
        # Authentication
        # ==================================================

        if not self._is_authenticated(
            user
        ):

            return False

        # ==================================================
        # Issue
        # ==================================================

        if not issue:

            return False

        # ==================================================
        # ADMIN
        # ==================================================

        if self._is_admin(
            user
        ):

            return True

        # ==================================================
        # Employee
        # ==================================================

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:

            return False

        # ==================================================
        # ISSUE CREATOR / REQUESTOR
        # ==================================================

        return (
            issue.requestor_employee_id
            == employee_id
        )


    # ==========================================================
    # ISSUE - ADD ATTACHMENT
    # ==========================================================

    def can_add_issue_attachment(
        self,
        user,
        issue,
    ):
        """
        Check whether user can add an attachment
        to an Issue.

        Allowed:
        1. ADMIN
        2. Issue creator / requestor

        Other users:
            Read only
        """

        return self.can_edit_issue(
            user=user,
            issue=issue,
        )


    # ==========================================================
    # ISSUE - DELETE ATTACHMENT
    # ==========================================================

    def can_delete_issue_attachment(
        self,
        user,
        issue,
    ):
        """
        Check whether user can delete an attachment
        from an Issue.

        Allowed:
        1. ADMIN
        2. Issue creator / requestor

        Other users:
            Read only
        """

        return self.can_edit_issue(
            user=user,
            issue=issue,
        )


    # ==========================================================
    # ISSUE - DELETE
    # ==========================================================

    def can_delete_issue(
        self,
        user,
        issue,
    ):
        """
        Check whether user can delete an Issue.

        Allowed:
        1. ADMIN
        2. Issue creator / requestor

        Other users:
            Read only
        """

        return self.can_edit_issue(
            user=user,
            issue=issue,
        )

    # ==========================================================
    # ISSUE - REQUEST CLARIFICATION
    # ==========================================================

    def can_request_issue_clarification(self, user, issue):
        """
        Only ADMIN can request clarification for an Issue.
        """

        if not self._is_authenticated(user):
            return False

        if not issue:
            return False

        return self._is_admin(user)

    # ==========================================================
    # ISSUE - RESPOND CLARIFICATION
    # ==========================================================

    def can_respond_issue_clarification(
        self,
        user,
        clarification,
    ):
        """
        Only the Issue requestor can respond
        to an open clarification.
        """

        if not self._is_authenticated(user):
            return False

        if not clarification:
            return False

        if clarification.status != "OPEN":
            return False

        issue = clarification.issue

        if not issue:
            return False

        employee_id = getattr(
            user,
            "employee_id",
            None,
        )

        if not employee_id:
            return False

        return (
            issue.requestor_employee_id
            == employee_id
        )