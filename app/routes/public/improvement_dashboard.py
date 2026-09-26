from flask import (
    Blueprint,
    render_template,
    request,
)

from app.services.public.public_improvement_dashboard_service import (
    PublicImprovementDashboardService,
)

from app.services.public.public_improvement_list_service import (
    PublicImprovementListService,
)


improvement_dashboard_bp = Blueprint(
    "improvement_dashboard",
    __name__,
    url_prefix="/improvement-dashboard",
)


# =========================================================
# PUBLIC IMPROVEMENT DASHBOARD
# =========================================================

@improvement_dashboard_bp.route("/")
def index():

    service = PublicImprovementDashboardService()

    dashboard = service.get_dashboard()

    return render_template(
        "improvement_dashboard/index.html",
        dashboard=dashboard,
    )


# =========================================================
# PUBLIC IMPROVEMENT LIST
# =========================================================

@improvement_dashboard_bp.route("/improvements")
def improvements():

    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    # -----------------------------------------------------
    # PER PAGE
    # -----------------------------------------------------

    per_page = request.args.get(
        "per_page",
        10,
        type=int,
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()

    # -----------------------------------------------------
    # DEPARTMENT
    # -----------------------------------------------------

    department = request.args.get(
        "department",
        "",
        type=str,
    ).strip()

    # -----------------------------------------------------
    # PERIOD
    #
    # Example:
    # period=6_months
    # -----------------------------------------------------

    period = request.args.get(
        "period",
        "",
        type=str,
    ).strip()

    # -----------------------------------------------------
    # SERVICE
    # -----------------------------------------------------

    service = PublicImprovementListService()

    result = service.get_improvements(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        department=department,
        period=period,
    )

    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------

    return render_template(
        "improvement_dashboard/list.html",

        improvements=result["improvements"],

        pagination=result["pagination"],

        search=result["search"],

        status=result["status"],

        department=result["department"],

        departments=result["departments"],

        period=result["period"],
    )


# =========================================================
# PUBLIC IMPROVEMENT DETAIL
# =========================================================

@improvement_dashboard_bp.route(
    "/<int:improvement_id>"
)
def detail(improvement_id):

    service = PublicImprovementDashboardService()

    # -----------------------------------------------------
    # GET IMPROVEMENT
    # -----------------------------------------------------

    improvement = service.get_improvement_detail(
        improvement_id
    )

    # -----------------------------------------------------
    # NOT FOUND
    # -----------------------------------------------------

    if not improvement:

        return render_template(
            "improvement_dashboard/not_found.html"
        ), 404

    # -----------------------------------------------------
    # BENEFIT
    # -----------------------------------------------------

    benefit = service.calculate_benefit(
        improvement_id
    )

    # -----------------------------------------------------
    # DETAIL PAGE
    # -----------------------------------------------------

    return render_template(
        "improvement_dashboard/view.html",

        improvement=improvement,

        benefit=benefit,
    )