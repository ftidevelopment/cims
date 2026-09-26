from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from app.core.authorization import permission_required
from app.services.role_service import (
    RoleService,
)
from app.services.user_service import UserService
from flask_login import login_required
from io import BytesIO

user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/users",
)

service = UserService()
role_service = RoleService()

@user_bp.route("/")
@login_required
@permission_required("USER_VIEW")
def index():

    keyword = request.args.get(
        "keyword",
        ""
    )


    page = request.args.get(
        "page",
        1,
        type=int,
    )

    sort = request.args.get(
        "sort",
        "created_at",
    )

    order = request.args.get(
        "order",
        "desc",
    )

    users = service.get_all(
        keyword=keyword,        
        page=page,
        sort_by=sort,
        sort_order=order,
    )

    return render_template(
        "user/list.html",
        keyword=keyword,
        users=users,       
        sort_by=sort,
        sort_order=order,
    )

@user_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@permission_required("USER_CREATE")
def create():

    employees = service.get_available_employees()

    roles = role_service.get_all(
        per_page=1000,
    ).items

    if request.method == "POST":

        employee_id = request.form.get(
            "employee_id",
            type=int,
        )

        username = request.form.get(
            "username",
            ""
        ).strip()

        role_id = request.form.get(
            "role_id",
            type=int,
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if password != confirm_password:

            flash(
                "Password confirmation does not match.",
                "danger",
            )

            return render_template(
                "user/form.html",
                employees=employees,
                roles=roles,
            )

        try:

            service.create(
                employee_id=employee_id,
                role_id=role_id,
                username=username,
                password=password,
            )

            flash(
                "User created successfully.",
                "success",
            )

            return redirect(
                url_for("user.index")
            )

        except ValueError as e:

            flash(str(e), "danger")

        except Exception as e:

            print(
                "CREATE USER ERROR:",
                repr(e),
            )

            flash(
                str(e),
                "danger",
            )

    return render_template(
        "user/form.html",
        employees=employees,
        roles=roles,
    )

@user_bp.route(
    "/edit/<int:user_id>",
    methods=["GET", "POST"],
)
@login_required
@permission_required("USER_EDIT")
def edit(user_id):

    user = service.get_by_id(
        user_id
    )

    if not user:

        flash(
            "User not found.",
            "danger",
        )

        return redirect(
            url_for("user.index")
        )

    # ==========================================
    # Employees
    # ==========================================

    employees = (
        service.get_available_employees()
    )

    # Tambahkan employee milik user
    # agar tetap muncul di dropdown

    if user.employee not in employees:

        employees.append(
            user.employee
        )

    # ==========================================
    # Roles
    # ==========================================

    roles = (
        role_service
        .get_all(
            per_page=1000,
        )
        .items
    )

    # ==========================================
    # POST
    # ==========================================

    if request.method == "POST":

        employee_id = request.form.get(
            "employee_id",
            type=int,
        )

        role_id = request.form.get(
            "role_id",
            type=int,
        )

        username = request.form.get(
            "username",
            ""
        ).strip()

        try:

            service.update(
                user=user,
                employee_id=employee_id,
                role_id=role_id,
                username=username,
            )

            flash(
                "User updated successfully.",
                "success",
            )

            return redirect(
                url_for("user.index")
            )

        except ValueError as e:

            flash(
                str(e),
                "danger",
            )

        except Exception as e:

            print(
                "UPDATE USER ERROR:",
                repr(e),
            )

            flash(
                str(e),
                "danger",
            )

    # ==========================================
    # Form
    # ==========================================

    return render_template(
        "user/form.html",
        user=user,
        employees=employees,
        roles=roles,
    )

@user_bp.route(
    "/delete/<int:user_id>",
    methods=["POST"],
)
@login_required
@permission_required("USER_DELETE")
def delete(user_id):

    user = service.get_by_id(user_id)

    if not user:

        flash(
            "User not found.",
            "danger",
        )

    else:

        service.delete(user)

        flash(
            "User deleted successfully.",
            "success",
        )

    return redirect(
        url_for("user.index")
    )

@user_bp.route(
    "/restore/<int:user_id>",
    methods=["POST"],
)
@login_required
def restore(user_id):

    result = service.restore(user_id)

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for("user.index")
    )



@user_bp.route("/export")
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "created_at",
    )

    order = request.args.get(
        "order",
        "desc",
    )

    workbook = service.export_excel(
        keyword=keyword,
        sort=sort,
        order=order,
    )

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="User.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

@user_bp.route("/reset-password/<int:id>", methods=["POST"])
@login_required
def reset_password(id):

    user = service.get_by_id(id)

    if not user:
        flash(
            "User not found.",
            "danger",
        )
        return redirect(url_for("user.index"))

    result = service.reset_password(
        user_id=id,
        new_password="12345678",
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(url_for("user.index"))

@user_bp.route("/unlock/<int:id>", methods=["POST"])
@login_required
def unlock(id):

    result = service.unlock(id)

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(url_for("user.index"))