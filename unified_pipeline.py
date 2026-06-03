from auto_sel.auth.session import load_session
from auto_sel.scraper.fetch_posts import fetch_posts

from automation.api_client import generate_comment
from automation.save_data import save_posts


def run():

    print("=" * 60)
    print("UNIFIED LINKEDIN COMMENT PIPELINE")
    print("=" * 60)

    driver = load_session()

    try:

        print("\nFetching posts using Selenium scraper...")

        posts = fetch_posts(driver)

    finally:
        driver.quit()

    if not posts:
        print("No posts found")
        return

    final_posts = []

    for i, post in enumerate(posts):

        print(f"\nGenerating comment for post {i+1}")

        try:

            comment = generate_comment(
                post["content"]
            )

            final_posts.append(
                {
                    "post_url": post.get("post_url", ""),
                    "post_text": post["content"],
                    "generated_comment": comment,
                    "status": "generated"
                }
            )

        except Exception as e:

            print(f"Error: {e}")

            final_posts.append(
                {
                    "post_url": post.get("post_url", ""),
                    "post_text": post["content"],
                    "generated_comment": "",
                    "status": "error"
                }
            )

    save_posts(final_posts)

    print("\nPipeline complete")


if __name__ == "__main__":
    run()



