from flask import (
    Blueprint,
    render_template,
)

from flask_login import (
    login_required,
    current_user,
)

from app.core.authorization import (
    permission_required,
)

from app.services.dashboard_service import (
    DashboardService
)

from app.services.user_dashboard_service import (
    UserDashboardService
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

# ==================================================
# PUBLIC HOME
# ==================================================

@dashboard_bp.route("/")
def home():

    return render_template(
        "dashboard/home.html"
    )
# ==================================================
# PUBLIC DASHBOARD
# ==================================================

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/dashboard/")
def index():

    service = DashboardService()

    dashboard_data = (
        service.get_problem_improvement_dashboard()
    )

    return render_template(
        "dashboard/index.html",
        dashboard=dashboard_data
    )


# ==================================================
# USER DASHBOARD
#
# Dashboard setelah login
# 6 bulan terakhir
# My Problem
# My Improvement
# My Kaizen
# ==================================================

@dashboard_bp.route("/my-dashboard")
@login_required
def my_dashboard():

    service = UserDashboardService()

    dashboard_data = (
        service.get_dashboard(
            employee_id=current_user.employee_id,
            user=current_user
        )
    )

    return render_template(
        "dashboard/my_dashboard.html",
        dashboard=dashboard_data
    )

@dashboard_bp.route("/my-dashboard/action-required/problem")
@login_required
def problem_action_required():
    service = UserDashboardService()

    action_required = service.get_problem_action_required(
        user=current_user
    )

    return render_template(
        "dashboard/problem_action_required.html",
        action_required=action_required
    )


# ==========================================================
# IMPROVEMENT ACTION REQUIRED
# ==========================================================

@dashboard_bp.route(
    "/my-dashboard/action-required/improvement"
)
@login_required
def improvement_action_required():

    service = UserDashboardService()

    action_required = (
        service.get_improvement_action_required(
            user=current_user
        )
    )

    return render_template(
        "dashboard/improvement_action_required.html",
        action_required=action_required,
    )

# ==========================================================
# KAIZEN ACTION REQUIRED
# ==========================================================

@dashboard_bp.route(
    "/my-dashboard/action-required/kaizen"
)
@login_required
def kaizen_action_required():

    service = UserDashboardService()

    action_required = (
        service.get_kaizen_action_required(
            user=current_user
        )
    )

    return render_template(
        "dashboard/kaizen_action_required.html",
        action_required=action_required,
    )

# ==================================================
# AUTHORIZATION TEST
# ==================================================

@dashboard_bp.route("/test-authorization")
@login_required
def test_authorization():

    return {
        "username": current_user.username,

        "role": current_user.role_code,

        "permissions": {

            "PROBLEM_VIEW":
                current_user.has_permission(
                    "PROBLEM_VIEW"
                ),

            "PROBLEM_CREATE":
                current_user.has_permission(
                    "PROBLEM_CREATE"
                ),

            "PROBLEM_EDIT":
                current_user.has_permission(
                    "PROBLEM_EDIT"
                ),

            "PROBLEM_ASSIGN":
                current_user.has_permission(
                    "PROBLEM_ASSIGN"
                ),

            "PROBLEM_DELETE":
                current_user.has_permission(
                    "PROBLEM_DELETE"
                ),
        }
    }


# ==================================================
# PROBLEM ASSIGN TEST
# ==================================================

@dashboard_bp.route(
    "/test-problem-assign"
)
@login_required
@permission_required(
    "PROBLEM_ASSIGN"
)
def test_problem_assign():

    return {
        "status": "success",

        "message":
            "You have PROBLEM_ASSIGN permission."
    }


# ==================================================
# PROBLEM DELETE TEST
# ==================================================

@dashboard_bp.route(
    "/test-problem-delete"
)
@login_required
@permission_required(
    "PROBLEM_DELETE"
)
def test_problem_delete():

    return {
        "status": "success",

        "message":
            "You have PROBLEM_DELETE permission."
    }




# ==================================================
# USER DASHBOARD DATA TEST
#
# Digunakan sementara untuk memastikan
# UserDashboardService menghasilkan data yang benar.
# ==================================================

@dashboard_bp.route(
    "/my-dashboard-data-test"
)
@login_required
def my_dashboard_data_test():

    service = UserDashboardService()

    dashboard_data = (
        service.get_dashboard(
            employee_id=current_user.employee_id
        )
    )

    return dashboard_data