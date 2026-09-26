from functools import wraps

from flask import abort

from flask_login import current_user


# ==========================================================
# Permission Decorator
# ==========================================================

def permission_required(
    permission_code,
):
    """
    Restrict access to a route based on permission code.
    """

    def decorator(
        view_function
    ):

        @wraps(view_function)
        def wrapped_view(
            *args,
            **kwargs
        ):

            # ==============================================
            # Authentication Check
            # ==============================================

            if not current_user.is_authenticated:

                abort(401)

            # ==============================================
            # Permission Check
            # ==============================================

            if not current_user.has_permission(
                permission_code
            ):

                abort(403)

            # ==============================================
            # Execute View
            # ==============================================

            return view_function(
                *args,
                **kwargs
            )

        return wrapped_view

    return decorator