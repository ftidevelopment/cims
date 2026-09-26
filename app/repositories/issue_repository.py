from app.models.issue import Issue
from app.repositories.base_repository import BaseRepository
from app.extensions import db


class IssueRepository(BaseRepository):

    model = Issue

    searchable_fields = [
        Issue.issue_no,
        Issue.module,
        Issue.category,
        Issue.priority,
        Issue.status,
        Issue.description,
    ]

    sortable_fields = {
        "issue_no": Issue.issue_no,
        "module": Issue.module,
        "category": Issue.category,
        "priority": Issue.priority,
        "status": Issue.status,
        "created_at": Issue.created_at,
        "updated_at": Issue.updated_at,
    }

    def __init__(self):
        super().__init__(Issue)

    # ======================================================
    # GET BY ISSUE NO
    # ======================================================

    def get_by_issue_no(self, issue_no):

        return self.get_first_by(
            issue_no=issue_no
        )

    # ======================================================
    # GET BY STATUS
    # ======================================================

    def get_by_status(self, status):

        return (
            self.model.query
            .filter(
                self.model.status == status,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY REQUESTOR
    # ======================================================

    def get_by_requestor(self, employee_id):

        return (
            self.model.query
            .filter(
                self.model.requestor_employee_id == employee_id,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY DEVELOPER
    # ======================================================

    def get_by_developer(self, employee_id):

        return (
            self.model.query
            .filter(
                self.model.developer_employee_id == employee_id,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY PRIORITY
    # ======================================================

    def get_by_priority(self, priority):

        return (
            self.model.query
            .filter(
                self.model.priority == priority,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY MODULE
    # ======================================================

    def get_by_module(self, module):

        return (
            self.model.query
            .filter(
                self.model.module == module,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY CATEGORY
    # ======================================================

    def get_by_category(self, category):

        return (
            self.model.query
            .filter(
                self.model.category == category,
                self.model.is_active.is_(True),
            )
            .order_by(
                self.model.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # OPEN ISSUES
    # ======================================================

    def get_open_issues(self):

        return self.get_by_status(
            "OPEN"
        )

    # ======================================================
    # IN PROGRESS ISSUES
    # ======================================================

    def get_in_progress_issues(self):

        return self.get_by_status(
            "IN_PROGRESS"
        )

    # ======================================================
    # FINISHED ISSUES
    # ======================================================

    def get_finished_issues(self):

        return self.get_by_status(
            "FINISH"
        )

    # ======================================================
    # CLOSED ISSUES
    # ======================================================

    def get_closed_issues(self):

        return self.get_by_status(
            "CLOSE"
        )