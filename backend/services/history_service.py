import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "linkedin_posts.csv"


def get_saved_comments():

    if not CSV_PATH.exists():
        return []

    df = pd.read_csv(CSV_PATH)

    return df.fillna("").to_dict(orient="records")