import pandas as pd
from pathlib import Path

CSV_PATH = "data/linkedin_posts.csv"


def save_posts(posts):

    path = Path(CSV_PATH)

    df = pd.DataFrame(posts)

    if path.exists():

        old_df = pd.read_csv(path)

        df = pd.concat(
            [old_df, df],
            ignore_index=True
        )

    df.to_csv(
        CSV_PATH,
        index=False
    )

    print(
        f"Saved {len(posts)} posts to CSV"
    )