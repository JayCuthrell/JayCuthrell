from pathlib import Path
import datetime
import feedparser
import json
import pytz
import re
import emoji

# Setup robust file paths based on the location of this script
src_dir = Path(__file__).parent
project_root = src_dir.parent
readme_path = project_root / 'README.md'

# Constants
YOUTUBE_CHANNEL_ID = "UC0gbzQXghnt-4cgci-VpodQ"
YOUTUBE_CACHE_PATH = src_dir / 'youtube_cache.json'

def update_footer():
    """Generates the footer with the current timestamp."""
    now = datetime.datetime.now(pytz.timezone("America/New_York"))
    return f"""<!-- footer_start -->
<div align="center">This README.md is updated on {now.strftime('%c')}</div>
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
<!-- footer_end -->"""

def fetch_rss_entries(rss_feed_url, limit=7):
    """Fetches and parses an RSS feed."""
    try:
        rss_feed = feedparser.parse(rss_feed_url)
        if rss_feed.bozo:
            print(f"Warning: Malformed feed at {rss_feed_url}. Bozo reason: {rss_feed.bozo_exception}")
        return rss_feed.entries[:limit]
    except Exception as e:
        print(f"Error fetching or parsing RSS feed at {rss_feed_url}: {e}")
        return []

def fetch_youtube_entries(channel_id, limit=7, cache_path=YOUTUBE_CACHE_PATH):
    """
    Fetches and parses a YouTube RSS feed with caching.
    Returns entries from live feed if successful, otherwise from cache.
    """
    rss_feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    live_entries = fetch_rss_entries(rss_feed_url, limit)

    if live_entries:
        # Save successful fetch to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(live_entries, f, indent=2)
        return live_entries
    
    print("Fetching YouTube feed failed. Attempting to load from cache.")
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    
    return []

if __name__ == "__main__":
    fudge_feed = fetch_rss_entries("https://fudge.org/feed.xml")
    consulting_feed = fetch_rss_entries("https://cuthrell.consulting/feed.xml")
    youtube_feed = fetch_youtube_entries(YOUTUBE_CHANNEL_ID)
    all_entries = sorted(
        fudge_feed + consulting_feed + youtube_feed,
        key=lambda item: item.updated_parsed,
        reverse=True
    )

    posts_md_lines = []
    for item in all_entries[:7]:
        published_date = datetime.datetime(*item.updated_parsed[:6]).strftime('%Y %b %d')
        
        if "youtube.com" in item.link:
            emoji_char = emoji.emojize(':video_camera:')
        elif 'enclosures' in item and any('audio' in e.get('type', '') for e in item.enclosures):
            emoji_char = emoji.emojize(':studio_microphone:')
        else:
            emoji_char = emoji.emojize(':newspaper:')
            
        posts_md_lines.append(f" - {emoji_char} [{item.title}]({item.link}) {published_date}")

    posts_md = "\n".join(posts_md_lines)

    readme_text = readme_path.read_text(encoding="utf-8")

    # Use regex to find and replace the content between the markers
    updated_readme = re.sub(
        r"(?s)<!-- recent_posts_start -->.*<!-- recent_posts_end -->",
        f"<!-- recent_posts_start -->\n{posts_md}\n<!-- recent_posts_end -->",
        readme_text
    )
    
    # Use regex to find and replace the content between the footer markers
    updated_readme = re.sub(
        r"(?s)<!-- footer_start -->.*<!-- footer_end -->",
        update_footer(),
        updated_readme
    )
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_readme)