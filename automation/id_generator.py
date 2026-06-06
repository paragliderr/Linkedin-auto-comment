import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "linkedin_posts.csv"


def get_next_id():

    if not CSV_PATH.exists():
        return 1

    df = pd.read_csv(CSV_PATH)

    if "id" not in df.columns:
        return len(df) + 1

    return int(df["id"].max()) + 1