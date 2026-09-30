import json

from openai import OpenAI

from core.config import settings


class BookingExtractor:

    def __init__(self) -> None:

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.openai_chat_model

    def extract(
        self,
        conversation: list[dict[str, str]],
    ) -> dict:

        system_prompt = """
You are an interview booking assistant.

Determine whether the user is trying to book
an interview.

If the user is NOT trying to book an interview,
return:

{
    "is_booking": false
}

If the user IS trying to book an interview,
extract these fields when available:

- name
- email
- date
- time

Return ONLY valid JSON.

If a field is missing, return null.

Expected format:

{
    "is_booking": true,
    "name": "John Doe",
    "email": "john@example.com",
    "date": "2026-10-05",
    "time": "14:00"
}

Do not invent missing information.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        messages.extend(conversation)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            response_format={
                "type": "json_object"
            },
        )

        content = (
            response.choices[0]
            .message
            .content
        )

        if not content:
            return {
                "is_booking": False
            }

        try:
            return json.loads(content)

        except json.JSONDecodeError:

            return {
                "is_booking": False
            }
