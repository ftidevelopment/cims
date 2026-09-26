from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    login_required,
    current_user,
)

from app.core.authorization import permission_required
from app.services.permission_service import (
    PermissionService,
)


permission_bp = Blueprint(
    "permission",
    __name__,
    url_prefix="/permissions",
)


permission_service = PermissionService()


# ==========================================
# Permission List
# ==========================================

@permission_bp.route("/")
@login_required
@permission_required("PERMISSION_VIEW")
def index():

    # ==========================================
    # Search
    # ==========================================

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    # ==========================================
    # Pagination
    # ==========================================

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    # ==========================================
    # Sorting
    # ==========================================

    sort = request.args.get(
        "sort",
        "permission_name",
    )

    order = request.args.get(
        "order",
        "asc",
    )

    # ==========================================
    # Active Status
    # ==========================================

    is_active = request.args.get(
        "is_active",
        "true",
    )

    if is_active == "true":

        active_filter = True

    elif is_active == "false":

        active_filter = False

    else:

        active_filter = None

    # ==========================================
    # Get Data
    # ==========================================

    permissions = permission_service.get_all(
        keyword=keyword,
        is_active=active_filter,
        page=page,
        per_page=10,
        sort_by=sort,
        sort_order=order,
    )

    # ==========================================
    # Render
    # ==========================================

    return render_template(
        "permission/list.html",
        permissions=permissions,
        keyword=keyword,
        is_active=is_active,
        sort_by=sort,
        sort_order=order,
    )


# ==========================================
# Create Permission
# ==========================================

@permission_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("PERMISSION_CREATE")
def create():

    if request.method == "POST":

        # ======================================
        # Form Data
        # ======================================

        form_data = {

            "permission_code":
                request.form.get(
                    "permission_code",
                    "",
                ),

            "permission_name":
                request.form.get(
                    "permission_name",
                    "",
                ),

            "description":
                request.form.get(
                    "description",
                    "",
                ),
        }

        # ======================================
        # Service
        # ======================================

        result = permission_service.create(
            form_data=form_data,
            created_by=current_user.id,
        )

        # ======================================
        # Result
        # ======================================

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "permission.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    # ==========================================
    # Form
    # ==========================================

    return render_template(
        "permission/form.html",
    )


# ==========================================
# Edit Permission
# ==========================================

@permission_bp.route(
    "/edit/<int:permission_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("PERMISSION_EDIT")
def edit(permission_id):

    # ==========================================
    # Get Permission
    # ==========================================

    permission = (
        permission_service
        .get_by_id(
            permission_id
        )
    )

    if not permission:

        flash(
            "Permission not found.",
            "danger",
        )

        return redirect(
            url_for(
                "permission.index"
            )
        )

    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        # ======================================
        # Form Data
        # ======================================

        form_data = {

            "permission_code":
                request.form.get(
                    "permission_code",
                    "",
                ),

            "permission_name":
                request.form.get(
                    "permission_name",
                    "",
                ),

            "description":
                request.form.get(
                    "description",
                    "",
                ),
        }

        # ======================================
        # Service
        # ======================================

        result = permission_service.update(

            permission_id=permission_id,

            form_data=form_data,

            updated_by=current_user.id,
        )

        # ======================================
        # Result
        # ======================================

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "permission.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    # ==========================================
    # Form
    # ==========================================

    return render_template(
        "permission/form.html",
        permission=permission,
    )


# ==========================================
# Delete Permission
# ==========================================

@permission_bp.route(
    "/<int:permission_id>/delete",
    methods=["POST"],
)
@login_required
@permission_required("PERMISSION_DELETE")
def delete(permission_id):

    result = permission_service.delete(

        permission_id=permission_id,

        deleted_by=current_user.id,
    )

    flash(
        result.message,

        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for(
            "permission.index"
        )
    )


# ==========================================
# Restore Permission
# ==========================================

@permission_bp.route(
    "/<int:permission_id>/restore",
    methods=["POST"],
)
@login_required
def restore(permission_id):

    result = permission_service.restore(

        permission_id=permission_id,

        updated_by=current_user.id,
    )

    flash(
        result.message,

        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for(
            "permission.index"
        )
    )