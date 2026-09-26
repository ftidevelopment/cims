from app.repositories.permission_repository import (
    PermissionRepository,
)

from app.models.permission import (
    Permission,
)

from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class PermissionService(
    BaseService
):

    def __init__(self):

        super().__init__()

        self.repository = (
            PermissionRepository()
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
    # Get By ID
    # ==========================================

    def get_by_id(
        self,
        permission_id,
    ):

        return self.repository.get_by_id(
            permission_id
        )

    # ==========================================
    # Get By Code
    # ==========================================

    def get_by_code(
        self,
        permission_code,
    ):

        return self.repository.get_by_code(
            permission_code
        )

    # ==========================================
    # Get By Name
    # ==========================================

    def get_by_name(
        self,
        permission_name,
    ):

        return self.repository.get_by_name(
            permission_name
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

            permission_code = (
                form_data.get(
                    "permission_code",
                    ""
                ).strip().upper()
            )

            permission_name = (
                form_data.get(
                    "permission_name",
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
                    permission_code,
                    "Permission Code",
                ),
                self.validate_required(
                    permission_name,
                    "Permission Name",
                ),
            )

            if not result.success:

                return result

            # ==================================
            # Validate Duplicate Code
            # ==================================

            if self.repository.exists_code(
                permission_code
            ):

                return self.failed(
                    "Permission Code already exists."
                )

            # ==================================
            # Validate Duplicate Name
            # ==================================

            if self.repository.exists_name(
                permission_name
            ):

                return self.failed(
                    "Permission Name already exists."
                )

            # ==================================
            # Create
            # ==================================

            with TransactionManager():

                permission = Permission()

                permission.permission_code = (
                    permission_code
                )

                permission.permission_name = (
                    permission_name
                )

                permission.description = (
                    description
                    if description
                    else None
                )

                permission.created_by = (
                    created_by
                )

                self.repository.create(
                    permission
                )

            return self.success(
                "Permission created successfully.",
                permission,
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
        permission_id,
        form_data,
        updated_by=None,
    ):

        try:

            permission = (
                self.repository.get_by_id(
                    permission_id
                )
            )

            result = self.validate_exists(
                permission,
                "Permission",
            )

            if not result.success:

                return result

            permission_code = (
                form_data.get(
                    "permission_code",
                    ""
                ).strip().upper()
            )

            permission_name = (
                form_data.get(
                    "permission_name",
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
                    permission_code,
                    "Permission Code",
                ),
                self.validate_required(
                    permission_name,
                    "Permission Name",
                ),
            )

            if not result.success:

                return result

            # ==================================
            # Validate Duplicate Code
            # ==================================

            duplicate = (
                self.repository.get_by_code(
                    permission_code
                )
            )

            if (
                duplicate
                and duplicate.id != permission.id
            ):

                return self.failed(
                    "Permission Code already exists."
                )

            # ==================================
            # Validate Duplicate Name
            # ==================================

            duplicate = (
                self.repository.get_by_name(
                    permission_name
                )
            )

            if (
                duplicate
                and duplicate.id != permission.id
            ):

                return self.failed(
                    "Permission Name already exists."
                )

            # ==================================
            # Update
            # ==================================

            with TransactionManager():

                permission.permission_code = (
                    permission_code
                )

                permission.permission_name = (
                    permission_name
                )

                permission.description = (
                    description
                    if description
                    else None
                )

                permission.updated_by = (
                    updated_by
                )

                self.repository.update(
                    permission
                )

            return self.success(
                "Permission updated successfully.",
                permission,
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
        permission_id,
        deleted_by=None,
    ):

        try:

            permission = (
                self.repository.get_by_id(
                    permission_id
                )
            )

            result = self.validate_exists(
                permission,
                "Permission",
            )

            if not result.success:

                return result

            with TransactionManager():

                permission.updated_by = (
                    deleted_by
                )

                self.repository.delete(
                    permission
                )

            return self.success(
                "Permission deleted successfully."
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Restore
    # ==========================================

    def restore(
        self,
        permission_id,
        updated_by=None,
    ):

        try:

            permission = (
                self.repository
                .get_inactive_by_id(
                    permission_id
                )
            )

            result = self.validate_exists(
                permission,
                "Permission",
            )

            if not result.success:

                return result

            with TransactionManager():

                permission.is_active = True

                permission.updated_by = (
                    updated_by
                )

                self.repository.update(
                    permission
                )

            return self.success(
                "Permission restored successfully.",
                permission,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )