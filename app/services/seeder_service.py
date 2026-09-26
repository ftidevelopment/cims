from werkzeug.security import generate_password_hash

from app.extensions import db

from app.models.employee import Employee
from app.models.user import User
from app.models.role import Role
from app.services.base_service import BaseService

from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository

from app.core.transaction_manager import TransactionManager
from app.services.seeder.role_seeder import (
    RoleSeeder,
)

class SeederService(BaseService):

    def __init__(self):
        super().__init__()

        self.department_repository = DepartmentRepository()
        self.employee_repository = EmployeeRepository()
        self.user_repository = UserRepository()

    def create_admin(self):

    # ==========================================
    # Check existing admin user
    # ==========================================

        existing_user = (
            self.user_repository
            .get_by_username("admin")
        )

        if existing_user:
            return self.failed(
                "Administrator already exists."
            )

        # ==========================================
        # Get MIS Department
        # ==========================================

        department = (
            self.department_repository
            .get_by_code("104")
        )

        if not department:
            return self.failed(
                "Department '104' (MIS) not found. "
                "Please create it first."
            )

        # ==========================================
        # Get ADMIN Role
        # ==========================================

        admin_role = (
            Role.query
            .filter_by(
                role_code="ADMIN",
                is_active=True,
            )
            .first()
        )

        if not admin_role:
            return self.failed(
                "Role 'ADMIN' not found. "
                "Please create the ADMIN role first."
            )

        # ==========================================
        # Create Admin
        # ==========================================

        try:

            with TransactionManager():

                employee = Employee(
                    nik="ADMIN001",
                    full_name="System Administrator",
                    department_id=department.id,
                    email="admin@company.local",
                    phone_number="-",
                    telegram_chat_id="-",
                    status="ACTIVE",
                )

                self.employee_repository.create(
                    employee
                )

                db.session.flush()

                user = User(
                    employee_id=employee.id,
                    role_id=admin_role.id,
                    username="admin",
                    password_hash=generate_password_hash(
                        "admin123"
                    ),
                    failed_login_count=0,
                    is_locked=False,
                )

                self.user_repository.create(
                    user
                )

            return self.success(
                "Administrator created successfully."
            )

        except Exception as ex:

            return self.handle_exception(ex)
    # ==========================================
    # Seed All Master Data
    # ==========================================

    def seed_all(
        self,
    ):

        try:

            role_created = (
                RoleSeeder().seed()
            )

            return self.success(
                f"Master data seeded successfully. "
                f"Role created : {role_created}"
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )