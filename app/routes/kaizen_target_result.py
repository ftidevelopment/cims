from flask import (
    Blueprint,
    render_template,
    request,
)

from flask_login import login_required

from app.services.kaizen_target_result_service import (
    KaizenTargetResultService,
)


kaizen_target_result_bp = Blueprint(
    "kaizen_target_result",
    __name__,
    url_prefix="/kaizen-target-result",
)


@kaizen_target_result_bp.route("/")
@login_required
def index():
    """
    Display Kaizen Target vs Result.
    """

    period_id = request.args.get(
        "period_id",
        default=None,
        type=int,
    )

    service = KaizenTargetResultService()

    data = service.get_target_result(
        period_id=period_id
    )

    return render_template(
        "kaizen_target_result/index.html",
        data=data,
    )