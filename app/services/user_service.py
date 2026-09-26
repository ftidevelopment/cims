from werkzeug.security import generate_password_hash

from app.models.user import (
    User,
)

from app.repositories.user_repository import (
    UserRepository,
)

from app.repositories.employee_repository import (
    EmployeeRepository,
)

from app.repositories.role_repository import (
    RoleRepository,
)

from app.services.base_service import (
    BaseService,
)

from app.services.base_export_service import (
    BaseExportService,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class UserService(
    BaseService,
):

    EXPORT_CONFIG = [

        {
            "header": "Username",
            "field": "username",
            "width": 25,
        },

        {
            "header": "NIK",
            "field": "nik",
            "width": 18,
        },

        {
            "header": "Full Name",
            "field": "full_name",
            "width": 35,
        },

        {
            "header": "Role",
            "field": "role_name",
            "width": 25,
        },

        {
            "header": "Last Login",
            "field": "last_login",
            "width": 25,
        },

        {
            "header": "Locked",
            "field": "is_locked",
            "width": 12,
        },

    ]

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self):

        super().__init__()

        self.repository = (
            UserRepository()
        )

        self.employee_repository = (
            EmployeeRepository()
        )

        self.role_repository = (
            RoleRepository()
        )

        self.export_service = (
            BaseExportService(
                self.repository
            )
        )

    # ==========================================
    # Get By ID
    # ==========================================

    def get_by_id(
        self,
        user_id,
    ):

        return self.repository.get_by_id(
            user_id
        )

    # ==========================================
    # Get All
    # ==========================================

    def get_all(
        self,
        keyword=None,
        page=1,
        per_page=10,
        sort_by="created_at",
        sort_order="desc",
    ):

        return self.repository.get_all(

            keyword=keyword,

            page=page,

            per_page=per_page,

            sort_by=sort_by,

            sort_order=sort_order,

        )

    # ==========================================
    # Get Active Users
    # ==========================================

    def get_active(self):

        return self.repository.get_active()

    # ==========================================
    # Available Employees
    # ==========================================

    def get_available_employees(self):

        employees = (
            self.employee_repository
            .get_active()
        )

        return [
            employee
            for employee in employees
            if not self.repository.has_user(
                employee.id
            )
        ]

    # ==========================================
    # Validate Role
    # ==========================================

    def _validate_role(
        self,
        role_id,
    ):

        if not role_id:

            raise ValueError(
                "Role is required."
            )

        role = (
            self.role_repository
            .get_by_id(
                role_id
            )
        )

        if not role:

            raise ValueError(
                "Role not found."
            )

        return role

    # ==========================================
    # Create
    # ==========================================

    def create(
        self,
        employee_id,
        username,
        password,
        role_id=None,
    ):

        # ==========================================
        # Validate Employee
        # ==========================================

        employee = (
            self.employee_repository
            .get_by_id(
                employee_id
            )
        )

        if not employee:

            raise ValueError(
                "Employee not found."
            )

        # ==========================================
        # Validate Employee Active
        # ==========================================

        if not employee.is_active:

            raise ValueError(
                "Employee is inactive."
            )

        # ==========================================
        # Validate Employee Already Has User
        # ==========================================

        if self.repository.get_by_employee_id(
            employee_id
        ):

            raise ValueError(
                "Employee already has a user account."
            )

        # ==========================================
        # Validate Username
        # ==========================================

        if self.repository.get_by_username(
            username
        ):

            raise ValueError(
                "Username already exists."
            )

        # ==========================================
        # Validate Role
        # ==========================================

        if not role_id:

            raise ValueError(
                "Role is required."
            )

        role = (
            self.role_repository
            .get_by_id(
                role_id
            )
        )

        if not role:

            raise ValueError(
                "Role not found."
            )

        # ==========================================
        # Create User
        # ==========================================

        with TransactionManager():

            user = User()

            user.employee_id = employee_id

            user.role_id = role_id

            user.username = username

            user.password_hash = (
                generate_password_hash(
                    password
                )
            )

            self.repository.create(
                user
            )

        return user

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        user,
        employee_id,
        role_id=None,
        username="",
    ):

        try:

            # ==========================================
            # Validate User
            # ==========================================

            self.validate_exists(
                user,
                "User",
            )

            # ==========================================
            # Validate Employee
            # ==========================================

            employee = (
                self.employee_repository.get_by_id(
                    employee_id
                )
            )

            self.validate_exists(
                employee,
                "Employee",
            )

            # ==========================================
            # Validate Role
            # ==========================================

            if role_id is None:

                raise ValueError(
                    "Role is required."
                )

            role = (
                self.role_repository.get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==========================================
            # Employee Duplicate
            # ==========================================

            existing = (
                self.repository.get_by_employee_id(
                    employee_id
                )
            )

            if (
                existing
                and existing.id != user.id
            ):

                raise ValueError(
                    "Employee already has a user account."
                )

            # ==========================================
            # Username Duplicate
            # ==========================================

            existing = (
                self.repository.get_by_username(
                    username
                )
            )

            if (
                existing
                and existing.id != user.id
            ):

                raise ValueError(
                    "Username already exists."
                )

            # ==========================================
            # Update
            # ==========================================

            with TransactionManager():

                user.employee_id = employee_id

                user.role_id = role_id

                user.username = username

                self.repository.update(
                    user
                )

            return self.success(
                "User updated successfully.",
                user,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Delete
    # ==========================================

    def delete(
        self,
        user,
    ):

        with TransactionManager():

            self.repository.delete(
                user
            )

    # ==========================================
    # Reset Password
    # ==========================================

    def reset_password(
        self,
        user_id,
        new_password,
    ):

        user = (
            self.repository
            .get_by_id(
                user_id
            )
        )

        self.validate_exists(
            user,
            "User",
        )

        with TransactionManager():

            user.password_hash = (
                generate_password_hash(
                    new_password
                )
            )

            self.repository.update(
                user
            )

        return self.success(
            "Password reset successfully."
        )

    # ==========================================
    # Unlock
    # ==========================================

    def unlock(
        self,
        user_id,
    ):

        user = (
            self.repository
            .get_by_id(
                user_id
            )
        )

        self.validate_exists(
            user,
            "User",
        )

        with TransactionManager():

            user.is_locked = False

            user.failed_login_count = 0

            self.repository.update(
                user
            )

        return self.success(
            "User unlocked successfully."
        )