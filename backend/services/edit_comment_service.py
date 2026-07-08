import pandas as pd
from utils.app_paths import POSTS_CSV_PATH

CSV_PATH = POSTS_CSV_PATH

def update_comment(comment_id, edited_comment):

    df = pd.read_csv(CSV_PATH)

    row_index = df.index[df["id"] == comment_id]

    if len(row_index) == 0:
        return False

    row_index = row_index[0]

    df.loc[row_index, "generated_comment"] = edited_comment
    df.loc[row_index, "status"] = "edited"

    df.to_csv(CSV_PATH, index=False)

    return True