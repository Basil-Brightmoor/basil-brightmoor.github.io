#!/usr/bin/env python3
"""Source fetching utilities: Reddit, HN, RSS, web pages, GitHub trending.

All functions return lists of dicts: [{"title", "url", "snippet", "source_name"}]
Zero external dependencies — stdlib only.
"""

import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.error import URLError, HTTPError


# Shared HTTP helpers

def _make_request(url, timeout=15):
    """Make an HTTP GET request, return response text. Returns None on failure."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "BlogBot/1.0 (autonomous research blog)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError, TimeoutError, OSError) as e:
        print(f"  [fetch] Error fetching {url}: {e}")
        return None


def _make_json_request(url, timeout=15):
    """Make HTTP GET, parse JSON. Returns None on failure."""
    text = _make_request(url, timeout)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  [fetch] JSON parse error for {url}: {e}")
        return None


class _TextExtractor(HTMLParser):
    """Extract visible text from HTML."""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self._skip = False
        self._skip_tags = {"script", "style", "noscript", "nav", "footer", "header"}

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self):
        return " ".join(self.text_parts)


def _extract_text(html_str, max_len=2000):
    """Extract visible text from HTML string."""
    parser = _TextExtractor()
    try:
        parser.feed(html_str)
    except Exception:
        pass
    text = parser.get_text()
    return text[:max_len] if len(text) > max_len else text


# Source fetchers

def fetch_reddit_json(subreddit, limit=10):
    """Fetch top posts from a subreddit using Reddit's public JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    data = _make_json_request(url)
    if not data or "data" not in data:
        return []
    results = []
    for child in data["data"].get("children", []):
        post = child.get("data", {})
        title = post.get("title", "")
        permalink = post.get("permalink", "")
        selftext = post.get("selftext", "")[:300]
        link_url = post.get("url", "")
        results.append({
            "title": title,
            "url": f"https://www.reddit.com{permalink}" if permalink else link_url,
            "snippet": selftext or title,
            "source_name": f"r/{subreddit}",
        })
    return results


def fetch_hackernews(limit=15):
    """Fetch top stories from Hacker News via Firebase API."""
    ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ids = _make_json_request(ids_url)
    if not ids:
        return []
    results = []
    for story_id in ids[:limit]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        item = _make_json_request(item_url)
        if not item:
            continue
        title = item.get("title", "")
        url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
        results.append({
            "title": title,
            "url": url,
            "snippet": title,
            "source_name": "Hacker News",
        })
    return results


def fetch_rss(feed_url, source_name=None, limit=10):
    """Fetch items from an RSS or Atom feed."""
    text = _make_request(feed_url)
    if not text:
        return []
    results = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        print(f"  [fetch] RSS parse error for {feed_url}: {e}")
        return []

    # Handle RSS 2.0
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        title = title_el.text if title_el is not None and title_el.text else ""
        link = link_el.text if link_el is not None and link_el.text else ""
        desc = desc_el.text if desc_el is not None and desc_el.text else ""
        # Strip HTML from description
        desc = re.sub(r'<[^>]+>', '', desc)[:300]
        results.append({
            "title": title,
            "url": link,
            "snippet": desc or title,
            "source_name": source_name or feed_url,
        })
        if len(results) >= limit:
            break

    # Handle Atom feeds if no RSS items found
    if not results:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall(".//atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link", ns)
            summary_el = entry.find("atom:summary", ns)
            title = title_el.text if title_el is not None and title_el.text else ""
            link = link_el.get("href", "") if link_el is not None else ""
            summary = summary_el.text if summary_el is not None and summary_el.text else ""
            summary = re.sub(r'<[^>]+>', '', summary)[:300]
            results.append({
                "title": title,
                "url": link,
                "snippet": summary or title,
                "source_name": source_name or feed_url,
            })
            if len(results) >= limit:
                break

        # Also try without namespace (some Atom feeds)
        if not results:
            for entry in root.iter("entry"):
                title_el = entry.find("title")
                link_el = entry.find("link")
                summary_el = entry.find("summary") or entry.find("content")
                title = title_el.text if title_el is not None and title_el.text else ""
                link = link_el.get("href", "") if link_el is not None else ""
                summary = summary_el.text if summary_el is not None and summary_el.text else ""
                summary = re.sub(r'<[^>]+>', '', summary)[:300]
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": summary or title,
                    "source_name": source_name or feed_url,
                })
                if len(results) >= limit:
                    break

    return results


