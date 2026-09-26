from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from flask_login import (
    login_required,
    current_user,
)

from app.services.authorization_service import (
    AuthorizationService,
)

from app.services.kaizen_award_period_service import (
    KaizenAwardPeriodService,
)

from app.services.kaizen_award_judge_service import (
    KaizenAwardJudgeService,
)

from app.services.kaizen_service import (
    KaizenService,
)

from app.services.kaizen_award_score_service import (
    KaizenAwardScoreService,
)

from app.repositories.kaizen_award_score_repository import (
    KaizenAwardScoreRepository,
)


kaizen_award_score_bp = Blueprint(
    "kaizen_award_score",
    __name__,
    url_prefix="/kaizen_award_scores",
)


authorization_service = AuthorizationService()


# ==========================================================
# SCORE LIST
# ==========================================================

@kaizen_award_score_bp.route(
    "/<int:award_period_id>"
)
@login_required
def index(award_period_id):

    award_period_service = (
        KaizenAwardPeriodService()
    )

    judge_service = (
        KaizenAwardJudgeService()
    )

    score_service = (
        KaizenAwardScoreService()
    )

    score_repository = (
        KaizenAwardScoreRepository()
    )

    # ==================================================
    # Get Award Period
    # ==================================================

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

    # ==================================================
    # Current User
    # ==================================================

    employee_id = (
        current_user.employee_id
    )

    # ==================================================
    # Pagination
    # ==================================================

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

    # ==================================================
    # Check Current User as Judge
    # ==================================================

    is_judge = (
        judge_service
        .is_judge(
            award_period_id=award_period_id,
            employee_id=employee_id
        )
    )

    if not is_judge:

        flash(
            "You are not registered as a Judge for this Award Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # ==================================================
    # Get Score of Current Judge
    # ==================================================

    scores = (
        score_repository
        .get_by_judge(
            award_period_id=award_period_id,
            judge_employee_id=employee_id
        )
    )

    score_map = {
        score.kaizen_id: score
        for score in scores
    }

    # ==================================================
    # Get Kaizen + Score Summary
    # ==================================================

    score_summary = (
        score_service
        .get_summary_by_award_period(
            award_period_id=award_period_id,
            start_date=award_period.start_date,
            end_date=award_period.end_date,
            page=page,
            per_page=per_page
        )
    )

    # ==================================================
    # Prepare Kaizen List
    # ==================================================

    paged_kaizens = []

    score_summary_map = {}

    for item in score_summary.items:

        # item[0] = Kaizen
        # item[1] = Judges Scored
        # item[2] = Total Score
        # item[3] = Average Score

        kaizen = item[0]

        paged_kaizens.append(
            kaizen
        )

        score_summary_map[
            kaizen.id
        ] = {
            "judges_scored": item[1],
            "total_score": item[2],
            "average_score": item[3]
        }

    # ==================================================
    # Render
    # ==================================================

    return render_template(
        "kaizen_award_score/list.html",
        award_period=award_period,
        kaizens=paged_kaizens,
        score_map=score_map,
        score_summary_map=score_summary_map,
        pagination=score_summary
    )


# ==========================================================
# SCORE FORM
# ==========================================================

@kaizen_award_score_bp.route(
    "/<int:award_period_id>/<int:kaizen_id>/score",
    methods=["GET", "POST"]
)
@login_required
def score(
    award_period_id,
    kaizen_id
):

    from datetime import (
        datetime,
        time,
        timedelta,
    )

    award_period_service = (
        KaizenAwardPeriodService()
    )

    judge_service = (
        KaizenAwardJudgeService()
    )

    kaizen_service = (
        KaizenService()
    )

    # ==================================================
    # Get Award Period
    # ==================================================

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

    # ==================================================
    # Check Current User as Judge
    # ==================================================

    employee_id = (
        current_user.employee_id
    )

    is_judge = (
        judge_service
        .is_judge(
            award_period_id=award_period_id,
            employee_id=employee_id
        )
    )

    if not is_judge:

        flash(
            "You are not registered as a Judge for this Award Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_period.index"
            )
        )

    # ==================================================
    # Get Kaizen
    # ==================================================

    kaizen_result = (
        kaizen_service
        .get_by_id(
            kaizen_id
        )
    )

    if not kaizen_result.success:

        flash(
            kaizen_result.message,
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_score.index",
                award_period_id=award_period_id
            )
        )

    kaizen = (
        kaizen_result.data
    )

    # ==================================================
    # Validate Kaizen Approval Date
    # ==================================================

    start_datetime = datetime.combine(
        award_period.start_date,
        time.min
    )

    end_datetime = datetime.combine(
        award_period.end_date
        + timedelta(days=1),
        time.min
    )

    if (
        kaizen.approved_at is None
        or kaizen.approved_at < start_datetime
        or kaizen.approved_at >= end_datetime
    ):

        flash(
            "Kaizen approval date is outside this Award Period.",
            "danger"
        )

        return redirect(
            url_for(
                "kaizen_award_score.index",
                award_period_id=award_period_id
            )
        )

    # ==================================================
    # Get Existing Score
    # ==================================================

    score_repository = (
        KaizenAwardScoreRepository()
    )

    existing_score = (
        score_repository
        .get_by_kaizen_and_judge(
            award_period_id=award_period_id,
            kaizen_id=kaizen_id,
            judge_employee_id=employee_id
        )
    )

    # ==================================================
    # Authorization
    #
    # New Score  -> CREATE
    # Existing   -> EDIT
    # ==================================================

    if existing_score:

        can_edit = (
            authorization_service
            .can_edit_award_score(
                user=current_user
            )
        )

        if not can_edit:

            flash(
                "You do not have permission to edit an Award Score.",
                "danger"
            )

            return redirect(
                url_for(
                    "kaizen_award_score.index",
                    award_period_id=award_period_id
                )
            )

    else:

        can_create = (
            authorization_service
            .can_create_award_score(
                user=current_user
            )
        )

        if not can_create:

            flash(
                "You do not have permission to create an Award Score.",
                "danger"
            )

            return redirect(
                url_for(
                    "kaizen_award_score.index",
                    award_period_id=award_period_id
                )
            )

    # ==================================================
    # POST - Save / Update Score
    # ==================================================

    if request.method == "POST":

        score = request.form.get(
            "score"
        )

        comment = request.form.get(
            "comment"
        )

        score_service = (
            KaizenAwardScoreService()
        )

        result = (
            score_service
            .create_or_update(
                award_period_id=award_period_id,
                kaizen_id=kaizen_id,
                judge_employee_id=employee_id,
                score=score,
                comment=comment
            )
        )

        if result.success:

            flash(
                result.message,
                "success"
            )

            return redirect(
                url_for(
                    "kaizen_award_score.index",
                    award_period_id=award_period_id
                )
            )

        flash(
            result.message,
            "danger"
        )

    # ==================================================
    # Display Form
    # ==================================================

    return render_template(
        "kaizen_award_score/form.html",
        award_period=award_period,
        kaizen=kaizen,
        existing_score=existing_score
    )