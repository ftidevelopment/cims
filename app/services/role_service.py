from app.repositories.role_repository import (
    RoleRepository,
)

from app.models.role import (
    Role,
)

from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class RoleService(
    BaseService
):

    def __init__(self):

        super().__init__()

        self.repository = (
            RoleRepository()
        )

    # ==========================================
    # Get All
    # ==========================================

    def get_all(
        self,
        keyword=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):

        return self.repository.get_all(
            keyword=keyword,
            is_active=is_active,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # ==========================================
    # Get By Id
    # ==========================================

    def get_by_id(
        self,
        role_id,
    ):

        return self.repository.get_by_id(
            role_id
        )

    # ==========================================
    # Get By Code
    # ==========================================

    def get_by_code(
        self,
        role_code,
    ):

        return self.repository.get_by_code(
            role_code
        )

    # ==========================================
    # Get By Name
    # ==========================================

    def get_by_name(
        self,
        role_name,
    ):

        return self.repository.get_by_name(
            role_name
        )

    # ==========================================
    # Create
    # ==========================================

    def create(
        self,
        form_data,
        created_by=None,
    ):

        try:

            # ==================================
            # Get Form Data
            # ==================================

            role_code = (
                form_data.get(
                    "role_code",
                    ""
                ).strip().upper()
            )

            role_name = (
                form_data.get(
                    "role_name",
                    ""
                ).strip()
            )

            description = (
                form_data.get(
                    "description",
                    ""
                ).strip()
            )

            # ==================================
            # Validate Required
            # ==================================

            result = self.validate(
                self.validate_required(
                    role_code,
                    "Role Code",
                ),

                self.validate_required(
                    role_name,
                    "Role Name",
                ),
            )

            if not result.success:

                return result

            # ==================================
            # Validate Duplicate Role Code
            # ==================================

            if self.repository.exists_code(
                role_code
            ):

                return self.failed(
                    "Role Code already exists."
                )

            # ==================================
            # Validate Duplicate Role Name
            # ==================================

            if self.repository.exists_name(
                role_name
            ):

                return self.failed(
                    "Role Name already exists."
                )

            # ==================================
            # Create
            # ==================================

            with TransactionManager():

                role = Role()

                role.role_code = (
                    role_code
                )

                role.role_name = (
                    role_name
                )

                role.description = (
                    description
                    if description
                    else None
                )

                role.created_by = (
                    created_by
                )

                self.repository.create(
                    role
                )

            return self.success(
                "Role created successfully.",
                role,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        role_id,
        form_data,
        updated_by=None,
    ):

        try:

            # ==================================
            # Get Role
            # ==================================

            role = (
                self.repository.get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==================================
            # Get Form Data
            # ==================================

            role_code = (
                form_data.get(
                    "role_code",
                    ""
                ).strip().upper()
            )

            role_name = (
                form_data.get(
                    "role_name",
                    ""
                ).strip()
            )

            description = (
                form_data.get(
                    "description",
                    ""
                ).strip()
            )

            # ==================================
            # Validate Required
            # ==================================

            result = self.validate(
                self.validate_required(
                    role_code,
                    "Role Code",
                ),

                self.validate_required(
                    role_name,
                    "Role Name",
                ),
            )

            if not result.success:

                return result

            # ==================================
            # Validate Duplicate Role Code
            # ==================================

            duplicate = (
                self.repository.get_by_code(
                    role_code
                )
            )

            if (
                duplicate
                and duplicate.id != role.id
            ):

                return self.failed(
                    "Role Code already exists."
                )

            # ==================================
            # Validate Duplicate Role Name
            # ==================================

            duplicate = (
                self.repository.get_by_name(
                    role_name
                )
            )

            if (
                duplicate
                and duplicate.id != role.id
            ):

                return self.failed(
                    "Role Name already exists."
                )

            # ==================================
            # Update
            # ==================================

            with TransactionManager():

                role.role_code = (
                    role_code
                )

                role.role_name = (
                    role_name
                )

                role.description = (
                    description
                    if description
                    else None
                )

                role.updated_by = (
                    updated_by
                )

                self.repository.update(
                    role
                )

            return self.success(
                "Role updated successfully.",
                role,
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
        role_id,
        deleted_by=None,
    ):

        try:

            # ==================================
            # Get Role
            # ==================================

            role = (
                self.repository.get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==================================
            # Delete
            # ==================================

            with TransactionManager():

                role.updated_by = (
                    deleted_by
                )

                self.repository.delete(
                    role
                )

            return self.success(
                "Role deleted successfully."
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )