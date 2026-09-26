from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_login import LoginManager

from celery import Celery


# ==========================================
# Database
# ==========================================

db = SQLAlchemy()


# ==========================================
# Database Migration
# ==========================================

migrate = Migrate()


# ==========================================
# Authentication
# ==========================================

login_manager = LoginManager()


# ==========================================
# Celery
# ==========================================

celery = Celery()