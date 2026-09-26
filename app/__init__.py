from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
)

from app.config import Config
from app.extensions import (
    db,
    migrate,
    login_manager,
)

from app.logging_config import (
    configure_logging,
)
from app.core.template_helpers import (
    has_permission,
    has_any_permission,
    has_all_permissions,
)

from app.repositories.user_repository import (
    UserRepository,
)


# ==========================================
# Commands
# ==========================================

from app.commands.seed_command import (
    seed,
    seed_admin,
)

from app.commands.test_email import (
    test_email,
)
from app.routes.line import line_bp

# ==========================================
# Blueprints
# ==========================================

from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.department import department_bp
from app.routes.employee import employee_bp
from app.routes.user import user_bp
from app.routes.problem_category import (
    problem_category_bp,
)
from app.routes.problem import (
    problem_bp,
)
from app.routes.problem_attachment import (
    problem_attachment_bp,
)
from app.routes.role import role_bp
from app.routes.permission import (
    permission_bp,
)
from app.routes.improvement import improvement_bp
from app.routes.improvement_attachment import (
    improvement_attachment_bp
)
from app.routes.kaizen import kaizen_bp
from app.routes.kaizen_category import kaizen_category_bp
from app.routes.kaizen_reporting_period import (
    kaizen_reporting_period_bp
)
from app.routes.kaizen_department_target import (
    kaizen_department_target_bp
)
from app.routes.kaizen_award_period import (
    kaizen_award_period_bp
)
from app.routes.kaizen_award_judge import (
    kaizen_award_judge_bp,
)

from app.routes.kaizen_award_score import (
    kaizen_award_score_bp
)
from app.routes.public.problem_dashboard import problem_dashboard_bp
from app.routes.public.improvement_dashboard import improvement_dashboard_bp
from app.routes.public.kaizen_dashboard import kaizen_dashboard_bp
from app.routes.kaizen_award_result import (
    kaizen_award_result_bp
)
from app.routes.problem_assignment_authority import (
    problem_assignment_authority_bp,
)
from app.routes.improvement_approval_authority import (
    improvement_approval_authority_bp,
)
from app.routes.kaizen_approval_authority import (
    kaizen_approval_authority_bp,
)
from app.routes.notification_rule import (
    notification_rule_bp,
)
from app.routes.issue import issue_bp
from app.routes.kaizen_target_result import (
    kaizen_target_result_bp,
)

def create_app():

    app = Flask(__name__)

    app.config.from_object(
        Config
    )

    app.jinja_env.globals.update(
        has_permission=has_permission,
        has_any_permission=has_any_permission,
        has_all_permissions=has_all_permissions,
    )

    logger = configure_logging(
        app
    )

    # ==========================================
    # Initialize Extensions
    # ==========================================

    db.init_app(app)

    from app import models  # noqa: F401

    migrate.init_app(
        app,
        db,
    )

    login_manager.init_app(
        app
    )

    login_manager.login_view = (
        "auth.login"
    )

    # ==========================================
    # User Loader
    # ==========================================

    user_repository = (
        UserRepository()
    )

    @login_manager.user_loader
    def load_user(user_id):

        return user_repository.get_by_id(
            int(user_id)
        )

    logger.info(
        "Database initialized successfully."
    )

    # ==========================================
    # Register Blueprints
    # ==========================================

    app.register_blueprint(
        health_bp
    )

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        department_bp
    )

    app.register_blueprint(
        employee_bp
    )

    app.register_blueprint(
        user_bp
    )

    app.register_blueprint(
        problem_category_bp
    )

    app.register_blueprint(
        problem_bp
    )

    app.register_blueprint(
        problem_attachment_bp
    )
    app.register_blueprint(role_bp)
    app.register_blueprint(
        permission_bp
    )
    app.register_blueprint(improvement_bp)
    app.register_blueprint(
            improvement_attachment_bp
    )
    app.register_blueprint(
        kaizen_bp
    )
    app.register_blueprint(kaizen_category_bp)
    app.register_blueprint(
        kaizen_reporting_period_bp
    )
    app.register_blueprint(
        kaizen_department_target_bp
    )

    app.register_blueprint(
        kaizen_award_period_bp
    )

    app.register_blueprint(
        kaizen_award_judge_bp
    )

    app.register_blueprint(
        kaizen_award_score_bp
    )
    app.register_blueprint(problem_dashboard_bp)
    app.register_blueprint(improvement_dashboard_bp)
    app.register_blueprint(kaizen_dashboard_bp)
    app.register_blueprint(
        kaizen_award_result_bp
    )
    app.register_blueprint(problem_assignment_authority_bp)
    app.register_blueprint(
        improvement_approval_authority_bp
    )
    app.register_blueprint(
        kaizen_approval_authority_bp
    )
    app.register_blueprint(
        notification_rule_bp
    )
    app.register_blueprint(line_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(
        kaizen_target_result_bp
    )
    
    logger.info(
        "Blueprint registered successfully."
    )

    # ==========================================
    # Register CLI Commands
    # ==========================================

    app.cli.add_command(
        seed
    )

    app.cli.add_command(
        seed_admin
    )

    app.cli.add_command(
        test_email
    )
    

    # ==========================================
    # Default Route
    # ==========================================

    @app.route("/")
    def home():

        return redirect(
            url_for("dashboard.index")
        )

    logger.info(
        "CIMS application started successfully."
    )

    @app.errorhandler(403)
    def forbidden(error):

        return render_template(
            "errors/403.html"
        ), 403

    @app.errorhandler(401)
    def unauthorized(error):

        return render_template(
            "errors/401.html"
        ), 401

    return app