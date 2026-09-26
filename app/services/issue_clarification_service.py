from datetime import datetime

from app.extensions import db

from app.models.issue_clarification import IssueClarification

from app.repositories.issue_clarification_repository import (
    IssueClarificationRepository,
)

from app.repositories.issue_repository import IssueRepository

from app.services.base_service import BaseService


class IssueClarificationService(BaseService):

    def __init__(self):
        self.repository = IssueClarificationRepository()
        self.issue_repository = IssueRepository()

    # ==========================================================
    # CREATE CLARIFICATION
    # ==========================================================

    def create_clarification(
        self,
        issue_id,
        question,
        requested_by_employee_id,
        created_by=None,
    ):
        # ------------------------------------------------------
        # Validation
        # ------------------------------------------------------

        if not question or not question.strip():
            return self.failed(
                "Clarification question is required."
            )

        issue = self.issue_repository.get_by_id(issue_id)

        if not issue:
            return self.failed(
                "Issue not found."
            )

        # ------------------------------------------------------
        # Create clarification
        # ------------------------------------------------------

        clarification = IssueClarification(
            issue_id=issue_id,
            question=question.strip(),
            requested_by_employee_id=requested_by_employee_id,
            requested_at=datetime.now(),
            status="OPEN",
            created_by=created_by,
        )

        db.session.add(clarification)

        # ------------------------------------------------------
        # Commit database first
        # ------------------------------------------------------

        db.session.commit()

        # ------------------------------------------------------
        # Send notification through Celery
        # ------------------------------------------------------

        from app.tasks.notification_tasks import (
            send_issue_clarification_requested_notification,
        )

        send_issue_clarification_requested_notification.delay(
            clarification.id
        )

        # ------------------------------------------------------
        # Return success
        # ------------------------------------------------------

        return self.success(
            "Clarification request created successfully.",
            clarification,
        )

    # ==========================================================
    # RESPOND CLARIFICATION
    # ==========================================================

    def respond_clarification(
        self,
        clarification_id,
        response,
        responded_by_employee_id,
        updated_by=None,
    ):
        # ------------------------------------------------------
        # Validation
        # ------------------------------------------------------

        if not response or not response.strip():
            return self.failed(
                "Response is required."
            )

        clarification = self.repository.get_by_id(
            clarification_id
        )

        if not clarification:
            return self.failed(
                "Clarification not found."
            )

        if clarification.status != "OPEN":
            return self.failed(
                "This clarification is no longer open."
            )

        # ------------------------------------------------------
        # Update clarification
        # ------------------------------------------------------

        clarification.response = response.strip()

        clarification.responded_by_employee_id = (
            responded_by_employee_id
        )

        clarification.responded_at = datetime.now()

        # OPEN → CLOSE
        clarification.status = "CLOSE"

        clarification.updated_by = updated_by

        # ------------------------------------------------------
        # Commit database first
        # ------------------------------------------------------

        db.session.commit()

        # ------------------------------------------------------
        # Send notification through Celery
        # ------------------------------------------------------

        from app.tasks.notification_tasks import (
            send_issue_clarification_responded_notification,
        )

        send_issue_clarification_responded_notification.delay(
            clarification.id
        )

        # ------------------------------------------------------
        # Return success
        # ------------------------------------------------------

        return self.success(
            "Clarification response submitted successfully.",
            clarification,
        )

    # ==========================================================
    # GET CLARIFICATIONS BY ISSUE
    # ==========================================================

    def get_by_issue(self, issue_id):
        return self.repository.get_by_issue(issue_id)

    # ==========================================================
    # GET OPEN CLARIFICATIONS BY ISSUE
    # ==========================================================

    def get_open_by_issue(self, issue_id):
        return self.repository.get_open_by_issue(issue_id)