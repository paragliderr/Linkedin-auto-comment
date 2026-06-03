from auth.login import login_and_save_session
from auto_sel.auth.session import load_session
from scraper.fetch_posts import fetch_posts
from scraper.save_csv import save_posts


def pick_posts(posts):
    print(f"\n{len(posts)} posts fetched.\n")

    for i, post in enumerate(posts, 1):
        preview = post["content"][:120].replace("\n", " ")
        url = "has URL" if post.get("post_url") else "no URL"
        print(f"  [{i}] ({url}) {preview}...")

    raw = input("\nEnter post numbers to keep (e.g. 1,3,5) or Enter for ALL: ").strip()

    if not raw:
        return posts

    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 0 <= int(part) - 1 < len(posts):
            selected.append(posts[int(part) - 1])

    print(f"{len(selected)} post(s) selected.")
    return selected


def main():
    print("\n1. Login and save session")
    print("2. Scrape posts and save to CSV\n")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        login_and_save_session()

    elif choice == "2":
        driver = load_session()
        try:
            posts = fetch_posts(driver)

            if not posts:
                print("No posts found. Try re-logging in.")
                return

            selected = pick_posts(posts)

            if not selected:
                print("Nothing selected — exiting.")
                return

            save_posts(selected)
            print("Done! Check data/posts.csv")

        finally:
            driver.quit()

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()