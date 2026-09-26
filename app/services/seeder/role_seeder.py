from app.core.choices.role import (
    ROLE,
)

from app.models.role import (
    Role,
)

from app.repositories.role_repository import (
    RoleRepository,
)

from app.core.transaction_manager import (
    TransactionManager,
)


class RoleSeeder:

    def __init__(self):

        self.repository = (
            RoleRepository()
        )

    # ==========================================
    # Seed Default Roles
    # ==========================================

    def seed(self):

        created = 0

        with TransactionManager():

            for role_code, role_name in ROLE:

                if self.repository.get_by_code(
                    role_code
                ):
                    continue

                role = Role()

                role.role_code = role_code

                role.role_name = role_name

                role.description = (
                    f"{role_name} Role"
                )

                role.created_by = (
                    "SYSTEM"
                )

                self.repository.create(
                    role
                )

                created += 1

        return created