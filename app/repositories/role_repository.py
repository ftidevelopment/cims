from app.models.role import (
    Role,
)

from app.repositories.base_repository import (
    BaseRepository,
)


class RoleRepository(
    BaseRepository
):

    searchable_fields = [

        Role.role_code,

        Role.role_name,

        Role.description,

    ]

    sortable_fields = {

        "role_code":
            Role.role_code,

        "role_name":
            Role.role_name,

        "created_at":
            Role.created_at,

    }

    def __init__(self):

        super().__init__(
            Role
        )

    # ==========================================
    # Find
    # ==========================================

    def get_by_code(
        self,
        role_code,
    ):

        return self.get_first_by(
            role_code=role_code,
        )

    def get_by_name(
        self,
        role_name,
    ):

        return self.get_first_by(
            role_name=role_name,
        )

    # ==========================================
    # Exists
    # ==========================================

    def exists_code(
        self,
        role_code,
    ):

        return self.exists_by(
            role_code=role_code,
        )

    def exists_name(
        self,
        role_name,
    ):

        return self.exists_by(
            role_name=role_name,
        )