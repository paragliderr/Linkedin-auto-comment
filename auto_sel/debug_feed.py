"""
python3 debug_feed2.py
"""
from auth.session import load_session
import time, re

driver = load_session()
driver.get("https://www.linkedin.com/feed/")
input("\n[DEBUG] Wait for feed to fully load, then press Enter...")

# ── 1. Find all <a> tags whose href looks like a LinkedIn post URL ─────────
print("\n=== <a> hrefs that look like post links ===")
anchors = driver.find_elements("css selector", "a[href]")
post_links = set()
for a in anchors:
    href = a.get_attribute("href") or ""
    if any(p in href for p in ["/feed/update/", "/posts/", "/pulse/"]):
        post_links.add(href.split("?")[0])   # strip query params

print(f"Found {len(post_links)} candidate post URLs:")
for link in list(post_links)[:15]:
    print(" ", link)

# ── 2. For the first such anchor, walk UP to find the post container ───────
print("\n=== Parent chain of first post-link anchor ===")
post_anchors = [
    a for a in anchors
    if any(p in (a.get_attribute("href") or "") for p in ["/feed/update/", "/posts/"])
]
print(f"Total post-link anchors: {len(post_anchors)}\n")

for anchor in post_anchors[:3]:
    href = anchor.get_attribute("href")
    print(f"href: {href}")
    chain = driver.execute_script(r"""
        var el = arguments[0];
        var parts = [];
        for (var i = 0; i < 12; i++) {
            if (!el || el === document.body) break;
            var tag = el.tagName.toLowerCase();
            var da = [];
            for (var j = 0; j < el.attributes.length; j++) {
                var a = el.attributes[j];
                da.push(a.name + '=' + a.value.slice(0,60));
            }
            parts.push(tag + ' [' + da.join(', ') + ']');
            el = el.parentElement;
        }
        return parts;
    """, anchor)
    for level, part in enumerate(chain):
        print(f"  {'  ' * level}{part}")
    print()

# ── 3. Check how many text-boxes share the same grandparent as a post link ─
print("\n=== Relationship between text-boxes and post-link anchors ===")
boxes  = driver.find_elements("css selector", "[data-testid='expandable-text-box']")
print(f"Text boxes: {len(boxes)},  Post-link anchors: {len(post_anchors)}")

# Walk up 10 levels from each text-box and see if a post link lives there
matched = 0
for box in boxes[:10]:
    found_url = driver.execute_script(r"""
        var el = arguments[0];
        for (var i = 0; i < 15; i++) {
            if (!el || el === document.body) break;
            var links = el.querySelectorAll('a[href*="/feed/update/"], a[href*="/posts/"]');
            if (links.length > 0) return links[0].href.split('?')[0];
            el = el.parentElement;
        }
        return null;
    """, box)
    status = f"✓ {found_url}" if found_url else "✗ no URL found"
    preview = box.text[:80].replace("\n", " ")
    print(f"  {status}")
    print(f"    text: {preview}")
    if found_url:
        matched += 1

print(f"\nMatched {matched}/{min(10,len(boxes))} text-boxes to a URL")

driver.quit()