from .config import CASE_SENSITIVE, MATCH_MODE


def filter_posts_by_keywords(
    posts: list,
    keywords: list,
    case_sensitive: bool = CASE_SENSITIVE,
    match_mode: str = MATCH_MODE
) -> list:
    """
    Filter posts based on the provided keywords.

    - Empty keywords list returns all posts.
    - match_mode="any": matches if at least one keyword is found.
    - match_mode="all": matches only if all keywords are found.
    - case_sensitive=False enables case-insensitive matching.

    Args:
        posts: List of post dictionaries containing a "content" field.
        keywords: Keywords to search for.
        case_sensitive: Whether keyword matching is case-sensitive.
        match_mode: Matching strategy ("any" or "all").

    Returns:
        List of posts that satisfy the keyword filter.
    """

    if not keywords:
        return posts

    filtered = []

    for post in posts:
        text = post.get("content", "")

        if not case_sensitive:
            text = text.lower()
            compare_keywords = [kw.lower() for kw in keywords]
        else:
            compare_keywords = keywords

        if match_mode == "all":
            match = all(kw in text for kw in compare_keywords)
        else:  
            match = any(kw in text for kw in compare_keywords)

        if match:
            filtered.append(post)

    print(
        f"[KeywordFilter] {len(filtered)}/{len(posts)} posts "
        f"matched keywords: {keywords} "
        f"(mode={match_mode}, case_sensitive={case_sensitive})"
    )

    return filtered