def fetch_webpage_extract(url, source_name=None):
    """Fetch a web page and extract text content. Returns a single-item list."""
    text = _make_request(url)
    if not text:
        return []
    # Try to get title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else url
    extracted = _extract_text(text)
    return [{
        "title": title,
        "url": url,
        "snippet": extracted[:500],
        "source_name": source_name or url,
    }]


def fetch_github_trending(language=None, since="weekly"):
    """Scrape GitHub trending page for trending repos."""
    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    url += f"?since={since}"
    text = _make_request(url)
    if not text:
        return []
    results = []
    # Parse repo links from trending page
    repo_pattern = r'<h2 class="h3 lh-condensed">\s*<a href="(/[^"]+)"'
    matches = re.findall(repo_pattern, text)
    # Also try alternate pattern
    if not matches:
        matches = re.findall(r'href="(/[^/]+/[^"]+)"[^>]*class="[^"]*Link[^"]*"', text)

    for path in matches[:15]:
        repo_name = path.strip("/")
        # Try to find description
        desc_pattern = re.escape(path) + r'.*?<p class="[^"]*">\s*(.+?)\s*</p>'
        desc_match = re.search(desc_pattern, text, re.DOTALL)
        snippet = desc_match.group(1).strip() if desc_match else repo_name
        snippet = re.sub(r'<[^>]+>', '', snippet).strip()
        results.append({
            "title": repo_name,
            "url": f"https://github.com{path}",
            "snippet": snippet[:300],
            "source_name": "GitHub Trending",
        })
    return results


def fetch_producthunt(limit=10):
    """Fetch from Product Hunt's RSS feed."""
    return fetch_rss("https://www.producthunt.com/feed", source_name="Product Hunt", limit=limit)


def fetch_all_sources(sources_config):
    """Fetch all enabled sources from sources.json config.

    sources_config format:
    [
        {"type": "reddit", "subreddit": "puzzles", "enabled": true, "name": "r/puzzles"},
        {"type": "hackernews", "enabled": true, "name": "Hacker News"},
        {"type": "rss", "url": "...", "enabled": true, "name": "Some Feed"},
        {"type": "webpage", "url": "...", "enabled": true, "name": "Some Page"},
        {"type": "github_trending", "language": "python", "enabled": true, "name": "GitHub Trending"},
        {"type": "producthunt", "enabled": true, "name": "Product Hunt"}
    ]
    """
    all_items = []
    for source in sources_config:
        if not source.get("enabled", True):
            continue
        source_type = source.get("type", "")
        name = source.get("name", source_type)
        try:
            if source_type == "reddit":
                items = fetch_reddit_json(source["subreddit"], limit=source.get("limit", 10))
            elif source_type == "hackernews":
                items = fetch_hackernews(limit=source.get("limit", 15))
            elif source_type == "rss":
                items = fetch_rss(source["url"], source_name=name, limit=source.get("limit", 10))
            elif source_type == "webpage":
                items = fetch_webpage_extract(source["url"], source_name=name)
            elif source_type == "github_trending":
                items = fetch_github_trending(language=source.get("language"), since=source.get("since", "weekly"))
            elif source_type == "producthunt":
                items = fetch_producthunt(limit=source.get("limit", 10))
            else:
                print(f"  [fetch] Unknown source type: {source_type}")
                items = []
            print(f"  [fetch] {name}: {len(items)} items")
            all_items.extend(items)
            # Mark source as successfully fetched
            source["_last_success"] = True
        except Exception as e:
            print(f"  [fetch] Error with {name}: {e}")
            source["_last_success"] = False
            source["_consecutive_failures"] = source.get("_consecutive_failures", 0) + 1
    return all_items


if __name__ == "__main__":
    # Quick test
    print("Testing Reddit fetch...")
    items = fetch_reddit_json("puzzles", limit=3)
    for item in items:
        print(f"  - {item['title'][:60]}")

    print("\nTesting HN fetch...")
    items = fetch_hackernews(limit=3)
    for item in items:
        print(f"  - {item['title'][:60]}")
