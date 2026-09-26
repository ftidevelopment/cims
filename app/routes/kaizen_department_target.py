from io import BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)

from flask_login import (
    login_required,
    current_user,
)

from app.services.authorization_service import (
    AuthorizationService,
)

from app.services.kaizen_department_target_service import (
    KaizenDepartmentTargetService,
)

from app.repositories.kaizen_reporting_period_repository import (
    KaizenReportingPeriodRepository,
)

from app.repositories.department_repository import (
    DepartmentRepository,
)


kaizen_department_target_bp = Blueprint(
    "kaizen_department_target",
    __name__,
    url_prefix="/kaizen_department_targets",
)


service = KaizenDepartmentTargetService()

reporting_period_repository = (
    KaizenReportingPeriodRepository()
)

department_repository = (
    DepartmentRepository()
)

authorization_service = AuthorizationService()


# ============================================================
# LIST
# ============================================================

@kaizen_department_target_bp.route("/")
@login_required
def index():

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int,
    )

    keyword = request.args.get(
        "keyword",
        "",
        type=str,
    ).strip()

    # ========================================================
    # STATUS
    # ========================================================

    status = request.args.get(
        "status",
        "active",
        type=str,
    )

    if status == "active":

        is_active = True

    elif status == "inactive":

        is_active = False

    else:

        status = "all"
        is_active = None

    # ========================================================
    # DEPARTMENT
    # ========================================================

    department_id = request.args.get(
        "department_id",
        None,
        type=int,
    )

    # ========================================================
    # SORT
    # ========================================================

    sort_by = request.args.get(
        "sort",
        "created_at",
        type=str,
    )

    sort_order = request.args.get(
        "order",
        "desc",
        type=str,
    )

    # ========================================================
    # GET DEPARTMENTS
    # ========================================================

    departments = (
        department_repository
        .get_active()
    )

    # ========================================================
    # GET DATA
    # ========================================================

    targets = service.get_all(
        keyword=keyword,
        is_active=is_active,
        department_id=department_id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "kaizen_department_target/list.html",
        targets=targets,
        keyword=keyword,
        status=status,
        department_id=department_id,
        departments=departments,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# CREATE
# ============================================================

@kaizen_department_target_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
def create():

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not authorization_service.can_create_department_target(
        user=current_user
    ):

        flash(
            "You do not have permission to create a Kaizen Department Target.",
            "danger",
        )

        return redirect(
            url_for(
                "kaizen_department_target.index"
            )
        )

    # --------------------------------------------------------
    # Get Reporting Periods
    # --------------------------------------------------------

    reporting_periods = (
        reporting_period_repository
        .get_active()
    )

    # --------------------------------------------------------
    # Get Departments
    # --------------------------------------------------------

    departments = (
        department_repository
        .get_active()
    )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        reporting_period_id = request.form.get(
            "reporting_period_id",
            type=int,
        )

        department_id = request.form.get(
            "department_id",
            type=int,
        )

        target_quantity = request.form.get(
            "target_quantity",
            type=int,
        )

        description = request.form.get(
            "description",
            "",
            type=str,
        ).strip()

        result = service.create(
            reporting_period_id=reporting_period_id,
            department_id=department_id,
            target_quantity=target_quantity,
            description=description,
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "kaizen_department_target.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    return render_template(
        "kaizen_department_target/form.html",
        target=None,
        reporting_periods=reporting_periods,
        departments=departments,
    )


# ============================================================
# EDIT
# ============================================================

@kaizen_department_target_bp.route(
    "/edit/<int:target_id>",
    methods=["GET", "POST"],
)
@login_required
def edit(target_id):

    service = KaizenDepartmentTargetService()

    target = service.get_by_id(
        target_id
    )

    if not target:

        flash(
            "Kaizen department target not found.",
            "danger",
        )

        return redirect(
            url_for(
                "kaizen_department_target.index"
            )
        )

    reporting_periods = (
        reporting_period_repository
        .get_active()
    )

    departments = (
        department_repository
        .get_active()
    )

    if request.method == "POST":

        reporting_period_id = request.form.get(
            "reporting_period_id",
            type=int,
        )

        department_id = request.form.get(
            "department_id",
            type=int,
        )

        target_quantity = request.form.get(
            "target_quantity",
            type=int,
        )

        description = request.form.get(
            "description",
            "",
            type=str,
        ).strip()

        result = service.update(
            target=target,
            reporting_period_id=reporting_period_id,
            department_id=department_id,
            target_quantity=target_quantity,
            description=description,
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "kaizen_department_target.index"
                )
            )

        flash(
            result.message,
            "danger",
        )

    return render_template(
        "kaizen_department_target/form.html",
        target=target,
        reporting_periods=reporting_periods,
        departments=departments,
    )


# ============================================================
# DELETE
# ============================================================

@kaizen_department_target_bp.route(
    "/delete/<int:target_id>",
    methods=["POST"],
)
@login_required
def delete(target_id):

    service = KaizenDepartmentTargetService()

    target = service.get_by_id(
        target_id
    )

    if not target:

        flash(
            "Kaizen department target not found.",
            "danger",
        )

        return redirect(
            url_for(
                "kaizen_department_target.index"
            )
        )

    result = service.delete(
        target
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "kaizen_department_target.index"
        )
    )


# ============================================================
# INACTIVE
# ============================================================

@kaizen_department_target_bp.route(
    "/inactive"
)
@login_required
def inactive():

    targets = service.get_inactive()

    return render_template(
        "kaizen_department_target/inactive.html",
        targets=targets,
    )


# ============================================================
# RESTORE
# ============================================================

@kaizen_department_target_bp.route(
    "/restore/<int:target_id>",
    methods=["POST"],
)
@login_required
def restore(target_id):

    result = service.restore(
        target_id
    )

    flash(
        result.message,
        "success" if result.success else "danger",
    )

    return redirect(
        url_for(
            "kaizen_department_target.index"
        )
    )


# ============================================================
# EXPORT
# ============================================================

@kaizen_department_target_bp.route(
    "/export"
)
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        "",
        type=str,
    ).strip()

    # ========================================================
    # STATUS
    # ========================================================

    status = request.args.get(
        "status",
        "active",
        type=str,
    )

    if status == "active":

        is_active = True

    elif status == "inactive":

        is_active = False

    else:

        status = "all"
        is_active = None

    # ========================================================
    # SORT
    # ========================================================

    sort_by = request.args.get(
        "sort",
        "created_at",
        type=str,
    )

    sort_order = request.args.get(
        "order",
        "desc",
        type=str,
    )

    # ========================================================
    # EXPORT
    # ========================================================

    workbook = service.export_excel(
        keyword=keyword,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # ========================================================
    # SAVE WORKBOOK TO MEMORY
    # ========================================================

    output = BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    # ========================================================
    # DOWNLOAD
    # ========================================================

    return send_file(
        output,
        as_attachment=True,
        download_name="kaizen_department_target.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )