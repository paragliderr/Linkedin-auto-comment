from Ai_services.chatbot import generate_comment
from Ai_services.comment_assistant import improve_comment

def generate_comment_service(post_text: str) -> str:
    """
    Uses the AI service to generate a LinkedIn comment.
    """

    return generate_comment(post_text)

def improve_comment_service(
    comment: str,
    instruction: str
) -> str:

    return improve_comment(
        comment,
        instruction
    )