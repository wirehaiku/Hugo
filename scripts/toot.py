#!/bin/env python

"""
toot.py: Automatically toots the latest Wire Haiku post to @stvmln.
"""

import os

import feedparser
import requests

API_URL = "https://stvmln.com/api/v1/statuses"
RSS_URL = "https://wirehaiku.org/posts/index.xml"
API_KEY = os.environ.get("MASTODON_API", None)

STATUS = """
:wh: {title} :wh:

{blog_summary}

{link}
"""

if __name__ == "__main__":
    # Ensure API key is present.
    if not API_KEY:
        raise SystemExit("No API key present.")

    # Get the latest feed item.
    feed = feedparser.parse(RSS_URL)
    item = feed["entries"][0]

    # Ask for post permission.
    okay = input(f"Latest feed item is {item['title']}, post? [Y/n] ")
    if okay.lower().startswith("n"):
        raise SystemExit("Post cancelled.")

    # Send the API request.
    text = STATUS.format(**item)
    head = {"Authorization": f"Bearer {API_KEY}"}
    data = {"status": text, "language": "en", "visibility": "public"}
    resp = requests.post(API_URL, data=data, headers=head)

    if resp.status_code >= 444400:
        raise SystemExit(f"Request failed ({resp.status_code}).")

    print("Status posted.")
