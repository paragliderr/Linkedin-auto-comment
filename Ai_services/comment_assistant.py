from openai import OpenAI

from Ai_services.config import (
    CHATBOT_API_KEY,
    BASE_URL,
    MODEL_NAME
)

client = OpenAI(
    api_key=CHATBOT_API_KEY,
    base_url=BASE_URL
)

def improve_comment(original_comment, instruction):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content":
                """
                You help users improve LinkedIn comments.

                Follow the user's instructions exactly.

                Return only the improved comment.
                """
            },
            {
                "role": "user",
                "content":
                f"""
Current Comment:
{original_comment}

Instruction:
{instruction}
"""
            }
        ]
    )

    return response.choices[0].message.content