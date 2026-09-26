from app.models.role_permission import (
    RolePermission,
)
from app.extensions import db
from app.repositories.base_repository import (
    BaseRepository,
)


class RolePermissionRepository(
    BaseRepository
):

    def __init__(self):

        super().__init__(
            RolePermission
        )

    # ==========================================
    # Find By Role
    # ==========================================

    def get_by_role_id(
        self,
        role_id,
    ):

        return (
            self.model.query
            .filter_by(
                role_id=role_id,
            )
            .all()
        )

    # ==========================================
    # Find By Permission
    # ==========================================

    def get_by_permission_id(
        self,
        permission_id,
    ):

        return (
            self.model.query
            .filter_by(
                permission_id=permission_id,
            )
            .all()
        )

    # ==========================================
    # Find Specific Relation
    # ==========================================

    def get_by_role_permission(
        self,
        role_id,
        permission_id,
    ):

        return (
            self.model.query
            .filter_by(
                role_id=role_id,
                permission_id=permission_id,
            )
            .first()
        )

    # ==========================================
    # Exists
    # ==========================================

    def exists_relation(
        self,
        role_id,
        permission_id,
    ):

        return (
            self.get_by_role_permission(
                role_id=role_id,
                permission_id=permission_id,
            )
            is not None
        )

    # ==========================================
    # Get Permission IDs By Role
    # ==========================================

    def get_permission_ids_by_role(
        self,
        role_id,
    ):

        relations = (
            self.get_by_role_id(
                role_id
            )
        )

        return [
            relation.permission_id
            for relation in relations
        ]


    # ==========================================
    # Hard Delete By Role
    # ==========================================

    def delete_by_role_id(
        self,
        role_id,
    ):

        relations = (
            self.get_by_role_id(
                role_id
            )
        )

        for relation in relations:

            db.session.delete(
                relation
            )

        return len(relations)

    # ==========================================
    # Delete Specific Relation
    # ==========================================

    def delete_relation(
        self,
        role_id,
        permission_id,
    ):

        relation = (
            self.get_by_role_permission(
                role_id=role_id,
                permission_id=permission_id,
            )
        )

        if not relation:

            return False

        self.delete(
            relation
        )

        return True