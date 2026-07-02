from Ai_services.wrapper import (
    generate_comment,
    improve_comment
)

def generate_comment_service(
    post_text: str,
    goal: str = ""
) -> str:
    """
    Uses the AI service to generate a LinkedIn comment.
    """

    return generate_comment(
        post_text,
        goal
    )
    
def improve_comment_service(
    comment: str,
    instruction: str
) -> str:

    return improve_comment(
        comment,
        instruction
    )