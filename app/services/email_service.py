import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


class EmailService:

    # =========================================================
    # SEND EMAIL
    # =========================================================

    @staticmethod
    def send_email(
        recipient,
        subject,
        body,
        html=False,
    ):
        """
        Send an email to a single recipient
        using the configured SMTP server.
        """

        # ==========================================
        # Validate input
        # ==========================================

        if not recipient:
            raise ValueError(
                "Email recipient is required."
            )

        if not subject:
            raise ValueError(
                "Email subject is required."
            )

        if not body:
            raise ValueError(
                "Email body is required."
            )

        # ==========================================
        # Get mail configuration
        # ==========================================

        mail_server = current_app.config["MAIL_SERVER"]
        mail_port = current_app.config["MAIL_PORT"]
        mail_username = current_app.config["MAIL_USERNAME"]
        mail_password = current_app.config["MAIL_PASSWORD"]
        mail_use_tls = current_app.config["MAIL_USE_TLS"]

        # ==========================================
        # Create email message
        # ==========================================

        message = MIMEMultipart()

        message["From"] = mail_username
        message["To"] = recipient
        message["Subject"] = subject

        content_type = "html" if html else "plain"

        message.attach(
            MIMEText(
                body,
                content_type,
                "utf-8",
            )
        )

        # ==========================================
        # Connect to SMTP server
        # ==========================================

        with smtplib.SMTP(
            mail_server,
            mail_port,
        ) as server:

            # ======================================
            # Enable TLS
            # ======================================

            if mail_use_tls:
                server.starttls()

            # ======================================
            # Login
            # ======================================

            server.login(
                mail_username,
                mail_password,
            )

            # ======================================
            # Send email
            # ======================================

            server.send_message(
                message
            )

        return True

    # =========================================================
    # SEND BULK EMAIL
    # =========================================================

    @staticmethod
    def send_bulk_email(
        recipients,
        subject,
        body,
        html=False,
    ):
        """
        Send one email to multiple recipients
        using a single SMTP connection.

        Recipient email addresses are NOT exposed
        to other recipients.

        This method is intended for bulk/broadcast
        notification.
        """

        # ==========================================
        # Validate recipients
        # ==========================================

        if not recipients:
            raise ValueError(
                "At least one email recipient is required."
            )

        # ==========================================
        # Validate subject
        # ==========================================

        if not subject:
            raise ValueError(
                "Email subject is required."
            )

        # ==========================================
        # Validate body
        # ==========================================

        if not body:
            raise ValueError(
                "Email body is required."
            )

        # ==========================================
        # Clean recipients
        # ==========================================
        #
        # - Remove None
        # - Remove empty string
        # - Remove leading/trailing spaces
        # - Remove duplicate email addresses
        #
        # dict.fromkeys() preserves the original
        # recipient order.
        # ==========================================

        unique_recipients = list(
            dict.fromkeys(
                email.strip()
                for email in recipients
                if email and email.strip()
            )
        )

        if not unique_recipients:
            raise ValueError(
                "No valid email recipients found."
            )

        # ==========================================
        # Get mail configuration
        # ==========================================

        mail_server = current_app.config["MAIL_SERVER"]
        mail_port = current_app.config["MAIL_PORT"]
        mail_username = current_app.config["MAIL_USERNAME"]
        mail_password = current_app.config["MAIL_PASSWORD"]
        mail_use_tls = current_app.config["MAIL_USE_TLS"]

        # ==========================================
        # Create email message
        # ==========================================

        message = MIMEMultipart()

        message["From"] = mail_username

        # -------------------------------------------------
        # Do not expose recipient list.
        #
        # Actual recipients are supplied through
        # SMTP envelope recipients in sendmail().
        # -------------------------------------------------

        message["To"] = mail_username
        message["Subject"] = subject

        content_type = "html" if html else "plain"

        message.attach(
            MIMEText(
                body,
                content_type,
                "utf-8",
            )
        )

        # ==========================================
        # Connect to SMTP server ONCE
        # ==========================================

        with smtplib.SMTP(
            mail_server,
            mail_port,
        ) as server:

            # ======================================
            # Enable TLS
            # ======================================

            if mail_use_tls:
                server.starttls()

            # ======================================
            # Login ONCE
            # ======================================

            server.login(
                mail_username,
                mail_password,
            )

            # ======================================
            # Send to all recipients
            # ======================================
            #
            # sendmail() receives:
            #
            # 1. Sender
            # 2. List of envelope recipients
            # 3. Complete email message
            #
            # Therefore recipient addresses are not
            # placed in the visible To header.
            # ======================================

            server.sendmail(
                mail_username,
                unique_recipients,
                message.as_string(),
            )

        # ==========================================
        # Success
        # ==========================================

        return True