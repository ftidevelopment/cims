from sqlalchemy import or_

from app.models.user import User
from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository
from app.core.service_result import ServiceResult
from werkzeug.security import generate_password_hash
from app.models.role import Role


class UserRepository(BaseRepository):

    searchable_fields = [
        User.username,
        Employee.nik,
        Employee.full_name,
    ]

    sortable_fields = {
        "username": User.username,
        "last_login": User.last_login,
        "created_at": User.created_at,
    }

    def __init__(self):
        super().__init__(User)

    # ==========================================================
    # Query
    # ==========================================================

    def get_by_username(self, username):
        return self.model.query.filter_by(
            username=username
        ).first()

    def get_by_employee_id(self, employee_id):
        return self.model.query.filter_by(
            employee_id=employee_id
        ).first()

    def get_by_email(self, email):
        return (
            self.model.query
            .join(Employee)
            .filter(Employee.email == email)
            .first()
        )

    # ==========================================================
    # Validation
    # ==========================================================

    def username_exists(
        self,
        username,
        exclude_id=None,
    ):
        query = self.model.query.filter_by(
            username=username
        )

        if exclude_id:
            query = query.filter(
                self.model.id != exclude_id
            )

        return query.first() is not None

    def employee_exists(
        self,
        employee_id,
        exclude_id=None,
    ):
        query = self.model.query.filter_by(
            employee_id=employee_id
        )

        if exclude_id:
            query = query.filter(
                self.model.id != exclude_id
            )

        return query.first() is not None

    def has_user(self, employee_id):
        return (
            self.model.query
            .filter_by(employee_id=employee_id)
            .first()
            is not None
        )

    # ==========================================================
    # Override BaseRepository
    # ==========================================================

    def get_query(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        query = (
            self.model.query
            .outerjoin(
                Employee,
                User.employee_id == Employee.id,
            )
            .outerjoin(
                Role,
                User.role_id == Role.id,
            )
        )

        # ==========================================
        # Soft Delete
        # ==========================================

        if is_active is not None:

            query = query.filter(
                Employee.is_active == is_active
            )

        # ==========================================
        # Search
        # ==========================================

        if keyword:

            keyword = f"%{keyword}%"

            query = query.filter(
                or_(
                    User.username.ilike(keyword),
                    Employee.nik.ilike(keyword),
                    Employee.full_name.ilike(keyword),
                    Role.role_name.ilike(keyword),
                )
            )

        # ==========================================
        # Sorting
        # ==========================================

        if (
            sort_by
            and sort_by in self.sortable_fields
        ):

            column = self.sortable_fields[
                sort_by
            ]

            if sort_order.lower() == "desc":

                query = query.order_by(
                    column.desc()
                )

            else:

                query = query.order_by(
                    column.asc()
                )

        return query

        # ==========================================================
    # Account Management
    # ==========================================================

    def reset_password(
        self,
        user_id,
        new_password,
    ):

        user = self.repository.get_by_id(user_id)

        if not user:
            return ServiceResult(
                success=False,
                message="User not found."
            )

        user.password_hash = generate_password_hash(
            new_password
        )

        self.repository.update(user)

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Password reset successfully."
        )

    def unlock(
        self,
        user_id,
    ):

        user = self.repository.get_by_id(user_id)

        if not user:
            return ServiceResult(
                success=False,
                message="User not found."
            )

        user.is_locked = False
        user.failed_login_count = 0

        self.repository.update(user)

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="User unlocked successfully."
        )