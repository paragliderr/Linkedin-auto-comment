from openai import OpenAI

from Ai_services.config import (
    CHATBOT_API_KEY,
    BASE_URL,
    MODEL_NAME
)

from Ai_services.prompt import COMMENT_PROMPT

client = OpenAI(
    api_key=CHATBOT_API_KEY,
    base_url=BASE_URL
)

def generate_comment(post):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": COMMENT_PROMPT
            },
            {
                "role": "user",
                "content": f"LinkedIn Post:\n{post}"
            }
        ]
    )
    return response.choices[0].message.content