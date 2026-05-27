from Ai_services.chatbot import generate_comment


def generate_comment_service(post_text: str) -> str:
    """
    Uses the AI service to generate a LinkedIn comment.
    """

    return generate_comment(post_text)