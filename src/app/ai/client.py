from typing import Dict, Any, List
from openai import OpenAI

class AIClient:

    def __init__(self):
        
        self.client = OpenAI()

    def chat(self, messages: List[Dict[str, Any]]) -> str:

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content