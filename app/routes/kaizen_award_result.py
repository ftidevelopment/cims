from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import login_required

from app.services.kaizen_award_result_service import (
    KaizenAwardResultService,
)


# =========================================================
# BLUEPRINT
# =========================================================

kaizen_award_result_bp = Blueprint(
    "kaizen_award_result",
    __name__,
    url_prefix="/kaizen-award-results",
)


# =========================================================
# SERVICE
# =========================================================

service = KaizenAwardResultService()


# =========================================================
# INDEX
# =========================================================

@kaizen_award_result_bp.route("/")
@login_required
def index():

    # -----------------------------------------------------
    # Get Closed Award Periods
    # -----------------------------------------------------

    award_periods = service.get_closed_periods()


    # -----------------------------------------------------
    # Selected Period
    # -----------------------------------------------------

    award_period_id = request.args.get(
        "award_period_id",
        type=int
    )


    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Default Data
    # -----------------------------------------------------

    selected_period = None

    results = []

    pagination = None


    # -----------------------------------------------------
    # Get Selected Period Result
    # -----------------------------------------------------

    if award_period_id:

        result = service.get_result(
            award_period_id=award_period_id,
            page=page,
            per_page=per_page
        )


        if not result.success:

            flash(
                result.message,
                "danger"
            )

            return redirect(
                url_for(
                    "kaizen_award_result.index"
                )
            )


        selected_period = (
            result.data["award_period"]
        )

        results = (
            result.data["results"]
        )

        pagination = (
            result.data["pagination"]
        )


    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render_template(
        "kaizen_award_result/index.html",

        award_periods=award_periods,

        selected_period=selected_period,

        results=results,

        pagination=pagination,

        selected_period_id=award_period_id,

        per_page=per_page,
    )


# =========================================================
# DETAIL
# =========================================================

@kaizen_award_result_bp.route(
    "/<int:award_period_id>/<int:kaizen_id>"
)
@login_required
def detail(
    award_period_id,
    kaizen_id
):

    # -----------------------------------------------------
    # Get Detail
    # -----------------------------------------------------

    result = service.get_detail(
        award_period_id=award_period_id,
        kaizen_id=kaizen_id
    )


    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not result.success:

        flash(
            result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_result.index",
                award_period_id=award_period_id
            )
        )


    # -----------------------------------------------------
    # Data
    # -----------------------------------------------------

    data = result.data


    # -----------------------------------------------------
    # Render
    # -----------------------------------------------------

    return render_template(
        "kaizen_award_result/detail.html",

        award_period=data["award_period"],

        kaizen=data["kaizen"],

        scores=data["scores"],

        judges_scored=data["judges_scored"],

        total_score=data["total_score"],

        average_score=data["average_score"],
    )