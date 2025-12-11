import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from celery import shared_task

load_dotenv()


@shared_task
def send_email(user_email: str, subject: str, html_content: str) -> None:
    message = Mail(
        from_email=os.getenv("STORE_EMAIL"),
        to_emails=user_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        sg.send(message=message)
    except Exception as ex:
        logging.error(msg=f"The email could not be sent: {ex}")

