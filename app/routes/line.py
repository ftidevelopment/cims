import hashlib
import hmac
import base64
import requests

from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)

from flask import (
    Blueprint,
    request,
    current_app,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
)

from flask_login import login_required, current_user

from app.models.employee import Employee
from app.core.transaction_manager import TransactionManager


line_bp = Blueprint(
    "line",
    __name__,
    url_prefix="/line",
)


# ==========================================================
# Temporary LINE User ID Storage
#
# Used only for testing / confirmation.
#
# The latest LINE User ID received from webhook
# will be stored here temporarily.
#
# NOTE:
# This data will be lost when Flask is restarted.
# ==========================================================

latest_line_user_id = None
latest_line_event_type = None


# ==========================================================
# Helper - Verify LINE Webhook Signature
# ==========================================================

def verify_signature(
    body,
    signature,
    channel_secret,
):

    if not signature:
        return False

    hash_value = hmac.new(
        channel_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()

    expected_signature = base64.b64encode(
        hash_value
    ).decode("utf-8")

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


# ==========================================================
# Helper - Create Link Code
# ==========================================================

def create_link_code(employee_id):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    token = serializer.dumps({
        "employee_id": employee_id
    })

    return token


# ==========================================================
# Helper - Read Link Code
# ==========================================================

def read_link_code(token):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    try:

        data = serializer.loads(
            token,
            max_age=300,
        )

        return data.get(
            "employee_id"
        )

    except (
        BadSignature,
        SignatureExpired,
    ):

        return None


# ==========================================================
# Helper - Create Secure Connect Token
# ==========================================================

def create_connect_token(employee_id):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    token = serializer.dumps({
        "employee_id": employee_id,
    })

    return token


# ==========================================================
# Helper - Read Secure Connect Token
# ==========================================================

def read_connect_token(token):

    if not token:
        return None

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

    try:

        data = serializer.loads(
            token,
            max_age=300,
        )

        return data.get(
            "employee_id"
        )

    except (
        BadSignature,
        SignatureExpired,
    ):

        return None


# ==========================================================
# Helper - Verify LINE ID Token
# ==========================================================

def verify_line_id_token(id_token):

    if not id_token:
        raise ValueError(
            "LINE ID Token is required."
        )

    channel_id = current_app.config.get(
        "LINE_LOGIN_CHANNEL_ID"
    )

    if not channel_id:
        raise ValueError(
            "LINE_LOGIN_CHANNEL_ID "
            "is not configured."
        )

    response = requests.post(
        "https://api.line.me/oauth2/v2.1/verify",
        data={
            "id_token": id_token,
            "client_id": channel_id,
        },
        timeout=10,
    )

    if response.status_code != 200:

        raise ValueError(
            "LINE ID Token verification failed: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    data = response.json()

    return data


# ==========================================================
# LINE User ID Confirmation Page
#
# Used during testing to obtain the LINE User ID
# without checking the Flask terminal.
# ==========================================================

@line_bp.route(
    "/user-id-confirmation",
    methods=["GET"]
)
@login_required
def user_id_confirmation():

    return render_template(
        "line/user_id_confirmation.html"
    )


# ==========================================================
# Get Latest LINE User ID
#
# This endpoint is called by the HTML page
# periodically using JavaScript.
# ==========================================================

@line_bp.route(
    "/latest-user-id",
    methods=["GET"]
)
@login_required
def latest_user_id():

    return jsonify({
        "status": "success",
        "line_user_id": latest_line_user_id,
        "event_type": latest_line_event_type,
    }), 200


# ==========================================================
# LIFF Page
#
# This page is opened from LINE after scanning
# the QR Code displayed by CIMS.
#
# IMPORTANT:
# The connect_token may be temporarily moved by LINE
# into liff.state during LIFF initialization.
#
# Therefore, do NOT validate connect_token on the
# server before liff.init() is completed.
# ==========================================================

@line_bp.route(
    "/liff",
    methods=["GET"]
)
def liff():

    # ------------------------------------------------------
    # Get LIFF ID
    # ------------------------------------------------------

    liff_id = current_app.config.get(
        "LINE_LIFF_ID"
    )

    if not liff_id:

        return render_template(
            "line/liff.html",
            employee=None,
            connect_token=None,
            liff_id=None,
            error=(
                "LINE_LIFF_ID "
                "is not configured."
            ),
        )

    # ------------------------------------------------------
    # Render LIFF page
    #
    # Do not validate connect_token here.
    # The token will be read by JavaScript AFTER
    # liff.init() has completed.
    # ------------------------------------------------------

    return render_template(
        "line/liff.html",
        employee=None,
        connect_token=None,
        liff_id=liff_id,
        error=None,
    )


# ==========================================================
# Connect LINE Page
#
# NEW METHOD
#
# Employee opens this page from CIMS PC.
# CIMS generates a temporary secure token and
# displays a QR Code containing the LIFF URL.
# ==========================================================

@line_bp.route(
    "/connect",
    methods=["GET"]
)
@login_required
def connect():

    # ------------------------------------------------------
    # Get Employee ID from logged-in user
    # ------------------------------------------------------

    employee_id = current_user.employee_id

    if not employee_id:

        flash(
            "Employee account is not linked.",
            "danger"
        )

        return redirect(
            url_for("dashboard.my_dashboard")
        )

    # ------------------------------------------------------
    # Find Employee
    # ------------------------------------------------------

    employee = Employee.query.get(
        employee_id
    )

    if not employee:

        flash(
            "Employee not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard.my_dashboard")
        )

    # ------------------------------------------------------
    # Check LINE LIFF ID
    # ------------------------------------------------------

    liff_id = current_app.config.get(
        "LINE_LIFF_ID"
    )

    if not liff_id:

        flash(
            "LINE LIFF ID is not configured.",
            "danger"
        )

        return redirect(
            url_for("dashboard.my_dashboard")
        )

    # ------------------------------------------------------
    # Already Connected
    # ------------------------------------------------------

    if employee.line_user_id:

        return render_template(
            "line/connect.html",
            employee=employee,
            connected=True,
        )

    # ------------------------------------------------------
    # Create temporary secure token
    # ------------------------------------------------------

    connect_token = create_connect_token(
        employee.id
    )

    # ------------------------------------------------------
    # Build LIFF URL
    #
    # Example:
    #
    # https://liff.line.me/2011545711-maaoYrbv
    # ?connect_token=xxxxxxxx
    #
    # ------------------------------------------------------

    liff_url = (
        f"https://liff.line.me/"
        f"{liff_id}"
        f"?connect_token={connect_token}"
    )

    # ------------------------------------------------------
    # Render Connect Page
    # ------------------------------------------------------

    return render_template(
        "line/connect.html",
        employee=employee,
        connected=False,
        connect_token=connect_token,
        liff_url=liff_url,
    )


# ==========================================================
# LINE Webhook
#
# Existing webhook.
#
# This is still required for LINE Messaging API.
#
# NEW:
# Every LINE User ID received from the webhook
# will also be stored temporarily so that the
# User ID Confirmation page can display it.
# ==========================================================

@line_bp.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    global latest_line_user_id
    global latest_line_event_type

    body = request.get_data()

    signature = request.headers.get(
        "X-Line-Signature"
    )

    channel_secret = current_app.config.get(
        "LINE_CHANNEL_SECRET"
    )

    # ------------------------------------------------------
    # Check Channel Secret
    # ------------------------------------------------------

    if not channel_secret:

        return jsonify({
            "status": "error",
            "message": (
                "LINE_CHANNEL_SECRET "
                "is not configured."
            ),
        }), 500

    # ------------------------------------------------------
    # Verify LINE Signature
    # ------------------------------------------------------

    if not verify_signature(
        body,
        signature,
        channel_secret,
    ):

        return jsonify({
            "status": "error",
            "message": (
                "Invalid LINE signature."
            ),
        }), 401

    # ------------------------------------------------------
    # Read JSON
    # ------------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}

    events = data.get(
        "events",
        []
    )

    # ------------------------------------------------------
    # Process Events
    # ------------------------------------------------------

    for event in events:

        event_type = event.get(
            "type"
        )

        source = event.get(
            "source",
            {}
        )

        line_user_id = source.get(
            "userId"
        )

        print(
            "================================"
        )

        print(
            "LINE WEBHOOK RECEIVED"
        )

        print(
            "Event Type:",
            event_type
        )

        print(
            "LINE User ID:",
            line_user_id
        )

        # --------------------------------------------------
        # Store latest LINE User ID
        #
        # This is used by the User ID Confirmation page.
        # --------------------------------------------------

        if line_user_id:

            latest_line_user_id = (
                line_user_id
            )

            latest_line_event_type = (
                event_type
            )

        # --------------------------------------------------
        # Only process message event
        # --------------------------------------------------

        if event_type != "message":

            continue

        message = event.get(
            "message",
            {}
        )

        if message.get(
            "type"
        ) != "text":

            continue

        message_text = message.get(
            "text",
            ""
        ).strip()

        print(
            "Message:",
            message_text
        )

        # --------------------------------------------------
        # Check OLD Connection Code
        #
        # Keep this temporarily as backup.
        # --------------------------------------------------

        employee_id = read_link_code(
            message_text
        )

        if not employee_id:

            print(
                "Not a valid CIMS LINE "
                "connect code."
            )

            continue

        # --------------------------------------------------
        # Find Employee
        # --------------------------------------------------

        employee = Employee.query.get(
            employee_id
        )

        if not employee:

            print(
                "Employee not found:",
                employee_id
            )

            continue

        # --------------------------------------------------
        # Check Existing LINE Connection
        # --------------------------------------------------

        if employee.line_user_id:

            print(
                "Employee already has "
                "LINE User ID."
            )

            continue

        # --------------------------------------------------
        # Check LINE User ID
        # --------------------------------------------------

        if not line_user_id:

            print(
                "LINE User ID not found "
                "in webhook source."
            )

            continue

        # --------------------------------------------------
        # Check whether LINE account is already
        # connected to another employee
        # --------------------------------------------------

        existing_employee = (
            Employee.query
            .filter(
                Employee.line_user_id
                == line_user_id,
                Employee.id
                != employee.id,
            )
            .first()
        )

        if existing_employee:

            print(
                "LINE account is already "
                "connected to another employee:"
            )

            print(
                existing_employee.full_name
            )

            continue

        # --------------------------------------------------
        # Save LINE User ID
        # --------------------------------------------------

        try:

            employee.line_user_id = (
                line_user_id
            )

            transaction = TransactionManager()

            transaction.commit()

            print(
                "LINE CONNECTED SUCCESSFULLY"
            )

            print(
                "Employee:",
                employee.full_name
            )

            print(
                "LINE User ID:",
                line_user_id
            )

        except Exception as ex:

            print(
                "FAILED TO CONNECT LINE:",
                ex
            )

    print(
        "================================"
    )

    return jsonify({
        "status": "success"
    }), 200


# ==========================================================
# LIFF Connect
#
# NEW METHOD
#
# Receives:
# - connect_token
# - LINE ID Token
#
# Server verifies LINE ID Token and
# saves LINE User ID to Employee.
# ==========================================================

@line_bp.route(
    "/liff/connect",
    methods=["POST"]
)
def liff_connect():

    # ------------------------------------------------------
    # Read JSON request
    # ------------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}

    connect_token = (
        data.get("connect_token")
        or ""
    ).strip()

    id_token = (
        data.get("id_token")
        or ""
    ).strip()

    # ------------------------------------------------------
    # Validate connect token
    # ------------------------------------------------------

    employee_id = read_connect_token(
        connect_token
    )

    if not employee_id:

        return jsonify({
            "status": "error",
            "message": (
                "Connection token is "
                "missing, expired, or invalid."
            ),
        }), 400

    # ------------------------------------------------------
    # Find Employee
    # ------------------------------------------------------

    employee = Employee.query.get(
        employee_id
    )

    if not employee:

        return jsonify({
            "status": "error",
            "message": "Employee not found.",
        }), 404

    # ------------------------------------------------------
    # Check existing LINE connection
    # ------------------------------------------------------

    if employee.line_user_id:

        return jsonify({
            "status": "error",
            "message": (
                "This employee is already "
                "connected to LINE."
            ),
        }), 400

    # ------------------------------------------------------
    # Verify LINE ID Token
    # ------------------------------------------------------

    try:

        line_data = verify_line_id_token(
            id_token
        )

    except Exception as ex:

        return jsonify({
            "status": "error",
            "message": str(ex),
        }), 400

    # ------------------------------------------------------
    # Get verified LINE User ID
    #
    # LINE ID Token "sub" contains
    # the verified LINE User ID.
    # ------------------------------------------------------

    line_user_id = (
        line_data.get("sub")
    )

    if not line_user_id:

        return jsonify({
            "status": "error",
            "message": (
                "LINE User ID was not "
                "returned from LINE."
            ),
        }), 400

    # ------------------------------------------------------
    # Check duplicate LINE account
    # ------------------------------------------------------

    existing_employee = (
        Employee.query
        .filter(
            Employee.line_user_id
            == line_user_id,
            Employee.id
            != employee.id,
        )
        .first()
    )

    if existing_employee:

        return jsonify({
            "status": "error",
            "message": (
                "This LINE account is already "
                "connected to another employee."
            ),
        }), 400

    # ------------------------------------------------------
    # Save LINE User ID
    # ------------------------------------------------------

    try:

        employee.line_user_id = (
            line_user_id
        )

        transaction = TransactionManager()

        transaction.commit()

    except Exception as ex:

        return jsonify({
            "status": "error",
            "message": (
                "Failed to save LINE connection: "
                f"{ex}"
            ),
        }), 500

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    return jsonify({
        "status": "success",
        "message": (
            "LINE account connected successfully."
        ),
        "employee_id": employee.id,
    }), 200