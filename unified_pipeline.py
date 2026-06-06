from automation.scrape_posts import scrape_posts
from auto_sel.auth.session import load_session
from auto_sel.scraper.fetch_posts import fetch_posts
from automation.id_generator import get_next_id
from automation.api_client import generate_comment
from automation.save_data import save_posts
from filters import filter_posts_by_keywords          


def run(scraper_type="selenium", keywords=None, match_mode="any"):   
    """
    keywords=None or [] → no filtering, all posts processed
    keywords=["AI","hiring"] → only posts with those words processed
    """

    print("=" * 60)
    print("UNIFIED LINKEDIN COMMENT PIPELINE")
    print("=" * 60)

    if scraper_type == "playwright":
        print("\nFetching posts using Playwright scraper...")
        posts = scrape_posts()

    elif scraper_type == "selenium":
        print("\nFetching posts using Selenium scraper...")
        driver = load_session()
        try:
            posts = fetch_posts(driver)
        finally:
            driver.quit()

    else:
        raise ValueError(f"Unknown scraper type: {scraper_type}")

    if not posts:
        print("No posts found")
        return

    posts = filter_posts_by_keywords(posts, keywords or [], match_mode=match_mode)

    if not posts:
        print("No posts matched the keyword filter")
        return []

    final_posts = []
    next_id = get_next_id()

    for i, post in enumerate(posts):
        print(f"\nGenerating comment for post {i+1}")
        try:

            comment = generate_comment(
                post["content"]
            )

            final_posts.append(
                {
                    "id":next_id,
                    "post_url": post.get("post_url", ""),
                    "post_text": post["content"],
                    "generated_comment": comment,
                    "status": "generated"
                }
            )
            next_id += 1

        except Exception as e:
            print(f"Error: {e}")

            final_posts.append(
                {
                    "id":next_id,
                    "post_url": post.get("post_url", ""),
                    "post_text": post["content"],
                    "generated_comment": "",
                    "status": "error"
                }
            )
            next_id += 1

    save_posts(final_posts)
    print("\nPipeline complete")
    return final_posts


if __name__ == "__main__":
    run()