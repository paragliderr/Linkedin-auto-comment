import uuid
import threading
import pandas as pd
from utils.app_paths import POSTS_CSV_PATH
from automation.scrape_posts import scrape_posts
from auto_sel.auth.session import load_session
from auto_sel.scraper.fetch_posts import fetch_posts
from automation.id_generator import get_next_id
from automation.api_client import generate_comment
from automation.save_data import save_posts
from filters import filter_posts_by_keywords

_jobs: dict = {}


def get_job(job_id: str):
    return _jobs.get(job_id)


def _run_pipeline(job_id: str, scraper_type: str, keywords: list, match_mode: str, goal: str):
    _jobs[job_id] = {"status": "running", "result": None, "error": None}

    try:
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
            _jobs[job_id] = {"status": "done", "result": [], "error": "No posts found"}
            return

        posts = filter_posts_by_keywords(posts, keywords or [], match_mode=match_mode)
        if not posts:
            _jobs[job_id] = {"status": "done", "result": [], "error": "No posts matched keywords"}
            return
        
        
        CSV_PATH = POSTS_CSV_PATH
        existing_urls = set()
        
        if CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH)
            
            if "post_url" in df.columns:
                  existing_urls = set(
                     df["post_url"]
                     .dropna()
                     .astype(str)
                     .str.strip()
                  )
        original_count = len(posts)          
        posts = [
             post
             for post in posts
             if post.get("post_url", "").strip()
              not in existing_urls
        ]
        print(
             f"Skipped {original_count - len(posts)} duplicate posts"
        )
        
        print(
             f"New posts after duplicate check: {len(posts)}"
        )
        if not posts:
            _jobs[job_id] = {
                 "status": "done",
                 "result": [],
                 "error": "All posts already exist"
            }
            
            return
       

        final_posts = []
        next_id = get_next_id()

        for i, post in enumerate(posts):
            print(f"Generating comment for post {i + 1}/{len(posts)}")
            try:
                comment = generate_comment(post["content"], goal)
                status = "generated"
            except Exception as e:
                print(f"Error on post {i + 1}: {e}")
                comment = ""
                status = "error"

            final_posts.append({
                "id": next_id,
                "post_url": post.get("post_url", ""),
                "post_text": post["content"],
                "generated_comment": comment,
                "status": status,
            })
            next_id += 1

        save_posts(final_posts)
        print("\nPipeline complete")
        _jobs[job_id] = {"status": "done", "result": final_posts, "error": None}

    except Exception as e:
        print(f"Pipeline failed: {e}")
        _jobs[job_id] = {"status": "error", "result": None, "error": str(e)}


def run(scraper_type="selenium", keywords=None, match_mode="any", goal="") -> str:
    job_id = str(uuid.uuid4())
    threading.Thread(
        target=_run_pipeline,
        args=(job_id, scraper_type, keywords, match_mode, goal),
        daemon=True
    ).start()
    return job_id


if __name__ == "__main__":
    import time
    job_id = run()
    print(f"Job started: {job_id}")
    while True:
        job = get_job(job_id)
        if job and job["status"] in ("done", "error"):
            print(job)
            break
        time.sleep(2)