from app.models.permission import (
    Permission,
)

from app.repositories.base_repository import (
    BaseRepository,
)


class PermissionRepository(
    BaseRepository
):

    searchable_fields = [

        Permission.permission_code,

        Permission.permission_name,

        Permission.description,

    ]

    sortable_fields = {

        "permission_code":
            Permission.permission_code,

        "permission_name":
            Permission.permission_name,

        "created_at":
            Permission.created_at,

    }

    def __init__(self):

        super().__init__(
            Permission
        )

    # ==========================================
    # Find
    # ==========================================

    def get_by_code(
        self,
        permission_code,
    ):

        return self.get_first_by(
            permission_code=permission_code,
        )

    def get_by_name(
        self,
        permission_name,
    ):

        return self.get_first_by(
            permission_name=permission_name,
        )

    # ==========================================
    # Exists
    # ==========================================

    def exists_code(
        self,
        permission_code,
    ):

        return self.exists_by(
            permission_code=permission_code,
        )

    def exists_name(
        self,
        permission_name,
    ):

        return self.exists_by(
            permission_name=permission_name,
        )