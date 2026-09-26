import click

from app.services.email_service import EmailService


@click.command("test-email")
@click.argument("recipient")
def test_email(recipient):
    """
    Send a test email using the configured mail server.
    """

    try:

        EmailService.send_email(
            recipient=recipient,
            subject="[CIMS] Gmail SMTP Test",
            body="""
This is a test email from CIMS.

If you receive this email, the Gmail SMTP configuration
and EmailService are working correctly.

CIMS - Continuous Improvement Management System
""",
        )

        click.echo(
            f"Email successfully sent to {recipient}"
        )

    except Exception as e:

        click.echo(
            f"Failed to send email: {str(e)}"
        )