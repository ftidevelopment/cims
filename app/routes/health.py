from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():

    try:

        db.session.execute(text("SELECT 1"))

        return jsonify(
            {
                "status": "success",
                "database": "Connected",
                "application": "CIMS",
                "message": "Application is running properly",
            }
        ), 200

    except SQLAlchemyError as e:

        return jsonify(
            {
                "status": "failed",
                "database": "Disconnected",
                "error": str(e),
            }
        ), 500