from app.services.base_service import BaseService
from app.core.service_result import ServiceResult
from app.core.transaction_manager import TransactionManager

from app.repositories.audit_execution_item_repository import (
    AuditExecutionItemRepository
)


class AuditExecutionItemService(BaseService):

    VALID_RESULTS = [
        "OK",
        "NG",
        "NA"
    ]

    def __init__(self):
        self.repository = AuditExecutionItemRepository()
        self.transaction = TransactionManager()

    # =========================================================
    # GET
    # =========================================================

    def get_by_id(self, item_id):
        return self.repository.get_by_id(item_id)

    def get_by_execution(self, audit_execution_id):
        return self.repository.get_by_execution(
            audit_execution_id
        )

    def get_by_result(self, audit_execution_id, result):
        return self.repository.get_by_result(
            audit_execution_id=audit_execution_id,
            result=result
        )

    def count_by_result(self, audit_execution_id, result):
        return self.repository.count_by_result(
            audit_execution_id=audit_execution_id,
            result=result
        )

    # =========================================================
    # UPDATE RESULT
    # =========================================================

    def update_result(
        self,
        item_id,
        result,
        remark=None
    ):
        try:
            item = self.repository.get_by_id(item_id)

            if not item:
                return ServiceResult(
                    success=False,
                    message="Audit Execution Item not found."
                )

            if result not in self.VALID_RESULTS:
                raise ValueError(
                    "Invalid checklist result. "
                    "Allowed values: OK, NG, NA."
                )

            item.result = result

            if remark is not None:
                item.remark = remark

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Checklist result updated successfully.",
                data=item
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to update checklist result: {ex}"
            )

    # =========================================================
    # UPDATE REMARK
    # =========================================================

    def update_remark(self, item_id, remark):
        try:
            item = self.repository.get_by_id(item_id)

            if not item:
                return ServiceResult(
                    success=False,
                    message="Audit Execution Item not found."
                )

            item.remark = remark

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Checklist remark updated successfully.",
                data=item
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to update checklist remark: {ex}"
            )

    # =========================================================
    # UPDATE MULTIPLE ITEMS
    # =========================================================

    def update_multiple(self, items_data):
        """
        items_data example:

        [
            {
                "item_id": 1,
                "result": "OK",
                "remark": "Condition is good"
            },
            {
                "item_id": 2,
                "result": "NG",
                "remark": "PPE is not complete"
            }
        ]
        """

        try:

            for data in items_data:

                item_id = data.get("item_id")
                result = data.get("result")
                remark = data.get("remark")

                item = self.repository.get_by_id(item_id)

                if not item:
                    raise ValueError(
                        f"Audit Execution Item {item_id} not found."
                    )

                if result not in self.VALID_RESULTS:
                    raise ValueError(
                        f"Invalid result for item {item_id}. "
                        "Allowed values: OK, NG, NA."
                    )

                item.result = result
                item.remark = remark

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Checklist results updated successfully."
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to update checklist results: {ex}"
            )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(self, item_id):
        try:

            item = self.repository.get_by_id(item_id)

            if not item:
                return ServiceResult(
                    success=False,
                    message="Audit Execution Item not found."
                )

            self.repository.delete(item_id)

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution Item deleted successfully."
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to delete Audit Execution Item: {ex}"
            )

    # =========================================================
    # RESTORE
    # =========================================================

    def restore(self, item_id):
        try:

            item = self.repository.restore(item_id)

            if not item:
                return ServiceResult(
                    success=False,
                    message="Audit Execution Item not found."
                )

            self.transaction.commit()

            return ServiceResult(
                success=True,
                message="Audit Execution Item restored successfully.",
                data=item
            )

        except Exception as ex:
            self.transaction.rollback()

            return ServiceResult(
                success=False,
                message=f"Failed to restore Audit Execution Item: {ex}"
            )