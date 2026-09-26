from sqlalchemy import and_
from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.models.role import Role

class EmployeeRepository(BaseRepository):
    """
    Repository for Employee.
    """

    model = Employee

    searchable_fields = [
        Employee.nik,
        Employee.full_name,
        Employee.email,
    ]

    sortable_fields = {
        "nik": Employee.nik,
        "full_name": Employee.full_name,
        "email": Employee.email,
        "status": Employee.status,
        "created_at": Employee.created_at,
    }

    def __init__(self):
        super().__init__(Employee)

    def get_by_nik(self, nik: str):
        return self.get_first_by(nik=nik)

    def get_by_email(self, email: str):
        return self.get_first_by(email=email)

    def get_by_phone_number(self, phone_number: str):
        return self.get_first_by(phone_number=phone_number)

    def get_by_telegram_chat_id(self, telegram_chat_id: str):
        return self.get_first_by(telegram_chat_id=telegram_chat_id)

    def get_by_line_user_id(self, line_user_id):
        return Employee.query.filter_by(
            line_user_id=line_user_id
        ).first()

    def exists_by_nik(self, nik: str) -> bool:
        return self.exists_by(nik=nik)

    def exists_by_email(self, email: str) -> bool:
        return self.exists_by(email=email)

    def exists_by_phone_number(self, phone_number: str) -> bool:
        return self.exists_by(phone_number=phone_number)

    def exists_by_telegram_chat_id(self, telegram_chat_id: str) -> bool:
        return self.exists_by(telegram_chat_id=telegram_chat_id)


    def get_active(self):
        return (
            self.model.query
            .filter_by(status="ACTIVE")
            .all()
        )
    
    def get_without_user(self):
        return (
            self.model.query
            .filter(
                ~self.model.user.has()
            )
            .order_by(
                self.model.full_name.asc()
            )
            .all()
        )

    def get_pic_candidates_by_department(
        self,
        department_id,
    ):
        """
        Get active employees who can be assigned
        as Problem PIC for a specific department.

        Eligible roles:
        - MANAGER
        - SUPERVISOR
        """

        return (
            self.model.query
            .join(
                User,
                User.employee_id == self.model.id
            )
            .join(
                Role,
                Role.id == User.role_id
            )
            .filter(
                self.model.department_id == department_id,
                self.model.status == "ACTIVE",
                Role.role_code.in_(
                    [
                        "MANAGER",
                        "SUPERVISOR",
                    ]
                ),
            )
            .order_by(
                self.model.full_name.asc()
            )
            .all()
        )

    def get_pic_candidates(self):
        """
        Get all active employees who have
        a User account.

        Eligible:
        - Employee is ACTIVE
        - Has User account
        - Role does not matter
        - Department does not matter
        """

        return (
            self.model.query
            .join(
                User,
                User.employee_id == self.model.id
            )
            .filter(
                self.model.status == "ACTIVE"
            )
            .order_by(
                self.model.department_id.asc(),
                self.model.full_name.asc(),
            )
            .all()
        )

    def get_active_by_department(
        self,
        department_id,
    ):
        """
        Get active employees for a specific department.
        """

        return (
            self.model.query
            .filter(
                self.model.department_id == department_id,
                self.model.status == "ACTIVE",
            )
            .order_by(
                self.model.full_name.asc()
            )
            .all()
        )

    def get_active_by_nik(self, nik: str):
        """
        Get active employee by NIK.
        """

        if not nik:
            return None

        return (
            self.model.query
            .filter(
                self.model.nik == nik,
                self.model.status == "ACTIVE",
            )
            .first()
        )