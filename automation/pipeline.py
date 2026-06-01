from automation.scrape_posts import scrape_posts
from automation.api_client import generate_comment
from automation.save_data import save_posts


def run_pipeline():

    print("=" * 50)
    print("Starting Pipeline")
    print("=" * 50)

    posts = scrape_posts()

    final_posts = []

    for i, post in enumerate(posts):

        print(f"\nProcessing Post {i+1}")

        text = post["post_text"]

        try:

            comment = generate_comment(text)

            print("Comment generated")

            final_posts.append(
                {
                    "post_text": text,
                    "generated_comment": comment,
                    "status": "generated"
                }
            )

        except Exception as e:

            print(f"ERROR: {e}")

            final_posts.append(
                {
                    "post_text": text,
                    "generated_comment": "",
                    "status": "error"
                }
            )

    save_posts(final_posts)

    print("\nPipeline Complete")


if __name__ == "__main__":
    run_pipeline()