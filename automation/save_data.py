import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "linkedin_posts.csv"

def save_posts(posts):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(posts)

    if CSV_PATH.exists():
        old_df = pd.read_csv(CSV_PATH)
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(posts)} posts to CSV")