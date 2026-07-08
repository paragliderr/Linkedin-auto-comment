import pandas as pd
from utils.app_paths import POSTS_CSV_PATH

CSV_PATH = POSTS_CSV_PATH


def mark_as_posted(post_url):

    df = pd.read_csv(CSV_PATH)

    row_index = df.index[
        df["post_url"] == post_url
    ]

    if len(row_index) == 0:
        return False

    row_index = row_index[0]

    df.loc[row_index, "status"] = "posted"

    df.to_csv(CSV_PATH, index=False)

    return True