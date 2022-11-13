"""
autopost.py

This script does the following:

- Crawl Wire Haiku's RSS feed to find the latest item.
- Post a status on @wirehaiku@stvmln.com linking to that item.
- Boost that status on @stvmln@stvmln.com.

This script requires internet access and two MASTODON_* environment variables to be
set to Mastodon API keys.
"""

import os

import feedparser
import requests
from typing import Any

API_BASE = "https://stvmln.com/api/v1/statuses"
RSS_BASE = "https://wirehaiku.org/index.xml"
CREATOR_ENV = "MASTODON_WIREHAIKU"
BOOSTER_ENV = "MASTODON_STVMLN"

STATUS_STRING = """
:wh: {title} :wh:

{blog_summary}

{link}
"""


def get_api_headers(env: str) -> dict[str, str]:
    """
    Return a dictionary containing API authentication headers from an environ set to
    a Mastodon API key.
    """

    if env not in os.environ:
        raise ValueError(f"environment variable {env} missing")

    val = os.environ[env].strip()
    return {"Authorization": f"Bearer {val}"}


def get_feed_item(url: str) -> dict[str, Any]:
    """
    Return the latest item in a remote RSS feed as a dict.
    """

    feed = feedparser.parse(url)
    return feed["entries"][0]


def post_status(env: str, text: str) -> str:
    """
    Post a status to a Mastodon using an environ and return the status's local ID.
    """

    head = get_api_headers(env)
    data = {"status": text, "language": "en", "visibility": "public"}
    requ = requests.post(f"{API_BASE}", data=data, headers=head)

    if requ.status_code >= 300:
        raise ValueError(f"request failed {requ.status_code}")

    return requ.json()["id"]


def boost_status(env: str, id: str):
    """
    Boost an existing status in Mastodon using an environ.
    """

    head = get_api_headers(env)
    requ = requests.post(f"{API_BASE}/{id}/reblog", headers=head)
    if requ.status_code >= 300:
        raise ValueError(f"request failed {requ.status_code}")


def main():
    """
    Run the main program.
    """

    item = get_feed_item(RSS_BASE)

    okay = input(f"Latest feed item is {item['title']}, post? [Y/n] ")
    if okay.lower().startswith("n"):
        raise SystemExit("Post cancelled.")

    id = post_status(CREATOR_ENV, STATUS_STRING.format(**item))
    print("- Status posted.")

    boost_status(BOOSTER_ENV, id)
    print("- Status boosted.")


if __name__ == "__main__":
    main()
