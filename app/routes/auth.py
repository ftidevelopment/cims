from flask import (
    Blueprint,
    render_template,
    request,
    flash,redirect,url_for
)

from app.services.auth_service import AuthService
from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user,
)

auth_bp = Blueprint(
    "auth",
    __name__,
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        ).strip()

        if not username:
            flash(
                "Username wajib diisi.",
                "danger",
            )

            return render_template(
                "auth/login.html",
            )

        if not password:
            flash(
                "Password wajib diisi.",
                "danger",
            )

            return render_template(
                "auth/login.html",
            )

        auth_service = AuthService()
        result = auth_service.authenticate(
            username,
            password,
        )

        if result.success:
            login_user(result.data)
            flash(
                result.message,
                "success",
            )
            return redirect(url_for("dashboard.my_dashboard"))
        else:
            flash(
                result.message,
                "danger",
            )

    return render_template("auth/login.html")

@auth_bp.route(
    "/change-password",
    methods=["GET", "POST"],
)
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get(
            "current_password",
            "",
        ).strip()

        new_password = request.form.get(
            "new_password",
            "",
        ).strip()

        confirm_password = request.form.get(
            "confirm_password",
            "",
        ).strip()

        # ==========================================
        # Validation
        # ==========================================

        if not current_password:

            flash(
                "Current password wajib diisi.",
                "danger",
            )

            return render_template(
                "auth/change_password.html"
            )

        if not new_password:

            flash(
                "New password wajib diisi.",
                "danger",
            )

            return render_template(
                "auth/change_password.html"
            )

        if not confirm_password:

            flash(
                "Confirm password wajib diisi.",
                "danger",
            )

            return render_template(
                "auth/change_password.html"
            )

        if new_password != confirm_password:

            flash(
                "New password dan confirm password tidak sama.",
                "danger",
            )

            return render_template(
                "auth/change_password.html"
            )

        # ==========================================
        # Change Password
        # ==========================================

        auth_service = AuthService()

        result = auth_service.change_password(
            user=current_user,
            current_password=current_password,
            new_password=new_password,
        )

        if result.success:

            flash(
                result.message,
                "success",
            )

            return redirect(
                url_for(
                    "dashboard.my_dashboard"
                )
            )

        flash(
            result.message,
            "danger",
        )

    return render_template(
        "auth/change_password.html"
    )

@auth_bp.route("/logout")
def logout():
    logout_user()

    flash("You have been logged out.", "success")

    return redirect(
        url_for("dashboard.index")
    )

