from app.core.service_result import ServiceResult


class BaseService:
    """
    Base class untuk seluruh service di CIMS.
    """

    def success(self, message="", data=None):

        return ServiceResult(
            success=True,
            message=message,
            data=data,
        )

    def failed(self, message="", errors=None):

        result = ServiceResult(
            success=False,
            message=message,
        )

        if errors:
            result.errors = errors

        return result

    def handle_exception(self, exception):
        raise

    def validate_unique(
        self,
        value,
        exists_function,
        field_name,
    ):

        if not value:
            return self.success()

        if exists_function(value):
            return self.failed(
                f"{field_name} already exists."
            )

        return self.success()

    # ==========================================
# Validate Entity Exists
# ==========================================

    def validate_exists(
        self,
        entity,
        entity_name,
    ):

        if entity is None:

            raise ValueError(
                f"{entity_name} not found."
            )

        return entity

    def validate_required(
        self,
        value,
        field_name,
    ):

        if value is None:
            return self.failed(
                f"{field_name} is required."
            )

        if isinstance(value, str):

            if not value.strip():
                return self.failed(
                    f"{field_name} is required."
                )

        return self.success()


    def validate_positive_number(
        self,
        value,
        field_name,
    ):

        if value is None:
            return self.success()

        if value < 0:
            return self.failed(
                f"{field_name} cannot be negative."
            )

        return self.success()

    def validate(
    self,
        *results
    ):

        for result in results:

            if not result.success:
                return result

        return self.success()