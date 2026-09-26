import requests

from flask import current_app


class LineService:

    # =========================================================
    # LINE API
    # =========================================================

    API_URL = (
        "https://api.line.me/v2/bot/message/push"
    )

    MULTICAST_API_URL = (
        "https://api.line.me/v2/bot/message/multicast"
    )

    # LINE multicast maximum recipients per request
    MULTICAST_BATCH_SIZE = 500

    # Request timeout in seconds
    REQUEST_TIMEOUT = 10

    # =========================================================
    # SEND MESSAGE
    # =========================================================

    @staticmethod
    def send_message(
        line_user_id,
        message,
    ):
        """
        Send a LINE message to a single user.
        """

        # ==========================================
        # Validate LINE User ID
        # ==========================================

        if not line_user_id:
            raise ValueError(
                "LINE user ID is required."
            )

        # ==========================================
        # Validate message
        # ==========================================

        if not message:
            raise ValueError(
                "LINE message is required."
            )

        # ==========================================
        # Get LINE access token
        # ==========================================

        access_token = current_app.config.get(
            "LINE_CHANNEL_ACCESS_TOKEN"
        )

        if not access_token:
            raise ValueError(
                "LINE channel access token is not configured."
            )

        # ==========================================
        # Headers
        # ==========================================

        headers = {
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {access_token}"
            ),
        }

        # ==========================================
        # Payload
        # ==========================================

        payload = {
            "to": line_user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message,
                }
            ],
        }

        # ==========================================
        # Send request
        # ==========================================

        response = requests.post(
            LineService.API_URL,
            headers=headers,
            json=payload,
            timeout=LineService.REQUEST_TIMEOUT,
        )

        # ==========================================
        # Check response
        # ==========================================

        if response.status_code != 200:

            raise Exception(
                "LINE API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        return True

    # =========================================================
    # SEND MULTICAST
    # =========================================================

    @staticmethod
    def send_multicast(
        line_user_ids,
        message,
    ):
        """
        Send the same LINE message to multiple users.

        LINE Multicast API supports a maximum of
        500 recipients per request.

        If the number of recipients is greater than
        500, the recipients are automatically divided
        into multiple batches.

        Example:

            1 - 500     -> Request 1
            501 - 1000  -> Request 2
            1001 - 1500 -> Request 3
        """

        # ==========================================
        # Validate recipient list
        # ==========================================

        if not line_user_ids:
            raise ValueError(
                "At least one LINE user ID is required."
            )

        # ==========================================
        # Validate message
        # ==========================================

        if not message:
            raise ValueError(
                "LINE message is required."
            )

        # ==========================================
        # Clean & remove duplicate user IDs
        # ==========================================
        #
        # - Remove None
        # - Remove empty values
        # - Remove spaces
        # - Remove duplicate user IDs
        #
        # dict.fromkeys() keeps the original order.
        # ==========================================

        unique_user_ids = list(
            dict.fromkeys(
                user_id.strip()
                for user_id in line_user_ids
                if user_id and user_id.strip()
            )
        )

        if not unique_user_ids:
            raise ValueError(
                "No valid LINE user IDs found."
            )

        # ==========================================
        # Get LINE access token
        # ==========================================

        access_token = current_app.config.get(
            "LINE_CHANNEL_ACCESS_TOKEN"
        )

        if not access_token:
            raise ValueError(
                "LINE channel access token is not configured."
            )

        # ==========================================
        # Headers
        # ==========================================

        headers = {
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {access_token}"
            ),
        }

        # ==========================================
        # Message payload
        # ==========================================

        message_payload = {
            "type": "text",
            "text": message,
        }

        # ==========================================
        # Send in batches
        # ==========================================
        #
        # Maximum 500 LINE User IDs per
        # multicast request.
        # ==========================================

        total_recipients = len(unique_user_ids)

        for start in range(
            0,
            total_recipients,
            LineService.MULTICAST_BATCH_SIZE,
        ):

            end = (
                start
                + LineService.MULTICAST_BATCH_SIZE
            )

            batch = unique_user_ids[start:end]

            # ======================================
            # Payload
            # ======================================

            payload = {
                "to": batch,
                "messages": [
                    message_payload
                ],
            }

            # ======================================
            # Send multicast request
            # ======================================

            response = requests.post(
                LineService.MULTICAST_API_URL,
                headers=headers,
                json=payload,
                timeout=LineService.REQUEST_TIMEOUT,
            )

            # ======================================
            # Check response
            # ======================================

            if response.status_code != 200:

                raise Exception(
                    "LINE Multicast API error "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

        return True