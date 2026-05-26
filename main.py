from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

post_text = input("Paste LinkedIn post text: ")

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "system",
            "content": "You generate short, professional LinkedIn comments."
        },
        {
            "role": "user",
            "content": f"Generate 3 LinkedIn comments for this post:\n\n{post_text}"
        }
    ]
)

print("\nGenerated comments:\n")
print(response.choices[0].message.content)