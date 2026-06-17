import requests

API_URL = "http://127.0.0.1:8000/comments/generate"


def generate_comment(post_text, goal=""):

    response = requests.post(
        API_URL,
        json={
            "post_text": post_text,
            "goal": goal
        }
    )

    response.raise_for_status()

    data = response.json()

    return data["comment"]