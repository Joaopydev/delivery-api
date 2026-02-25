from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.emails.dto import EmailMessageDto

TEMPLATES_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
)


class EmailFactory:

    @staticmethod
    def build_message(to: str, data: dict[str, any], template: str, subject: str) -> EmailMessageDto:

        template = env.get_template(template)
        html_content = template.render(**data)

        return EmailMessageDto(
            to=to,
            subject=subject,
            html_content=html_content,
        )