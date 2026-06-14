import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "linkedin_posts.csv"


def get_next_id():
    if not CSV_PATH.exists():
        return 1

    df = pd.read_csv(CSV_PATH)

    if "id" not in df.columns or df.empty:
        return len(df) + 1

    ids = pd.to_numeric(df["id"], errors="coerce").dropna()
    return int(ids.max()) + 1 if not ids.empty else 1