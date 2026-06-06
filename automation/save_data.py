import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "linkedin_posts.csv"


def save_posts(posts):

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame(posts)

    if CSV_PATH.exists():

        old_df = pd.read_csv(CSV_PATH)

        if "id" not in old_df.columns:
            old_df.insert(
                0,
                "id",
                range(1, len(old_df) + 1)
            )

        df = pd.concat(
            [old_df, new_df],
            ignore_index=True
        )

    else:

        df = new_df

    if "id" in df.columns:
     df["id"] = range(1, len(df) + 1)
    df.to_csv(
        CSV_PATH,
        index=False
    )

    print(f"Saved {len(posts)} posts to CSV")