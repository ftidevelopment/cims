from flask_login import current_user


def has_permission(permission_code):

    if not current_user.is_authenticated:
        return False

    return current_user.has_permission(
        permission_code
    )


def has_any_permission(*permission_codes):

    if not current_user.is_authenticated:
        return False

    return current_user.has_any_permission(
        *permission_codes
    )


def has_all_permissions(*permission_codes):

    if not current_user.is_authenticated:
        return False

    return current_user.has_all_permissions(
        *permission_codes
    )