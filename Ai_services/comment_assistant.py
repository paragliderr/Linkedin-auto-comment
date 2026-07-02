from openai import OpenAI

from Ai_services.settings_manager import get_ai_settings

def improve_comment(original_comment, instruction):
    settings = get_ai_settings()

    client = OpenAI(
        api_key=settings["api_key"],
        base_url=settings["base_url"]
    )
    response = client.chat.completions.create(
        model=settings["model"],
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