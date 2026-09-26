from sqlalchemy import or_
from app.models.employee import Employee
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.services.base_service import BaseService
from app.core.transaction_manager import TransactionManager
from app.core.service_result import ServiceResult
from app.services.base_export_service import BaseExportService


class EmployeeService(BaseService, BaseExportService):
    """
    Business logic for Employee.
    """

    EXPORT_CONFIG = [
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
            "header": "Department",
            "field": "department.department_name",
            "width": 30,
        },
        {
            "header": "Email",
            "field": "email",
            "width": 35,
        },
        {
            "header": "Phone Number",
            "field": "phone_number",
            "width": 20,
        },
        {
            "header": "Telegram Chat ID",
            "field": "telegram_chat_id",
            "width": 20,
        },
        {
            "header": "Status",
            "field": "is_active",
            "width": 15,
        },
    ]

    def __init__(self):       

        self.repository = EmployeeRepository()
        self.department_repository = DepartmentRepository()
        self.transaction = TransactionManager()

    # ==========================================================
    # Query
    # ==========================================================

    def get_by_id(self, employee_id):
        return self.repository.get_by_id(employee_id)


    def get_all(
            self,
            keyword=None,
            is_active=True,
            page=1,
            per_page=10,
            sort_by="created_at",
            sort_order="desc",
        ):
    
            return self.repository.get_all(
                keyword=keyword,
                is_active=is_active,
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
            )

    def get_active(self):
        return self.repository.get_active()

    # ==========================================================
    # Command
    # ==========================================================

    def create(
            self,
            nik,
            full_name,
            department_id,
            email,
            phone_number,
            telegram_chat_id,
            line_user_id,
        ):

            # Validasi department
            department = self.department_repository.get_by_id(
                department_id
            )

            if not department:
                raise ValueError(
                    "Department not found."
                )     
                   
            # Validasi NIK
            if self.repository.get_by_nik(nik):
                raise ValueError(
                    "NIK already exists."
                )
            
            
            # Validasi Email
            if self.repository.get_by_email(email):
                raise ValueError(
                    "Email already exists."
                )  
            # Validasi Phone Number
            if self.repository.get_by_phone_number(phone_number):
                raise ValueError(
                    "Phone number already exists."
                )                       
            # Validasi telegram id
            if telegram_chat_id:

                if self.repository.get_by_telegram_chat_id(
                    telegram_chat_id
                ):
                    raise ValueError(
                        "Telegram ID already exists."
                    )
            # Validasi line id
            if line_user_id:

                if self.repository.get_by_line_user_id(
                    line_user_id
                ):
                    raise ValueError(
                        "LINE ID already exists."
                    )
                  
            employee = Employee(
                nik=nik,
                full_name=full_name,
                department_id=department_id,
                email=email,
                phone_number=phone_number,
                telegram_chat_id=telegram_chat_id,
                line_user_id=line_user_id,
            )
    
            self.repository.create(employee)
    
            self.transaction.commit()
    
            return employee
    

    def update(self, 
            employee,
            nik,
            full_name,
            department_id,
            email,
            phone_number,
            telegram_chat_id,
            line_user_id
        ):
            department = self.department_repository.get_by_id(
                department_id
            )

            if not department:
                raise ValueError(
                    "Department not found."
                )
            
            existing = self.repository.get_by_nik(nik)

            if existing and existing.id != employee.id:
                raise ValueError(
                    "NIK already exists."
                )

            existing = self.repository.get_by_email(email)

            if existing and existing.id != employee.id:
                raise ValueError(
                    "Email already exists."
                )

            existing = self.repository.get_by_phone_number(
                phone_number
            )

            if (
                phone_number
                and existing
                and existing.id != employee.id
            ):
                raise ValueError(
                    "Phone number already exists."
                )

            existing = self.repository.get_by_telegram_chat_id(
                telegram_chat_id
            )

            if (
                telegram_chat_id
                and existing
                and existing.id != employee.id
            ):
                raise ValueError(
                    "Telegram ID already exists."
                )

            existing = self.repository.get_by_line_user_id(
                line_user_id
            )

            if (
                line_user_id
                and existing
                and existing.id != employee.id
            ):
                raise ValueError(
                    "LINE ID already exists."
                )

            employee.nik = nik
            employee.full_name = full_name
            employee.department_id = department_id
            employee.email = email
            employee.phone_number = phone_number
            employee.telegram_chat_id = telegram_chat_id
            employee.line_user_id = line_user_id

            self.repository.update(employee)
        
            self.transaction.commit()
        
            return employee     
        

    def delete(self, employee):
        self.repository.delete(employee)       
        self.transaction.commit()


    def get_inactive(self):
        return self.repository.get_inactive()
    

    def restore(self, employee_id):
        employee = self.repository.restore(employee_id)

        if not employee:
            return ServiceResult(
                success=False,
                message="Employee not found."
            )

        self.transaction.commit()

        return ServiceResult(
            success=True,
            message="Employee restored successfully."
        )    

    def get_departments(self):
        return self.department_repository.get_active()

    def export_excel(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):
        return self.export(
            sheet_name="Employee",
            export_config=self.EXPORT_CONFIG,
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_pic_candidates_by_department(
        self,
        department_id,
    ):

        return (
            self.repository
            .get_pic_candidates_by_department(
                department_id
            )
        )

    def get_pic_candidates(self):

        return (
            self.repository
            .get_pic_candidates()
        )

  
