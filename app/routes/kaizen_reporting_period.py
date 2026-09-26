from io import BytesIO
from datetime import datetime

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

from app.services.kaizen_reporting_period_service import (
    KaizenReportingPeriodService,
)


kaizen_reporting_period_bp = Blueprint(
    "kaizen_reporting_period",
    __name__,
    url_prefix="/kaizen_reporting_periods"
)


authorization_service = AuthorizationService()


# =========================================================
# LIST REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route("/")
@login_required
def index():

    service = KaizenReportingPeriodService()

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    sort_by = request.args.get(
        "sort_by",
        "start_date"
    )

    sort_order = request.args.get(
        "sort_order",
        "asc"
    )

    periods = service.get_all(
        keyword=keyword,
        is_active=True,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "kaizen_reporting_period/list.html",
        periods=periods,
        keyword=keyword,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# =========================================================
# CREATE REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if not authorization_service.can_create_reporting_period(
        user=current_user
    ):

        flash(
            "You do not have permission to create a Kaizen Reporting Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_reporting_period.index"
            )
        )

    service = KaizenReportingPeriodService()

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        period_code = request.form.get(
            "period_code",
            ""
        ).strip()

        period_name = request.form.get(
            "period_name",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # -------------------------------------------------
        # Convert String Date
        # -------------------------------------------------

        try:

            start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid date format.",
                "danger"
            )

            return render_template(
                "kaizen_reporting_period/form.html"
            )

        # -------------------------------------------------
        # Create
        # -------------------------------------------------

        result = service.create(
            period_code=period_code,
            period_name=period_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_reporting_period.index"
                )
            )

        flash(
            result.message,
            "danger"
        )

    return render_template(
        "kaizen_reporting_period/form.html"
    )


# =========================================================
# EDIT REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route(
    "/edit/<int:reporting_period_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(reporting_period_id):

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if not authorization_service.can_edit_reporting_period(
        user=current_user
    ):

        flash(
            "You do not have permission to edit a Kaizen Reporting Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_reporting_period.index"
            )
        )

    service = KaizenReportingPeriodService()

    reporting_period = service.get_by_id(
        reporting_period_id
    )

    if not reporting_period:

        flash(
            "Reporting period not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_reporting_period.index"
            )
        )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        period_name = request.form.get(
            "period_name",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # -------------------------------------------------
        # Convert String Date
        # -------------------------------------------------

        try:

            start_date = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid date format.",
                "danger"
            )

            return render_template(
                "kaizen_reporting_period/form.html",
                reporting_period=reporting_period
            )

        # -------------------------------------------------
        # Update
        # -------------------------------------------------

        result = service.update(
            reporting_period=reporting_period,
            period_name=period_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_reporting_period.index"
                )
            )

        flash(
            result.message,
            "danger"
        )

    return render_template(
        "kaizen_reporting_period/form.html",
        reporting_period=reporting_period
    )


# =========================================================
# DELETE REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route(
    "/delete/<int:reporting_period_id>",
    methods=["POST"]
)
@login_required
def delete(reporting_period_id):

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if not authorization_service.can_delete_reporting_period(
        user=current_user
    ):

        flash(
            "You do not have permission to delete a Kaizen Reporting Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_reporting_period.index"
            )
        )

    service = KaizenReportingPeriodService()

    reporting_period = service.get_by_id(
        reporting_period_id
    )

    if not reporting_period:

        flash(
            "Reporting period not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_reporting_period.index"
            )
        )

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    result = service.delete(
        reporting_period
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )

    return redirect(
        url_for(
            "kaizen_reporting_period.index"
        )
    )


# =========================================================
# INACTIVE REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route(
    "/inactive"
)
@login_required
def inactive():

    service = KaizenReportingPeriodService()

    periods = service.get_inactive()

    return render_template(
        "kaizen_reporting_period/inactive.html",
        periods=periods
    )


# =========================================================
# RESTORE REPORTING PERIOD
# =========================================================

@kaizen_reporting_period_bp.route(
    "/restore/<int:reporting_period_id>",
    methods=["POST"]
)
@login_required
def restore(reporting_period_id):

    service = KaizenReportingPeriodService()

    result = service.restore(
        reporting_period_id
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "danger"
        )

    return redirect(
        url_for(
            "kaizen_reporting_period.inactive"
        )
    )


# =========================================================
# EXPORT
# =========================================================

@kaizen_reporting_period_bp.route(
    "/export"
)
@login_required
def export():

    service = KaizenReportingPeriodService()

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    sort_by = request.args.get(
        "sort_by",
        "start_date"
    )

    sort_order = request.args.get(
        "sort_order",
        "asc"
    )

    workbook = service.export_excel(
        keyword=keyword,
        is_active=True,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    output = BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="kaizen_reporting_period.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )