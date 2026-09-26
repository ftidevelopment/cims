from app.repositories.role_permission_repository import (
    RolePermissionRepository,
)

from app.repositories.role_repository import (
    RoleRepository,
)

from app.repositories.permission_repository import (
    PermissionRepository,
)

from app.models.role_permission import (
    RolePermission,
)

from app.services.base_service import (
    BaseService,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class RolePermissionService(
    BaseService
):

    def __init__(self):

        super().__init__()

        self.repository = (
            RolePermissionRepository()
        )

        self.role_repository = (
            RoleRepository()
        )

        self.permission_repository = (
            PermissionRepository()
        )

    # ==========================================
    # Get By Role
    # ==========================================

    def get_by_role_id(
        self,
        role_id,
    ):

        return (
            self.repository
            .get_by_role_id(
                role_id
            )
        )

    # ==========================================
    # Get Permission IDs By Role
    # ==========================================

    def get_permission_ids_by_role(
        self,
        role_id,
    ):

        return (
            self.repository
            .get_permission_ids_by_role(
                role_id
            )
        )

    # ==========================================
    # Assign Permissions
    # ==========================================

    def assign_permissions(
        self,
        role_id,
        permission_ids,
        updated_by=None,
    ):

        try:

            # ==================================
            # Validate Role
            # ==================================

            role = (
                self.role_repository
                .get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==================================
            # Normalize Permission IDs
            # ==================================

            if permission_ids is None:

                permission_ids = []

            permission_ids = list(
                dict.fromkeys(
                    int(permission_id)
                    for permission_id
                    in permission_ids
                )
            )

            # ==================================
            # Validate Permissions
            # ==================================

            permissions = []

            for permission_id in permission_ids:

                permission = (
                    self.permission_repository
                    .get_by_id(
                        permission_id
                    )
                )

                self.validate_exists(
                    permission,
                    "Permission",
                )

                # --------------------------------
                # Check Active
                # --------------------------------

                if not permission.is_active:

                    return self.failed(
                        f"Permission "
                        f"'{permission.permission_name}' "
                        f"is inactive."
                    )

                permissions.append(
                    permission
                )

            # ==================================
            # Save
            # ==================================

            with TransactionManager():

                # --------------------------------
                # Delete Existing Relations
                # --------------------------------

                self.repository.delete_by_role_id(
                    role_id
                )

                # --------------------------------
                # Create New Relations
                # --------------------------------

                for permission in permissions:

                    relation = (
                        RolePermission()
                    )

                    relation.role_id = (
                        role_id
                    )

                    relation.permission_id = (
                        permission.id
                    )

                    relation.updated_by = (
                        updated_by
                    )

                    self.repository.create(
                        relation
                    )

            return self.success(
                "Role permissions updated successfully.",
                role,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Add Single Permission
    # ==========================================

    def add_permission(
        self,
        role_id,
        permission_id,
        updated_by=None,
    ):

        try:

            # ==================================
            # Validate Role
            # ==================================

            role = (
                self.role_repository
                .get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==================================
            # Validate Permission
            # ==================================

            permission = (
                self.permission_repository
                .get_by_id(
                    permission_id
                )
            )

            self.validate_exists(
                permission,
                "Permission",
            )

            # ==================================
            # Check Active
            # ==================================

            if not permission.is_active:

                return self.failed(
                    "Permission is inactive."
                )

            # ==================================
            # Check Existing Relation
            # ==================================

            exists = (
                self.repository
                .exists_relation(
                    role_id=role_id,
                    permission_id=permission_id,
                )
            )

            if exists:

                return self.failed(
                    "Permission is already assigned "
                    "to this role."
                )

            # ==================================
            # Create Relation
            # ==================================

            with TransactionManager():

                relation = RolePermission()

                relation.role_id = (
                    role_id
                )

                relation.permission_id = (
                    permission_id
                )

                relation.updated_by = (
                    updated_by
                )

                self.repository.create(
                    relation
                )

            return self.success(
                "Permission assigned successfully.",
                relation,
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )

    # ==========================================
    # Remove Single Permission
    # ==========================================

    def remove_permission(
        self,
        role_id,
        permission_id,
    ):

        try:

            # ==================================
            # Validate Role
            # ==================================

            role = (
                self.role_repository
                .get_by_id(
                    role_id
                )
            )

            self.validate_exists(
                role,
                "Role",
            )

            # ==================================
            # Get Relation
            # ==================================

            relation = (
                self.repository
                .get_by_role_permission(
                    role_id=role_id,
                    permission_id=permission_id,
                )
            )

            if not relation:

                return self.failed(
                    "Permission is not assigned "
                    "to this role."
                )

            # ==================================
            # Delete Relation
            # ==================================

            with TransactionManager():

                self.repository.delete(
                    relation
                )

            return self.success(
                "Permission removed successfully."
            )

        except Exception as ex:

            return self.handle_exception(
                ex
            )