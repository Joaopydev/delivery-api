import os
import mailtrap as mt

from app.emails.dto import EmailMessageDto


class EmailService:

    def __init__(self):

        self.api_token = os.environ.get("MAILTRAP_API_TOKEN")
        self.email_service = mt.MailtrapClient(token=self.api_token, sandbox=True, inbox_id=4260001)
        self.store_email = os.environ.get("STORE_EMAIL")

    def send(self, message_dto: EmailMessageDto) -> None:
        
        mail = mt.Mail(
            sender=mt.Address(email=self.store_email),
            to=[mt.Address(email=message_dto.to)],
            subject=message_dto.subject,
            html=message_dto.html_content,
        )

        self.email_service.send(mail)