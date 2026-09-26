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
from app.services.role_service import (
    RoleService,
)
from app.services.permission_service import (
    PermissionService,
)

from app.services.role_permission_service import (
    RolePermissionService,
)


role_bp = Blueprint(
    "role",
    __name__,
    url_prefix="/roles",
)


role_service = RoleService()
permission_service = PermissionService()

role_permission_service = (
    RolePermissionService()
)


# ==========================================
# Role List
# ==========================================

@role_bp.route("/")
@login_required
@permission_required("ROLE_VIEW")
def index():

    keyword = request.args.get(
        "keyword",
        "",
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    sort = request.args.get(
        "sort",
        "role_name",
    )

    order = request.args.get(
        "order",
        "asc",
    )

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

    roles = role_service.get_all(
        keyword=keyword,
        is_active=active_filter,
        page=page,
        per_page=10,
        sort_by=sort,
        sort_order=order,
    )

    return render_template(
        "role/list.html",
        roles=roles,
        keyword=keyword,
        is_active=is_active,
        sort_by=sort,
        sort_order=order,
    )


# ==========================================
# Create Role
# ==========================================

@role_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("ROLE_CREATE")
def create():

    if request.method == "POST":

        form_data = {
            "role_code": request.form.get(
                "role_code",
                "",
            ),

            "role_name": request.form.get(
                "role_name",
                "",
            ),

            "description": request.form.get(
                "description",
                "",
            ),
        }

        result = role_service.create(
            form_data=form_data,
            created_by=current_user.id,
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for("role.index")
            )

        flash(
            result.message,
            "danger",
        )

    return render_template(
        "role/form.html",
    )


# ==========================================
# Edit Role
# ==========================================

@role_bp.route(
    "/edit/<int:role_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("ROLE_EDIT")
def edit(role_id):

    # ==========================================
    # Get Role
    # ==========================================

    role = role_service.get_by_id(
        role_id
    )

    if not role:

        flash(
            "Role not found.",
            "danger",
        )

        return redirect(
            url_for(
                "role.index"
            )
        )

    # ==========================================
    # Get Active Permissions
    # ==========================================

    permissions = (
        permission_service.get_all(
            is_active=True,
            page=1,
            per_page=1000,
            sort_by="permission_name",
            sort_order="asc",
        )
    )

    permissions = permissions.items

    # ==========================================
    # Get Current Role Permissions
    # ==========================================

    selected_permission_ids = (
        role_permission_service
        .get_permission_ids_by_role(
            role_id
        )
    )

    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        # ======================================
        # Role Form Data
        # ======================================

        form_data = {

            "role_code":
                request.form.get(
                    "role_code",
                    "",
                ),

            "role_name":
                request.form.get(
                    "role_name",
                    "",
                ),

            "description":
                request.form.get(
                    "description",
                    "",
                ),
        }

        # ======================================
        # Permission IDs
        # ======================================

        permission_ids = (
            request.form.getlist(
                "permission_ids"
            )
        )

        try:

            permission_ids = [
                int(permission_id)
                for permission_id
                in permission_ids
            ]

        except ValueError:

            flash(
                "Invalid permission selected.",
                "danger",
            )

            return render_template(
                "role/form.html",
                role=role,
                permissions=permissions,
                selected_permission_ids=selected_permission_ids,
            )

        # ======================================
        # Update Role
        # ======================================

        result = role_service.update(

            role_id=role_id,

            form_data=form_data,

            updated_by=current_user.id,
        )

        if not result.success:

            flash(
                result.message,
                "danger",
            )

            return render_template(
                "role/form.html",
                role=role,
                permissions=permissions,
                selected_permission_ids=selected_permission_ids,
            )

        # ======================================
        # Update Role Permissions
        # ======================================

        permission_result = (
            role_permission_service
            .assign_permissions(

                role_id=role_id,

                permission_ids=permission_ids,

                updated_by=current_user.id,
            )
        )

        if not permission_result.success:

            flash(
                permission_result.message,
                "danger",
            )

            return render_template(
                "role/form.html",
                role=role,
                permissions=permissions,
                selected_permission_ids=permission_ids,
            )

        # ======================================
        # Success
        # ======================================

        flash(
            "Role and permissions updated successfully.",
            "success",
        )

        return redirect(
            url_for(
                "role.index"
            )
        )

    # ==========================================
    # GET
    # ==========================================

    return render_template(
        "role/form.html",
        role=role,
        permissions=permissions,
        selected_permission_ids=selected_permission_ids,
    )


# ==========================================
# Delete Role
# ==========================================

@role_bp.route(
    "/<int:role_id>/delete",
    methods=["POST"],
)
@login_required
@permission_required("ROLE_DELETE")
def delete(role_id):

    result = role_service.delete(
        role_id=role_id,
        deleted_by=current_user.id,
    )

    flash(
        result.message,
        "success"
        if result.success
        else "danger",
    )

    return redirect(
        url_for("role.index")
    )