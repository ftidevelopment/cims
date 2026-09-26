from datetime import datetime
from io import BytesIO

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

from app.services.authorization_service import (
    AuthorizationService
)

from app.services.kaizen_award_period_service import (
    KaizenAwardPeriodService
)

from app.services.kaizen_award_score_service import (
    KaizenAwardScoreService
)


# ==========================================================
# BLUEPRINT
# ==========================================================

kaizen_award_period_bp = Blueprint(
    "kaizen_award_period",
    __name__,
    url_prefix="/kaizen_award_periods"
)


# ==========================================================
# SERVICES
# ==========================================================

service = KaizenAwardPeriodService()

score_service = KaizenAwardScoreService()

authorization_service = AuthorizationService()


# ==========================================================
# LIST
# ==========================================================

@kaizen_award_period_bp.route("/")
@login_required
def index():

    service = KaizenAwardPeriodService()

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

    award_periods = service.get_all(
        keyword=keyword,
        is_active=True,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "kaizen_award_period/list.html",
        award_periods=award_periods,
        keyword=keyword,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ==========================================================
# CREATE
# ==========================================================

@kaizen_award_period_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    # ======================================================
    # AUTHORIZATION
    # ======================================================

    if not authorization_service.can_create_award_period(
        user=current_user
    ):
        abort(403)

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        award_code = request.form.get(
            "award_code",
            ""
        ).strip()

        award_name = request.form.get(
            "award_name",
            ""
        ).strip()

        start_date_text = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date_text = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # ==================================================
        # DATE VALIDATION
        # ==================================================

        try:

            start_date = datetime.strptime(
                start_date_text,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid date format.",
                "error"
            )

            return render_template(
                "kaizen_award_period/form.html",
                award_period=None
            )

        # ==================================================
        # CREATE
        # ==================================================

        result = service.create(
            award_code=award_code,
            award_name=award_name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        # ==================================================
        # RESULT
        # ==================================================

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_award_period.index"
                )
            )

        flash(
            result.message,
            "error"
        )

        return render_template(
            "kaizen_award_period/form.html",
            award_period=None
        )

    # ======================================================
    # FORM
    # ======================================================

    return render_template(
        "kaizen_award_period/form.html",
        award_period=None
    )


# ==========================================================
# EDIT
# ==========================================================

@kaizen_award_period_bp.route(
    "/edit/<int:award_period_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(award_period_id):

    # ======================================================
    # AUTHORIZATION
    # ======================================================

    if not authorization_service.can_edit_award_period(
        user=current_user
    ):
        abort(403)

    # ======================================================
    # GET AWARD PERIOD
    # ======================================================

    award_period = service.get_by_id(
        award_period_id
    )

    if not award_period:

        flash(
            "Kaizen award period not found.",
            "error"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        award_name = request.form.get(
            "award_name",
            ""
        ).strip()

        start_date_text = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date_text = request.form.get(
            "end_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # ==================================================
        # DATE VALIDATION
        # ==================================================

        try:

            start_date = datetime.strptime(
                start_date_text,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid date format.",
                "error"
            )

            return render_template(
                "kaizen_award_period/form.html",
                award_period=award_period
            )

        # ==================================================
        # UPDATE
        # ==================================================

        result = service.update(
            award_period=award_period,
            award_name=award_name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )

        # ==================================================
        # RESULT
        # ==================================================

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_award_period.index"
                )
            )

        flash(
            result.message,
            "error"
        )

    # ======================================================
    # FORM
    # ======================================================

    return render_template(
        "kaizen_award_period/form.html",
        award_period=award_period
    )


# ==========================================================
# DELETE
# ==========================================================

@kaizen_award_period_bp.route(
    "/delete/<int:award_period_id>",
    methods=["POST"]
)
@login_required
def delete(award_period_id):

    # ======================================================
    # AUTHORIZATION
    # ======================================================

    if not authorization_service.can_delete_award_period(
        user=current_user
    ):
        abort(403)

    # ======================================================
    # GET AWARD PERIOD
    # ======================================================

    award_period = service.get_by_id(
        award_period_id
    )

    if not award_period:

        flash(
            "Kaizen award period not found.",
            "error"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # ======================================================
    # DELETE
    # ======================================================

    result = service.delete(
        award_period
    )

    # ======================================================
    # RESULT
    # ======================================================

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "error"
        )

    return redirect(
        url_for(
            "kaizen_award_period.index"
        )
    )


# ==========================================================
# INACTIVE
# ==========================================================

@kaizen_award_period_bp.route(
    "/inactive"
)
@login_required
def inactive():

    award_periods = service.get_inactive()

    return render_template(
        "kaizen_award_period/inactive.html",
        award_periods=award_periods
    )


# ==========================================================
# RESTORE
# ==========================================================

@kaizen_award_period_bp.route(
    "/restore/<int:award_period_id>",
    methods=["POST"]
)
@login_required
def restore(award_period_id):

    result = service.restore(
        award_period_id
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "error"
        )

    return redirect(
        url_for(
            "kaizen_award_period.inactive"
        )
    )


# ==========================================================
# EXPORT
# ==========================================================

@kaizen_award_period_bp.route(
    "/export"
)
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        "",
        type=str
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
        sort_order=sort_order
    )

    output = BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="kaizen_award_period.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


# ==========================================================
# CLOSE AWARD PERIOD
# ==========================================================

@kaizen_award_period_bp.route(
    "/close/<int:award_period_id>",
    methods=["POST"]
)
@login_required
def close(award_period_id):

    # ======================================================
    # AUTHORIZATION
    # ======================================================

    if not authorization_service.can_close_award_period(
        user=current_user
    ):
        abort(403)

    # ======================================================
    # GET AWARD PERIOD
    # ======================================================

    award_period = service.get_by_id(
        award_period_id
    )

    if not award_period:

        flash(
            "Kaizen award period not found.",
            "error"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # ======================================================
    # CHECK ALREADY CLOSED
    # ======================================================

    if award_period.status == "Closed":

        flash(
            "Kaizen award period is already closed.",
            "warning"
        )

        return redirect(
            url_for(
                "kaizen_award_period.edit",
                award_period_id=award_period_id
            )
        )

    # ======================================================
    # CLOSE
    # ======================================================

    result = service.close(
        award_period_id
    )

    # ======================================================
    # FLASH MESSAGE
    # ======================================================

    if result.success:

        flash(
            result.message,
            "success"
        )

    else:

        flash(
            result.message,
            "error"
        )

    # ======================================================
    # REDIRECT
    # ======================================================

    return redirect(
        url_for(
            "kaizen_award_period.edit",
            award_period_id=award_period_id
        )
    )