from pathlib import Path
import datetime
import time
import feedparser
import pytz

# Setup robust file paths based on the location of this script
src_dir = Path(__file__).parent
project_root = src_dir.parent
readme_path = project_root / 'README.md'
footer_path = project_root / 'FOOTER.md'

def update_footer():
    """Generates the footer with the current timestamp."""
    timestamp = datetime.datetime.now(pytz.timezone("America/New_York")).strftime("%c")
    footer = footer_path.read_text(encoding="utf-8")
    return footer.format(timestamp=timestamp)

def fetch_rss_entries(rss_feed_url):
    """Fetches and parses an RSS feed."""
    rss_feed = feedparser.parse(rss_feed_url)
    return rss_feed.entries

def combine_feeds(feed1, feed2):
    """Combines two feeds and sorts them by publication date (newest first)."""
    combined_entries = feed1 + feed2
    combined_entries.sort(key=lambda item: item.updated_parsed, reverse=True)
    return combined_entries

if __name__ == "__main__":
    rss_title = "### Recent Newsletter Issues by Jay Cuthrell on [fudge.org](https://fudge.org) and [cuthrell.consulting](https://cuthrell.consulting)"
    readme_content = readme_path.read_text(encoding="utf-8")
    
    # Fetch and combine feeds
    feed1 = fetch_rss_entries("https://fudge.org/feed.xml")
    feed2 = fetch_rss_entries("https://cuthrell.consulting/feed.xml")
    combined_feed = combine_feeds(feed1, feed2)
    
    # Build the markdown list of posts
    posts = []
    for item in combined_feed[:7]:
        title = item.title
        link = item.link
        published = time.strftime('%Y %b %d', item.updated_parsed)
        posts.append(f" - [{title}]({link}) {published}")
    
    posts_joined = '\n'.join(posts)
    
    # Slice the old README and inject the new posts and updated footer
    updated_readme = readme_content[:readme_content.find(rss_title)] + f"{rss_title}\n{posts_joined}\n"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_readme + update_footer())