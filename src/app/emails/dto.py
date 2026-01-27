from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmailMessageDto:
    to: List[str]
    subject: str
    html_content: str
    text_content: Optional[str] = None