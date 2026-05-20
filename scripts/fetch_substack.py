"""
fetch_substack.py  v2
---------------------
Fetches latest 3 posts from Substack RSS.
- Tries multiple URL formats automatically
- Shows "coming soon" placeholder if no posts published yet
- Never shows the ugly warning message
"""

import re, sys
from datetime import datetime

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed.")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
SUBSTACK_USERNAME = "amritasagardevops"   # ← only change this if username changes
README_PATH       = "README.md"
MAX_POSTS         = 3
START_MARKER      = "<!-- SUBSTACK_POSTS_START -->"
END_MARKER        = "<!-- SUBSTACK_POSTS_END -->"
SUBSTACK_URL      = f"https://{SUBSTACK_USERNAME}.substack.com"

# All formats Substack has ever used — tried in order
RSS_CANDIDATES = [
    f"https://{SUBSTACK_USERNAME}.substack.com/feed",
    f"https://{SUBSTACK_USERNAME}.substack.com/feed.xml",
    f"https://{SUBSTACK_USERNAME}.substack.com/rss",
    f"https://substack.com/@{SUBSTACK_USERNAME}/feed",
]

EMOJIS = ["📝", "🔧", "☁️", "🤖", "⚡", "🚀"]

# ── Placeholder shown before first post is published ──────────────────────────
PLACEHOLDER = f"""{START_MARKER}

> 🚀 **My build-in-public blog is live on Substack!**
> First post dropping soon — covering my 9-month journey to become a
> Backend + Cloud + AI engineer. Follow along at [{SUBSTACK_URL}]({SUBSTACK_URL})

| What's coming | |
|---|---|
| 📝 Week 1 | Why I'm committing to this 9-month engineering sprint |
| ☁️ Week 2 | Building a production FastAPI project from scratch |
| 🤖 Week 3 | What I learned deploying my first Docker container |

> 🔄 *Auto-updates when posts go live · [Follow on Substack →]({SUBSTACK_URL})*

{END_MARKER}"""

# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_posts():
    for url in RSS_CANDIDATES:
        print(f"Trying: {url}")
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                print(f"  ✅ Found {len(feed.entries)} posts at {url}")
                return feed.entries[:MAX_POSTS]
            else:
                print(f"  ⚠️  Feed reachable but empty (no posts published yet)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    return []

# ── Build markdown ────────────────────────────────────────────────────────────
def build_block(entries):
    if not entries:
        print("No posts found — using placeholder content.")
        return PLACEHOLDER

    lines = [START_MARKER, ""]
    for i, e in enumerate(entries):
        title   = e.get("title", "Untitled").strip()
        link    = e.get("link", SUBSTACK_URL).strip()
        summary = re.sub(r"<[^>]+>", "", e.get("summary", "")).strip()[:130]
        if len(summary) > 129:
            summary += "..."

        pub = e.get("published_parsed")
        date = datetime(*pub[:6]).strftime("%b %d, %Y") if pub else "Recent"

        emoji = EMOJIS[i % len(EMOJIS)]
        lines.append(f"{emoji} **[{title}]({link})**")
        if summary:
            lines.append(f"  > {summary}")
        lines.append(f"  `{date}`")
        lines.append("")

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines.append(
        f"> 🔄 *Auto-updated {ts} · [Read all posts →]({SUBSTACK_URL})*"
    )
    lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines)

# ── Write README ──────────────────────────────────────────────────────────────
def update_readme(block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print("ERROR: Markers not found in README.md — make sure both markers exist.")
        sys.exit(1)

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL
    )
    updated = pattern.sub(block, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    if updated == content:
        print("README unchanged — already up to date.")
    else:
        print("✅ README.md updated.")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    entries = fetch_posts()
    block   = build_block(entries)
    update_readme(block)
