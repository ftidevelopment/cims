from app.models.kaizen_category import KaizenCategory
from app.repositories.base_repository import BaseRepository


class KaizenCategoryRepository(BaseRepository):

    model = KaizenCategory

    searchable_fields = [
        KaizenCategory.kaizen_category_code,
        KaizenCategory.kaizen_category_name,
        KaizenCategory.description,
    ]

    sortable_fields = {
        "kaizen_category_code": KaizenCategory.kaizen_category_code,
        "kaizen_category_name": KaizenCategory.kaizen_category_name,
        "description": KaizenCategory.description,
        "created_at": KaizenCategory.created_at,
    }

    def __init__(self):
        super().__init__(KaizenCategory)

    def get_by_code(
        self,
        kaizen_category_code: str,
    ):

        return self.get_first_by(
            kaizen_category_code=kaizen_category_code,
        )

    def get_by_name(
        self,
        kaizen_category_name: str,
    ):

        return self.get_first_by(
            kaizen_category_name=kaizen_category_name,
        )

    def exists_by_code(
        self,
        kaizen_category_code: str,
    ) -> bool:

        return self.get_by_code(
            kaizen_category_code
        ) is not None

    def exists_by_name(
        self,
        kaizen_category_name: str,
    ) -> bool:

        return self.get_by_name(
            kaizen_category_name
        ) is not None