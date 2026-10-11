from flask import (
    Blueprint,
    render_template,
    request,
)

from app.services.public.PublicAuditDashboardService import (
    PublicAuditDashboardService,
)

from app.services.public.PublicAuditListService import (
    PublicAuditListService,
)
from app.services.public.PublicAuditFindingListService import (
    PublicAuditFindingListService
)

public_audit_bp = Blueprint(
    "public_audit",
    __name__,
    url_prefix="/public/audit",
)


# ==========================================================
# PUBLIC AUDIT DASHBOARD
# ==========================================================

@public_audit_bp.route("/")
def dashboard():

    service = PublicAuditDashboardService()

    dashboard_data = (
        service.get_dashboard()
    )

    return render_template(
        "audit_dashboard/dashboard.html",
        dashboard=dashboard_data,
    )


# ==========================================================
# PUBLIC AUDIT LIST
# ==========================================================

@public_audit_bp.route("/list")
def list():

    service = PublicAuditListService()


    # =====================================================
    # PAGINATION
    # =====================================================

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


    # =====================================================
    # FILTER
    # =====================================================

    search = request.args.get(
        "search",
        "",
    )


    status = request.args.get(
        "status",
        "",
    )


    audit_type_id = request.args.get(
        "audit_type_id",
        "",
    )


    audit_category_id = request.args.get(
        "audit_category_id",
        "",
    )


    department_id = request.args.get(
        "department_id",
        "",
    )


    period = request.args.get(
        "period",
        "",
    )


    # =====================================================
    # NEXT AUDIT
    # =====================================================

    next_audit = request.args.get(
        "next_audit",
        "",
    )


    # =====================================================
    # COMPLETED AUDIT
    # =====================================================

    completed_audit = request.args.get(
        "completed_audit",
        "",
    )


    # =====================================================
    # GET DATA
    # =====================================================

    data = service.get_audits(

        page=page,

        per_page=per_page,

        search=search,

        status=status,

        audit_type_id=audit_type_id,

        audit_category_id=audit_category_id,

        department_id=department_id,

        period=period,

        next_audit=next_audit,

        completed_audit=completed_audit,

    )


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(

        "audit_dashboard/list.html",

        **data

    )


# ============================================================
# PUBLIC AUDIT FINDING LIST
# ============================================================

@public_audit_bp.route("/findings")
def findings():

    service = PublicAuditFindingListService()


    # =====================================================
    # PAGINATION
    # =====================================================

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


    # =====================================================
    # FILTERS
    # =====================================================

    search = request.args.get(
        "search",
        "",
    )

    status = request.args.get(
        "status",
        "",
    )

    severity = request.args.get(
        "severity",
        "",
    )

    finding_source = request.args.get(
        "finding_source",
        "",
    )

    department_id = request.args.get(
        "department_id",
        "",
    )

    pic_employee_id = request.args.get(
        "pic_employee_id",
        "",
    )

    overdue = request.args.get(
        "overdue",
        "",
    )

    open_only = request.args.get(
        "open_only",
        "",
    )

    period = request.args.get(
        "period",
        "",
    )


    # =====================================================
    # GET DATA
    # =====================================================

    data = service.get_findings(

        page=page,

        per_page=per_page,

        search=search,

        status=status,

        severity=severity,

        finding_source=finding_source,

        department_id=department_id,

        pic_employee_id=pic_employee_id,

        overdue=overdue,

        period=period,

        open_only=open_only,

    )


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(

        "audit_dashboard/finding_list.html",

        **data

    )