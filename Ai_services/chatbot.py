from openai import OpenAI

from Ai_services.settings_manager import get_ai_settings

from Ai_services.prompt import COMMENT_PROMPT


def generate_comment(post, goal=""):
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
                "content": COMMENT_PROMPT
            },
            {
                "role": "user",
                "content":
                f"""
Goal:
{goal}

LinkedIn Post:
{post}
"""
            }
        ]
    )

    comment = response.choices[0].message.content.strip()
    comment = comment.strip('"').strip("'")
    
    return comment