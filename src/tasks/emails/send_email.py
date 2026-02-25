import logging
from typing import Dict
from dotenv import load_dotenv
from celery import shared_task

import mailtrap as mt

from app.emails.service import EmailService
from app.emails.factory import EmailFactory


load_dotenv()


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_confirmation_email(self, email_data: Dict[str, str]) -> None:
    try:
        message_dto = EmailFactory.build_message(
            to=email_data["to"],
            data={
                "customer_name": email_data["name"],
                "order_number": email_data["order_id"],
            },
            template="order_confirmed.html",
            subject="Confirmação do seu pedido"
        )
        email_service = EmailService()
        email_service.send(message_dto=message_dto)

    except mt.exceptions.MailtrapError as exc:
        logging.error(msg=f"The email could not be sent: {exc} - Trying again")
        raise self.retry(exc=exc)
    except Exception as exc:
        logging.error(f"Unexpected error while sending email: {exc}")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_ready_email(self, email_data: Dict[str, str]) -> None:
    try:
        message_dto = EmailFactory.build_message(
            to=email_data["to"],
            data={
                "customer_name": email_data["name"],
                "order_number": email_data["order_id"],
            },
            template="order_ready.html",
            subject="Seu pedido está a caminho."
        )

        email_service = EmailService()
        email_service.send(message_dto=message_dto)
    except mt.exceptions.MailtrapError as exc:
        logging.error(msg=f"The email could not be sent: {exc} - Trying again")
        raise self.retry(exc=exc)
    except Exception as exc:
        logging.error(f"Unexpected error while sending email: {exc}")


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def confirm_paid_order(self, email_data: Dict[str, str]) -> None:
    try:
        message_dto = EmailFactory.build_message(
            to=email_data["to"],
            data={
                "customer_name": email_data["name"],
                "order_number": email_data["order_id"], 
            },
            template="paid_order.html",
            subject="Confirmação de pagamento do pedido"
        )

        email_service = EmailService()
        email_service.send(message_dto=message_dto)
    except mt.exceptions.MailtrapError as exc:
        logging.error(msg=f"The email could not be sent: {exc} - Trying again")
        raise self.retry(exc=exc)
    except Exception as exc:
        logging.error(f"Unexpected error while sending email: {exc}")



