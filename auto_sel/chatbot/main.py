import os
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.generator import generate_comment

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH   = os.path.join(BASE_DIR, "data", "posts.csv")
DELAY_SECS = 1.5


def main():
    print(f"\nLooking for CSV at: {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        print(f"✗ posts.csv not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype={"generated_comment": "object"})

    # Force the column to string type so we can safely assign text into it
    df["generated_comment"] = df["generated_comment"].astype("object")

    print(f"  Loaded {len(df)} rows, columns: {list(df.columns)}")

    required = {"post_url", "content", "generated_comment"}
    if not required.issubset(df.columns):
        print(f"✗ CSV missing columns. Expected: {required}, Found: {set(df.columns)}")
        return

    needs_comment = df["content"].notna() & (
        df["generated_comment"].isna()
        | (df["generated_comment"].astype(str).str.strip().isin(["", "nan"]))
    )
    targets = df[needs_comment]

    if targets.empty:
        print("✓ All posts already have comments. Nothing to do.")
        return

    print(f"\nGenerating comments for {len(targets)} post(s)...\n")

    for i, (idx, row) in enumerate(targets.iterrows(), 1):
        preview = str(row["content"])[:80].replace("\n", " ")
        print(f"  [{i}/{len(targets)}] {preview}...")

        comment = generate_comment(str(row["content"]))

        if comment:
            df.at[idx, "generated_comment"] = comment
            print(f"           ✓ Comment written")
        else:
            print(f"           ✗ Failed — left blank")

        df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

        if i < len(targets):
            time.sleep(DELAY_SECS)

    filled = df["generated_comment"].notna() & (
        ~df["generated_comment"].astype(str).str.strip().isin(["", "nan"])
    )
    print(f"\n{'─'*50}")
    print(f"  Done! {filled.sum()} / {len(df)} comments written to {CSV_PATH}")
    print(f"{'─'*50}\n")


if __name__ == "__main__":
    main()