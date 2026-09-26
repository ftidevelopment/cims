from datetime import datetime
from flask_login import UserMixin
from app.extensions import db
from app.models.base_model import BaseModel


class User(UserMixin,BaseModel):
    """
    User Account
    """

    __tablename__ = "users"

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        unique=True,
        nullable=False,
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "roles.id"
        ),
        nullable=False,
        index=True,
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True,
    )

    failed_login_count = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    is_locked = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    employee = db.relationship(
        "Employee",
        backref=db.backref(
            "user",
            uselist=False,
        ),
    )

    role = db.relationship(
        "Role",
        back_populates="users",
    )

    # ============================================
    # Business Methods
    # ============================================

    def update_last_login(self):
        self.last_login = datetime.utcnow()

    def reset_failed_login(self):
        self.failed_login_count = 0

    def increase_failed_login(self):
        self.failed_login_count += 1

    def lock(self):
        self.is_locked = True

    def unlock(self):
        self.is_locked = False
        self.failed_login_count = 0

    def change_password(self, password_hash):
        self.password_hash = password_hash
    # ============================================
    # Properties
    # ============================================

    @property
    def full_name(self):
        return self.employee.full_name

    @property
    def nik(self):
        return self.employee.nik

    @property
    def department_name(self):
        return self.employee.department.department_name

    @property
    def department_code(self):
        return self.employee.department.department_code

    @property
    def role_code(self):

        if not self.role:
            return ""

        return self.role.role_code


    @property
    def role_name(self):

        if not self.role:
            return ""

        return self.role.role_name

    @property
    def email(self):
        return self.employee.email

    @property
    def phone_number(self):
        return self.employee.phone_number

    @property
    def telegram_chat_id(self):
        return self.employee.telegram_chat_id

    @property
    def status(self):
        return self.employee.status

        # ==========================================
    # Authorization
    # ==========================================

    def has_permission(
        self,
        permission_code,
    ):
        """
        Check whether the user has
        the specified permission.
        """

        if not self.role:
            return False

        permission_code = (
            permission_code
            .strip()
            .upper()
        )

        for role_permission in (
            self.role.role_permissions
        ):

            permission = (
                role_permission.permission
            )

            if not permission:
                continue

            if not permission.is_active:
                continue

            if (
                permission.permission_code
                == permission_code
            ):
                return True

        return False

    def has_any_permission(
        self,
        *permission_codes,
    ):
        """
        Return True if the user has
        at least one of the specified
        permissions.
        """

        for permission_code in permission_codes:

            if self.has_permission(
                permission_code
            ):
                return True

        return False

    def has_all_permissions(
        self,
        *permission_codes,
    ):
        """
        Return True if the user has
        all specified permissions.
        """

        for permission_code in permission_codes:

            if not self.has_permission(
                permission_code
            ):
                return False

        return True

    def __repr__(self):
        return (
            f"<User("
            f"username='{self.username}', "
            f"role='{self.role_code}'"
            f")>"
        )