from dotenv import load_dotenv
import os

load_dotenv()

CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")