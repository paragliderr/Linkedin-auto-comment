from auth.login import login_and_save_session
from auth.session import load_session
from scraper.fetch_posts import fetch_posts
from scraper.save_csv import save_posts


def pick_posts(posts: list[dict]) -> list[dict]:
    """
    Show the user a numbered list of fetched posts and let them choose
    which ones to keep before saving / generating comments.
    """
    print("\n" + "=" * 60)
    print(f"  {len(posts)} posts fetched. Choose which to keep.\n")

    for i, post in enumerate(posts, 1):
        preview = post["content"][:120].replace("\n", " ")
        url_tag = "✓ URL" if post.get("post_url") else "✗ no URL"
        print(f"  [{i:2d}] ({url_tag})  {preview}…")

    print("\n" + "=" * 60)
    print("Enter post numbers separated by commas, or press Enter to keep ALL.")

    raw = input("Enter here: ").strip()

    if not raw:
        return posts

    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(posts):
                selected.append(posts[idx])
            else:
                print(f"  ⚠  Skipping out-of-range index {part}")
        else:
            print(f"  ⚠  Ignoring non-numeric input '{part}'")

    print(f"\n{len(selected)} post(s) selected.")
    return selected


def main():
    print("\n────────────────────────────────")
    print("  LinkedIn Comment Generator")
    print("────────────────────────────────")
    print("\n1. Login & save session")
    print("2. Fetch posts -> pick -> save CSV\n")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        login_and_save_session()

    elif choice == "2":
        driver = load_session()
        try:
            posts = fetch_posts(driver)

            if not posts:
                print("\nNo posts collected. Try scrolling manually first, or re-login.")
                return

            selected = pick_posts(posts)

            if not selected:
                print("\nNo posts selected — nothing saved.")
                return

            save_posts(selected)
            print("\nDone! Open data/posts.csv to review.")

        finally:
            driver.quit()

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()