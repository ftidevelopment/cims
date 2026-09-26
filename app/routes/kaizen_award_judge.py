from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_login import (
    current_user,
    login_required,
)

from app.models.employee import Employee

from app.services.authorization_service import (
    AuthorizationService,
)

from app.services.kaizen_award_judge_service import (
    KaizenAwardJudgeService,
)

from app.services.kaizen_award_period_service import (
    KaizenAwardPeriodService,
)


kaizen_award_judge_bp = Blueprint(
    "kaizen_award_judge",
    __name__,
    url_prefix="/kaizen_award_judges",
)


authorization_service = AuthorizationService()


# =========================================================
# LIST JUDGES BY AWARD PERIOD
# =========================================================

@kaizen_award_judge_bp.route(
    "/<int:award_period_id>"
)
@login_required
def index(award_period_id):

    award_period_service = KaizenAwardPeriodService()
    judge_service = KaizenAwardJudgeService()

    # -----------------------------------------------------
    # Get Award Period
    # -----------------------------------------------------

    award_period = (
        award_period_service
        .get_by_id(
            award_period_id
        )
    )

    if not award_period:

        flash(
            "Award period not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # -----------------------------------------------------
    # Get Judges
    # -----------------------------------------------------

    judges = (
        judge_service
        .get_by_award_period(
            award_period_id
        )
    )

    return render_template(
        "kaizen_award_judge/list.html",
        award_period=award_period,
        judges=judges,
    )


# =========================================================
# ADD JUDGE
# =========================================================

@kaizen_award_judge_bp.route(
    "/<int:award_period_id>/add",
    methods=["GET", "POST"]
)
@login_required
def add(award_period_id):

    award_period_service = (
        KaizenAwardPeriodService()
    )

    judge_service = (
        KaizenAwardJudgeService()
    )

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if not authorization_service.can_assign_award_judge(
        user=current_user
    ):

        flash(
            "You do not have permission to assign an Award Judge.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # -----------------------------------------------------
    # Get Award Period
    # -----------------------------------------------------

    award_period = (
        award_period_service
        .get_by_id(
            award_period_id
        )
    )

    if not award_period:

        flash(
            "Award period not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # -----------------------------------------------------
    # Get Active Employees
    # -----------------------------------------------------

    employees = (
        Employee.query
        .filter_by(
            is_active=True,
            status="ACTIVE"
        )
        .order_by(
            Employee.nik.asc()
        )
        .all()
    )

    # -----------------------------------------------------
    # POST
    # -----------------------------------------------------

    if request.method == "POST":

        employee_id = request.form.get(
            "employee_id",
            type=int
        )

        result = (
            judge_service
            .create(
                award_period_id=award_period_id,
                employee_id=employee_id,
            )
        )

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_award_judge.index",
                    award_period_id=award_period_id,
                )
            )

        flash(
            result.message,
            "danger"
        )

    return render_template(
        "kaizen_award_judge/form.html",
        award_period=award_period,
        employees=employees,
    )


# =========================================================
# DELETE JUDGE
# =========================================================

@kaizen_award_judge_bp.route(
    "/delete/<int:judge_id>",
    methods=["POST"],
)
@login_required
def delete(judge_id):

    judge_service = (
        KaizenAwardJudgeService()
    )

    # -----------------------------------------------------
    # Authorization
    # -----------------------------------------------------

    if not authorization_service.can_remove_award_judge(
        user=current_user
    ):

        flash(
            "You do not have permission to remove an Award Judge.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # -----------------------------------------------------
    # Get Judge
    # -----------------------------------------------------

    judge = (
        judge_service
        .get_by_id(
            judge_id
        )
    )

    if not judge:

        flash(
            "Judge not found.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # -----------------------------------------------------
    # Get Award Period
    # -----------------------------------------------------

    award_period_id = (
        judge.award_period_id
    )

    # -----------------------------------------------------
    # Delete Judge
    # -----------------------------------------------------

    result = (
        judge_service
        .delete(
            judge
        )
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
            "kaizen_award_judge.index",
            award_period_id=award_period_id,
        )
    )


# =========================================================
# INACTIVE JUDGES
# =========================================================

@kaizen_award_judge_bp.route(
    "/inactive"
)
@login_required
def inactive():

    judge_service = (
        KaizenAwardJudgeService()
    )

    judges = (
        judge_service
        .get_inactive()
    )

    return render_template(
        "kaizen_award_judge/inactive.html",
        judges=judges,
    )


# =========================================================
# RESTORE JUDGE
# =========================================================

@kaizen_award_judge_bp.route(
    "/restore/<int:judge_id>",
    methods=["POST"],
)
@login_required
def restore(judge_id):

    judge_service = (
        KaizenAwardJudgeService()
    )

    result = (
        judge_service
        .restore(
            judge_id
        )
    )

    if result.success:

        flash(
            result.message,
            "success"
        )

        # -------------------------------------------------
        # If restored judge is available,
        # return to its Award Period
        # -------------------------------------------------

        if result.data:

            return redirect(
                url_for(
                    "kaizen_award_judge.index",
                    award_period_id=(
                        result.data.award_period_id
                    ),
                )
            )

    else:

        flash(
            result.message,
            "danger"
        )

    return redirect(
        url_for(
            "kaizen_award_judge.inactive"
        )
    )