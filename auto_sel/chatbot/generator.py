import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHATBOT_URL   = os.getenv("CHATBOT_URL")    # e.g. https://api.groq.com/openai/v1/chat/completions
CHATBOT_API   = os.getenv("CHATBOT_API")    # your Groq API key
CHATBOT_MODEL = os.getenv("CHATBOT_MODEL")  # e.g. llama3-8b-8192

SYSTEM_PROMPT = """You are a professional LinkedIn engagement specialist.
Your job is to write thoughtful, genuine comments on LinkedIn posts.

Rules:
- Keep comments between 2-4 sentences
- Sound human, not AI-generated
- Be specific to the post content — no generic praise
- Add value: a question, insight, or personal take
- No hashtags, no emojis unless the post uses them
- Never start with "Great post!" or "Amazing!" or similar openers
- Output ONLY the comment text, nothing else"""


def generate_comment(post_content: str) -> str:
    """
    Send a post to Groq and return a generated LinkedIn comment.
    Returns empty string on failure so the CSV row is left blank.
    """
    if not all([CHATBOT_URL, CHATBOT_API, CHATBOT_MODEL]):
        raise EnvironmentError(
            "Missing one or more env vars: CHATBOT_URL, CHATBOT_API, CHATBOT_MODEL"
        )

    headers = {
        "Authorization": f"Bearer {CHATBOT_API}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": CHATBOT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Write a LinkedIn comment for this post:\n\n{post_content[:2000]}"
                ),
            },
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    try:
        response = requests.post(CHATBOT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP error: {e.response.status_code} — {e.response.text[:200]}")
    except requests.exceptions.Timeout:
        print("  ✗ Request timed out")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")

    return ""