from Ai_services.chatbot import generate_comment as chatbot_generate_comment
from Ai_services.comment_assistant import improve_comment as chatbot_improve_comment
from Ai_services.settings_manager import get_ai_settings


def generate_comment(post_text: str, goal: str = ""):
    get_ai_settings()  # validates and prepares settings
    return chatbot_generate_comment(post_text, goal)


def improve_comment(comment: str, instruction: str):
    get_ai_settings()
    return chatbot_improve_comment(comment, instruction)