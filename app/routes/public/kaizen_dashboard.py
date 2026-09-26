from flask import (
    Blueprint,
    render_template,
    request,
)

from app.services.public.public_kaizen_dashboard_service import (
    PublicKaizenDashboardService,
)

from app.services.public.public_kaizen_list_service import (
    PublicKaizenListService,
)


kaizen_dashboard_bp = Blueprint(
    "kaizen_dashboard",
    __name__,
    url_prefix="/kaizen-dashboard",
)


# ============================================================
# DASHBOARD
# ============================================================

@kaizen_dashboard_bp.route("/")
def index():

    service = PublicKaizenDashboardService()

    dashboard = service.get_dashboard()

    return render_template(
        "kaizen_dashboard/index.html",
        dashboard=dashboard,
    )


# ============================================================
# KAIZEN LIST
# ============================================================

@kaizen_dashboard_bp.route("/kaizens")
def kaizens():

    # ========================================================
    # PAGINATION
    # ========================================================

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


    # ========================================================
    # SEARCH
    # ========================================================

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()


    # ========================================================
    # STATUS
    # ========================================================

    status = request.args.get(
        "status",
        "",
        type=str,
    ).strip()


    # ========================================================
    # DEPARTMENT
    # ========================================================

    department_id = request.args.get(
        "department_id",
        "",
        type=str,
    ).strip()


    # ========================================================
    # PERIOD
    # ========================================================

    period = request.args.get(
        "period",
        "",
        type=str,
    ).strip()


    # ========================================================
    # OPEN / PENDING
    # ========================================================

    open_only = (
        request.args.get(
            "open_only",
            "",
            type=str,
        ).lower()
        == "true"
    )


    # ========================================================
    # AGING
    # ========================================================

    aging = request.args.get(
        "aging",
        "",
        type=str,
    ).strip()


    # ========================================================
    # SERVICE
    # ========================================================

    service = PublicKaizenListService()

    result = service.get_kaizens(

        page=page,

        per_page=per_page,

        search=search,

        status=status,

        department_id=department_id,

        period=period,

        open_only=open_only,

        aging=aging,

    )


    # ========================================================
    # RENDER
    # ========================================================

    return render_template(

        "kaizen_dashboard/list.html",

        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        kaizens=result["kaizens"],

        pagination=result["pagination"],


        # ----------------------------------------------------
        # Filters
        # ----------------------------------------------------

        search=result["search"],

        status=result["status"],

        department_id=result["department_id"],

        departments=result["departments"],

        period=result["period"],


        # ----------------------------------------------------
        # Period
        # ----------------------------------------------------

        period_start=result["period_start"],

        period_end=result["period_end"],

        period_start_display=result[
            "period_start_display"
        ],

        period_end_display=result[
            "period_end_display"
        ],


        # ----------------------------------------------------
        # Open / Aging
        # ----------------------------------------------------

        open_only=result["open_only"],

        aging=result["aging"],

    )


# ============================================================
# KAIZEN DETAIL
# ============================================================

@kaizen_dashboard_bp.route("/<int:kaizen_id>")
def detail(kaizen_id):

    service = PublicKaizenDashboardService()

    kaizen = service.get_detail(
        kaizen_id
    )

    if not kaizen:

        return render_template(
            "kaizen_dashboard/not_found.html"
        ), 404

    return render_template(
        "kaizen_dashboard/view.html",
        kaizen=kaizen,
    )