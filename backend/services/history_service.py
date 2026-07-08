import pandas as pd
from utils.app_paths import POSTS_CSV_PATH

CSV_PATH = POSTS_CSV_PATH


def get_saved_comments():

    if not CSV_PATH.exists():
        return []

    df = pd.read_csv(CSV_PATH)

    return df.fillna("").to_dict(orient="records")