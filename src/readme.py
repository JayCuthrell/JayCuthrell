from pathlib import Path
import datetime
import feedparser
import pytz
import re
import emoji

# Setup robust file paths based on the location of this script
src_dir = Path(__file__).parent
project_root = src_dir.parent
readme_path = project_root / 'README.md'

# Constants
YOUTUBE_CHANNEL_ID = "UCi_sC2b2aQ-s4-g2aem2_3w"

def update_footer():
    """Generates the footer with the current timestamp."""
    now = datetime.datetime.now(pytz.timezone("America/New_York"))
    return f"""
<hr>
<div align="center">
My README.md was last auto generated {now.strftime("%c")}
<br>
  <link href="https://github.com/jaycuthrell" rel="me">
  <link href="https://fudge.org" rel="me">
This auto generated README.md file is created by code based on examples from <a href="https://towardsdatascience.com/auto-updating-your-github-profile-with-python-cde87b638168" target="_blank">@dylanroy</a> and <a href="https://github.com/eugeneyan" target="_blank">@eugeneyan</a>.
<br>
<a href="https://github.com/JayCuthrell/JayCuthrell/actions"><img src="https://github.com/JayCuthrell/JayCuthrell/actions/workflows/cron.yml/badge.svg?branch=master" align="center" alt="Build README"></a>
</div>
"""

def fetch_rss_entries(rss_feed_url, limit=7):
    """Fetches and parses an RSS feed."""
    rss_feed = feedparser.parse(rss_feed_url)
    return rss_feed.entries[:limit]

def fetch_youtube_entries(channel_id, limit=7):
    """Fetches and parses a YouTube RSS feed."""
    rss_feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    rss_feed = feedparser.parse(rss_feed_url)
    return rss_feed.entries[:limit]

if __name__ == "__main__":
    fudge_feed = fetch_rss_entries("https://fudge.org/feed.xml")
    consulting_feed = fetch_rss_entries("https://cuthrell.consulting/feed.xml")
    youtube_feed = fetch_youtube_entries(YOUTUBE_CHANNEL_ID)
    all_entries = sorted(
        fudge_feed + consulting_feed + youtube_feed,
        key=lambda item: item.updated_parsed,
        reverse=True
    )

    posts_md = "\n".join(
        [
            f" - {emoji.emojize(':video_camera:')} [{item.title}]({item.link}) {datetime.datetime(*item.updated_parsed[:6]).strftime('%Y %b %d')}"
            if "youtube.com" in item.link
            else f" - {emoji.emojize(':newspaper:')} [{item.title}]({item.link}) {datetime.datetime(*item.updated_parsed[:6]).strftime('%Y %b %d')}"
            for item in all_entries[:7]
        ]
    )

    readme_text = readme_path.read_text(encoding="utf-8")

    # Use regex to find and replace the content between the markers
    updated_readme = re.sub(
        r"(?s)<!-- recent_posts_start -->.*<!-- recent_posts_end -->",
        f"<!-- recent_posts_start -->\n{posts_md}\n<!-- recent_posts_end -->",
        readme_text
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_readme + update_footer())