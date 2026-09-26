from app.models.issue_clarification import IssueClarification
from app.repositories.base_repository import BaseRepository


class IssueClarificationRepository(BaseRepository):

    model = IssueClarification

    searchable_fields = [
        IssueClarification.question,
        IssueClarification.response,
        IssueClarification.status,
    ]

    sortable_fields = {
        "requested_at": IssueClarification.requested_at,
        "responded_at": IssueClarification.responded_at,
        "status": IssueClarification.status,
        "created_at": IssueClarification.created_at,
    }

    def __init__(self):
        super().__init__(IssueClarification)

    def get_by_issue(self, issue_id):
        return (
            self.model.query
            .filter(
                self.model.issue_id == issue_id,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.requested_at.asc()
            )
            .all()
        )

    def get_open_by_issue(self, issue_id):
        return (
            self.model.query
            .filter(
                self.model.issue_id == issue_id,
                self.model.status == "OPEN",
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.requested_at.asc()
            )
            .all()
        )

    def get_by_id(self, clarification_id):
        return (
            self.model.query
            .filter(
                self.model.id == clarification_id,
                self.model.is_active.is_(True),
            )
            .first()
        )