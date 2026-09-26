from app.models.problem_pic import (
    ProblemPIC,
)

from app.repositories.base_repository import (
    BaseRepository,
)

from app.extensions import db


class ProblemPICRepository(
    BaseRepository
):

    sortable_fields = {

        "employee_id":
            ProblemPIC.employee_id,

        "status":
            ProblemPIC.status,

        "created_at":
            ProblemPIC.created_at,

    }

    def __init__(self):

        super().__init__(
            ProblemPIC
        )

    # ==========================================
    # Get By Problem
    # ==========================================

    def get_by_problem_id(
        self,
        problem_id,
    ):

        return self.find_by(
            problem_id=problem_id
        )

    # ==========================================
    # Hard Delete By Problem
    # ==========================================

    def delete_by_problem_id(
        self,
        problem_id,
    ):
        """
        Hard delete all Problem PIC records
        belonging to a Problem.
        """

        problem_pics = (
            self.get_by_problem_id(
                problem_id
            )
        )

        for problem_pic in problem_pics:

            db.session.delete(
                problem_pic
            )

        return problem_pics