from celery import Celery
from app import create_app
from app.config import Config


flask_app = create_app()


celery = Celery(
    "cims",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
)


celery.conf.update(
    timezone="Asia/Jakarta",
    enable_utc=False,
)


class FlaskTask(celery.Task):

    def __call__(self, *args, **kwargs):

        with flask_app.app_context():

            return self.run(*args, **kwargs)


celery.Task = FlaskTask


# ==========================================
# Register Celery Tasks
# ==========================================
import app.tasks.notification_tasks