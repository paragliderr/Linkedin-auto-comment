import threading
import time
import webbrowser

import requests
import uvicorn

from backend.main import app


def start_server():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,   
    )


if __name__ == "__main__":

    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()

    print("Starting LinkedIn Auto Commenter...")

    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:8000")
            break
        except:
            time.sleep(1)

    webbrowser.open("http://127.0.0.1:8000")

    server_thread.join()