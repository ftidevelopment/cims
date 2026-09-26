from app.models.problem_category import ProblemCategory
from app.repositories.base_repository import BaseRepository


class ProblemCategoryRepository(BaseRepository):

    model = ProblemCategory

    searchable_fields = [
        ProblemCategory.problem_category_code,
        ProblemCategory.problem_category_name,
        ProblemCategory.description,
    ]

    sortable_fields = {
        "problem_category_code": ProblemCategory.problem_category_code,
        "problem_category_name": ProblemCategory.problem_category_name,
        "description": ProblemCategory.description,
        "created_at": ProblemCategory.created_at,
    }

    def __init__(self):
        super().__init__(ProblemCategory)

    def get_by_code(
        self,
        problem_category_code: str,
    ):

        return self.get_first_by(
            problem_category_code=problem_category_code,
        )

    def get_by_name(
        self,
        problem_category_name: str,
    ):

        return self.get_first_by(
            problem_category_name=problem_category_name,
        )

    def exists_by_code(self, problem_category_code: str) -> bool:
        return self.get_by_code(problem_category_code) is not None

    def exists_by_name(self, problem_category_name: str) -> bool:
        return self.get_by_name(problem_category_name) is not None