"""
fetch_substack.py
-----------------
Fetches the latest 3 posts from Amrita's Substack RSS feed
and updates the README.md between the markers:
  <!-- SUBSTACK_POSTS_START -->
  <!-- SUBSTACK_POSTS_END -->

Run locally:  python scripts/fetch_substack.py
Run by CI:    automatically via GitHub Actions
"""

import re
import sys
from datetime import datetime

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: pip install feedparser")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
SUBSTACK_RSS  = "https://amritasagardevops.substack.com/feed"
README_PATH   = "README.md"
MAX_POSTS     = 3
START_MARKER  = "<!-- SUBSTACK_POSTS_START -->"
END_MARKER    = "<!-- SUBSTACK_POSTS_END -->"

EMOJI_CYCLE   = ["📝", "🔧", "☁️", "🤖", "⚡", "🚀", "🏗️", "🔍"]

# ── Fetch feed ────────────────────────────────────────────────────────────────
def fetch_posts():
    print(f"Fetching RSS feed: {SUBSTACK_RSS}")
    feed = feedparser.parse(SUBSTACK_RSS)

    if not feed.entries:
        print("WARNING: No entries found. Feed may be empty or unavailable.")
        return []

    posts = []
    for i, entry in enumerate(feed.entries[:MAX_POSTS]):
        title   = entry.get("title", "Untitled").strip()
        link    = entry.get("link", "#").strip()
        summary = entry.get("summary", "").strip()

        # Clean HTML tags from summary
        summary = re.sub(r"<[^>]+>", "", summary)
        summary = summary[:120].strip()
        if len(summary) > 119:
            summary += "..."

        # Parse date
        published = entry.get("published_parsed")
        if published:
            date_str = datetime(*published[:6]).strftime("%b %d, %Y")
        else:
            date_str = "Recent"

        emoji = EMOJI_CYCLE[i % len(EMOJI_CYCLE)]
        posts.append({
            "title":   title,
            "link":    link,
            "summary": summary,
            "date":    date_str,
            "emoji":   emoji,
        })
        print(f"  ✓ Found: {title} ({date_str})")

    return posts

# ── Build markdown block ──────────────────────────────────────────────────────
def build_markdown(posts):
    if not posts:
        return (
            f"{START_MARKER}\n"
            "> ⚠️ Could not load posts — check back soon.\n"
            f"{END_MARKER}"
        )

    lines = [START_MARKER]
    lines.append("")  # blank line after marker

    for p in posts:
        lines.append(f"{p['emoji']} **[{p['title']}]({p['link']})**")
        if p["summary"]:
            lines.append(f"  > {p['summary']}")
        lines.append(f"  `{p['date']}`")
        lines.append("")

    # Auto-update timestamp (Singapore time approximation)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines.append(
        f"> 🔄 *Auto-updated {timestamp} via GitHub Actions · "
        f"[Read all posts →](https://amritasagardevops.substack.com)*"
    )
    lines.append("")
    lines.append(END_MARKER)

    return "\n".join(lines)

# ── Update README ─────────────────────────────────────────────────────────────
def update_readme(new_block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print("ERROR: Markers not found in README.md")
        print(f"  Add these two lines to your README where you want posts to appear:")
        print(f"  {START_MARKER}")
        print(f"  {END_MARKER}")
        sys.exit(1)

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL
    )

    updated = pattern.sub(new_block, content)

    if updated == content:
        print("README unchanged — posts are already up to date.")
    else:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated)
        print("✅ README.md updated successfully.")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    posts    = fetch_posts()
    block    = build_markdown(posts)
    update_readme(block)
