from app.extensions import db
from app.models.problem_attachment import (
    ProblemAttachment,
)
from app.repositories.base_repository import (
    BaseRepository,
)


class ProblemAttachmentRepository(
    BaseRepository
):

    searchable_fields = [
        ProblemAttachment.original_name,
    ]

    sortable_fields = {
        "original_name":
            ProblemAttachment.original_name,
        "sort_order":
            ProblemAttachment.sort_order,
        "created_at":
            ProblemAttachment.created_at,
    }

    def __init__(self):

        super().__init__(
            ProblemAttachment
        )

    # ==========================================
    # Find
    # ==========================================

    def get_by_problem(
        self,
        problem_id,
    ):

        return (
            self.get_query(
                sort_by="sort_order",
            )
            .filter_by(
                problem_id=problem_id,
            )
            .all()
        )

    def count_by_problem(
        self,
        problem_id,
    ):

        return (
            self.get_query()
            .filter_by(
                problem_id=problem_id,
            )
            .count()
        )

    # ==========================================
    # Get
    # ==========================================

    def get_by_stored_name(
        self,
        stored_name,
    ):

        return self.get_first_by(
            stored_name=stored_name,
        )

    # ==========================================
    # Exists
    # ==========================================

    def exists_file(
        self,
        problem_id,
        original_name,
    ):

        return self.exists_by(
            problem_id=problem_id,
            original_name=original_name,
        )

    # ==========================================
    # Delete
    # ==========================================

    def delete_by_problem(
        self,
        problem_id,
    ):

        self.delete_by(
            problem_id=problem_id,
        )


    def hard_delete(
        self,
        attachment,
    ):

        db.session.delete(
            attachment
        )