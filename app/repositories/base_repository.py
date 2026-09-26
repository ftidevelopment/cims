from app.extensions import db
from sqlalchemy import or_


class BaseRepository:

    def __init__(self, model):
        self.model = model

    def _has_soft_delete(self):
        return "is_active" in self.model.__table__.columns

    def get_query(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        query = self.model.query

        # Soft Delete
        if self._has_soft_delete():

            if is_active is not None:
                query = query.filter_by(
                    is_active=is_active
                )

        # Search
        if keyword and hasattr(self, "searchable_fields"):

            keyword = f"%{keyword}%"

            query = query.filter(
                or_(
                    *[
                        field.ilike(keyword)
                        for field in self.searchable_fields
                    ]
                )
            )

        # Sorting
        if (
            sort_by
            and hasattr(self, "sortable_fields")
            and sort_by in self.sortable_fields
        ):

            column = self.sortable_fields[sort_by]

            if sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

        return query

    def get_all(
    self,
        keyword=None,
        is_active=True,
        page=1,
        per_page=10,
        sort_by=None,
        sort_order="asc",
    ):

        query = self.get_query(
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def get_by_id(self, entity_id):
        query = self.model.query.filter_by(id=entity_id)

        if self._has_soft_delete():
            query = query.filter_by(is_active=True)

        return query.first()

    def get_first_by(self, **filters):

        query = self.model.query.filter_by(**filters)

        if self._has_soft_delete():
            query = query.filter_by(is_active=True)

        return query.first()

    def create(self, entity):
        db.session.add(entity)

    def update(self, entity):
        db.session.add(entity)

    def delete(self, entity):

        if self._has_soft_delete():
            entity.is_active = False
            db.session.add(entity)
        else:
            db.session.delete(entity)

    def get_export_data(
        self,
        keyword=None,
        is_active=True,
        sort_by=None,
        sort_order="asc",
    ):

        query = self.get_query(
            keyword=keyword,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return query.all()

    def exists(self, entity_id):
        return self.get_by_id(entity_id) is not None

    def count(self):
        return self.get_query().count()

    def get_first(self):
        return self.get_query().first()

    def get_active(self):
        if not self._has_soft_delete():
            return self.model.query.all()

        return (
            self.model.query
            .filter_by(is_active=True)
            .all()
        )

    def get_inactive(self):
        if not self._has_soft_delete():
            return []

        return (
            self.model.query
            .filter_by(is_active=False)
            .all()
        )

    def get_inactive_by_id(self, entity_id):

        if not self._has_soft_delete():
            return None

        return (
            self.model.query
            .filter_by(
                id=entity_id,
                is_active=False
            )
            .first()
        )

    def restore(self, entity_id):

        entity = self.get_inactive_by_id(entity_id)

        if not entity:
            return None

        entity.is_active = True

        return entity

    def find_by(self, **filters):

        query = self.model.query.filter_by(**filters)

        if self._has_soft_delete():
            query = query.filter_by(is_active=True)

        return query.all()

    def exists_by(self, **filters):

        query = self.model.query.filter_by(**filters)

        if self._has_soft_delete():
            query = query.filter_by(is_active=True)

        return query.first() is not None


    def delete_by(self, **filters):

        entities = self.find_by(**filters)

        for entity in entities:
            self.delete(entity)

    def get_last_by(self, column, prefix=None):

            query = self.model.query

            if prefix:
                query = query.filter(
                    column.like(f"{prefix}%")
                )

            return (
                query
                .order_by(column.desc())
                .first()
            )