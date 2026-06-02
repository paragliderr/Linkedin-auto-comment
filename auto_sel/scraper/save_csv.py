import os
import pandas as pd


def save_posts(posts: list[dict], path: str = "data/posts.csv") -> None:
    """
    Save scraped posts to CSV.

    Columns (in order):
      post_url          – direct link to the LinkedIn post
      content           – full post text
      generated_comment – blank; filled in by the AI step later
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    rows = []
    for post in posts:
        rows.append({
            "post_url": post.get("post_url", ""),
            "content": post.get("content", ""),
            "generated_comment": "",        
        })

    df = pd.DataFrame(rows, columns=["post_url", "content", "generated_comment"])
    df.to_csv(path, index=False, encoding="utf-8-sig")   

    print(f"\nSaved {len(rows)} posts → {path}")
    print(f"  Rows with URL : {df['post_url'].astype(bool).sum()}")
    print(f"  Rows missing URL: {(~df['post_url'].astype(bool)).sum()}")