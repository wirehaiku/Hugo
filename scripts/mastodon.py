"""
mastodon.py: Post the latest RSS item to Mastodon.
"""

import os

import feedparser
import requests

ENVI_KEY = "MASTODON_API"
POST_URL = "https://stvmln.com/api/v1/statuses"
FEED_URL = "https://wirehaiku.org/index.xml"
POST_STRING = """
:wh: {title} :wh:

{blog_summary}

{link}
"""

# Get API authentication key from environment variables.
if ENVI_KEY not in os.environ:
    raise ValueError(f"{ENVI_KEY} not in environment variables")

api_auth = os.environ[ENVI_KEY].strip()
api_head = {"Authorization": f"Bearer {api_auth}"}

# Get latest item from RSS feed.
rss_feed = feedparser.parse(FEED_URL)
rss_item = rss_feed["entries"][0]

# Prompt for post permission.
okay = input(f"Latest feed item is {rss_item['title']}, post? [Y/n] ")
if okay.lower().startswith("n"):
    raise SystemExit("Post cancelled.")

# Construct and post Mastodon status.
api_text = POST_STRING.format(**rss_item)
api_data = {"status": api_text, "language": "en", "visibility": "public"}
req_data = requests.post(POST_URL, data=api_data, headers=api_head)

if req_data.status_code != 200:
    raise ValueError(f"Error: {req_data.status_code} {req_data.text!r}")

# Print link to posted status.
print(f"Status posted to {req_data.json()['url']}.")
