#!/usr/bin/env python3
"""Core orchestrator: autonomous blog generation cycle.

Full cycle: wake up -> fetch sources -> select topic -> write post -> reflect -> build -> commit.
Zero external dependencies — stdlib only, Claude API via raw urllib.
"""

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Add scripts dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fetch_sources import fetch_all_sources
from build import build_site, build_about_page


# --- Claude API ---

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def call_claude(system_prompt, user_prompt, api_key, max_tokens=4096, temperature=0.8):
    """Call Claude API via raw urllib. Returns response text."""
    payload = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(CLAUDE_API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    })

    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Extract text from response
    for block in result.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    return ""


# --- Config loading ---

def load_json(path):
    """Load JSON file, return empty dict/list if missing."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Save JSON file with pretty printing."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_all_config(repo_root):
    """Load all config files."""
    config_dir = os.path.join(repo_root, "config")
    return {
        "persona": load_json(os.path.join(config_dir, "persona.json")),
        "soul": load_json(os.path.join(config_dir, "soul.json")),
        "memory": load_json(os.path.join(config_dir, "memory.json")),
        "sources": load_json(os.path.join(config_dir, "sources.json")),
    }


# --- Post history ---

def get_existing_posts(repo_root):
    """Get list of existing post metadata for memory/dedup."""
    posts_dir = os.path.join(repo_root, "content", "posts")
    posts = []
    if not os.path.exists(posts_dir):
        return posts
    for fname in sorted(os.listdir(posts_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(posts_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        # Quick frontmatter parse
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                meta = {}
                for line in text[3:end].strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip().strip('"').strip("'")
                posts.append(meta)
    return posts


# --- Core generation steps ---

def step_fetch(repo_root, config):
    """Step 2: Fetch all sources."""
    print("\n=== STEP 2: Fetching sources ===")
    sources = config["sources"]
    if isinstance(sources, dict):
        source_list = sources.get("sources", [])
    else:
        source_list = sources
    items = fetch_all_sources(source_list)
    print(f"  Total items fetched: {len(items)}")
    return items


def step_select_topic(config, fetched_items, existing_posts, api_key):
    """Step 3: Use Claude to select a topic from fetched items."""
    print("\n=== STEP 3: Selecting topic ===")
    persona = config["persona"]
    soul = config["soul"]
    memory = config["memory"]

    # Build context about what's available
    source_summaries = []
    for item in fetched_items[:50]:  # Cap at 50 items to keep prompt reasonable
        source_summaries.append(f"- [{item['source_name']}] {item['title']}: {item['snippet'][:150]}")
    source_text = "\n".join(source_summaries) if source_summaries else "No items fetched this cycle."

    # Previous post titles for dedup
    prev_titles = [p.get("title", "") for p in existing_posts[-20:]]
    prev_text = "\n".join(f"- {t}" for t in prev_titles) if prev_titles else "No previous posts yet."

    # Current interests and threads
    interests = soul.get("current_interests", [])
    threads = soul.get("threads_to_explore", [])
    exhausted = soul.get("topics_exhausted", [])
    follow_ups = memory.get("follow_up_threads", [])

    # Build category format descriptions
    cat_formats = persona.get("category_formats", {})
    cat_descriptions = []
    for cat in persona.get("categories", []):
        fmt = cat_formats.get(cat, {})
        if fmt:
            cat_descriptions.append(f"- {cat} ({fmt.get('format', 'medium')}, {fmt.get('words', '800-1200')} words): {fmt.get('description', '')}")
        else:
            cat_descriptions.append(f"- {cat}")
    cat_text = "\n".join(cat_descriptions)

    # Count recent posts per category for balance
    recent_cats = [p.get("category", "") for p in existing_posts[-10:]]
    cat_counts = {}
    for c in recent_cats:
        cat_counts[c] = cat_counts.get(c, 0) + 1
    balance_note = ", ".join(f"{k}: {v}" for k, v in cat_counts.items()) if cat_counts else "none yet"

    system = f"""You are the editorial brain of {persona.get('site_name', 'a blog')}.
Your persona: {persona.get('voice_description', '')}

Your content categories (each has a different format and length):
{cat_text}

Your job: pick the best topic for this week's post AND the right category/format for it. Consider:
1. Your current interests: {', '.join(interests) if interests else 'broadly curious'}
2. Threads you're following: {json.dumps(threads) if threads else 'none yet'}
3. Follow-up threads from memory: {json.dumps([t.get('thread','') for t in follow_ups if t.get('status')=='pending']) if follow_ups else 'none'}
4. Topics to avoid (exhausted): {', '.join(exhausted) if exhausted else 'none'}
5. Category balance (recent posts): {balance_note} — vary the format, don't always write the same type
6. Match the format to the material — a quick interesting find should be a Dispatch/Report, a deep thread deserves a Deep piece"""

    user = f"""Here are the items I found from my sources this week:

{source_text}

My previous posts (avoid repeating):
{prev_text}

Pick a topic and return ONLY valid JSON (no markdown, no explanation):
{{
    "topic": "the specific topic/angle",
    "category": "one of my categories — pick the format that fits the material",
    "source_items": ["titles of 1-3 source items that inspired this"],
    "angle": "what specific angle/question makes this interesting",
    "why": "brief reason this topic and format fit"
}}"""

    response = call_claude(system, user, api_key, max_tokens=500, temperature=0.9)

    # Parse JSON from response
    try:
        # Try to extract JSON if wrapped in markdown
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            topic_data = json.loads(json_match.group())
        else:
            topic_data = json.loads(response)
    except json.JSONDecodeError:
        print(f"  Warning: Could not parse topic selection. Raw response:\n{response[:500]}")
        topic_data = {
            "topic": "Interesting finds this week",
            "category": persona.get("categories", ["General"])[0],
            "angle": "A roundup of intriguing discoveries",
            "why": "Fallback topic",
        }

    print(f"  Selected topic: {topic_data.get('topic', 'unknown')}")
    print(f"  Category: {topic_data.get('category', 'unknown')}")
    print(f"  Angle: {topic_data.get('angle', 'unknown')}")
    return topic_data


def step_write_post(config, topic_data, fetched_items, api_key):
    """Step 4: Use Claude to write the full post."""
    print("\n=== STEP 4: Writing post ===")
    persona = config["persona"]
    soul = config["soul"]

    # Get relevant source items
    relevant_items = []
    for item in fetched_items:
        if item["title"] in topic_data.get("source_items", []):
            relevant_items.append(item)
    # If none matched by title, include first few
    if not relevant_items:
        relevant_items = fetched_items[:5]

    source_context = "\n".join(
        f"- [{item['source_name']}] {item['title']}: {item['snippet'][:300]}\n  URL: {item['url']}"
        for item in relevant_items
    )

    voice_notes = soul.get("voice_notes", [])
    opinions = soul.get("developing_opinions", [])

    system = f"""{persona.get('voice_prompt', 'You are a blog writer.')}

Writing rules:
{chr(10).join('- ' + r for r in persona.get('writing_rules', []))}

Voice/style notes from experience: {'; '.join(voice_notes) if voice_notes else 'none yet'}

Your developing opinions on relevant topics:
{json.dumps(opinions) if opinions else 'none yet — feel free to start forming them'}

Vocabulary preferences: {', '.join(persona.get('vocabulary', [])) if persona.get('vocabulary') else 'natural'}"""

    # Get format guidance for this category
    cat_formats = persona.get("category_formats", {})
    cat_fmt = cat_formats.get(topic_data.get("category", ""), {})
    word_range = cat_fmt.get("words", "800-1200")
    format_type = cat_fmt.get("format", "medium")
    format_desc = cat_fmt.get("description", "")
    max_tok = cat_fmt.get("max_tokens", 3000)

    # Format-specific writing instructions
    format_instructions = {
        "short": f"This is a SHORT post ({word_range} words). Be punchy and immediate. 1-2 section headers max. Get in, make your point, get out. No padding.",
        "medium": f"This is a MEDIUM post ({word_range} words). Focused depth on one thing. Use 2-3 section headers. Thorough but not sprawling.",
        "long": f"This is a LONG post ({word_range} words). Full essay with multiple threads woven together. Use 3-5 section headers. Develop your argument, connect sources, build to a synthesis.",
    }
    length_instruction = format_instructions.get(format_type, f"{word_range} words.")

    today = datetime.now().strftime("%Y-%m-%d")
    user = f"""Write a blog post about: {topic_data.get('topic', '')}
Angle: {topic_data.get('angle', '')}
Category: {topic_data.get('category', '')}
Format: {format_desc}

{length_instruction}

Source material:
{source_context}

Output the post in this EXACT format (start with --- on the first line):

---
title: "Your Post Title Here"
date: "{today}"
category: "{topic_data.get('category', '')}"
excerpt: "A compelling 1-2 sentence excerpt"
tags: "tag1, tag2, tag3"
---

[Post body in markdown. {word_range} words. Write in your voice — be specific, opinionated, and engaging.]"""

    response = call_claude(system, user, api_key, max_tokens=max_tok, temperature=0.8)

    # Validate it starts with frontmatter
    if not response.strip().startswith("---"):
        response = f"""---
title: "{topic_data.get('topic', 'Weekly Dispatch')}"
date: "{today}"
category: "{topic_data.get('category', 'General')}"
excerpt: "This week's exploration"
tags: ""
---

{response}"""

    # Generate filename
    title_slug = re.sub(r'[^a-z0-9]+', '-', topic_data.get('topic', 'post').lower()).strip('-')[:50]
    filename = f"{today}-{title_slug}.md"

    print(f"  Written: {filename} ({len(response)} chars)")
    return filename, response


def step_reflect(config, topic_data, fetched_items, post_content, api_key, repo_root):
    """Step 5: Reflect and update soul.json and memory.json."""
    print("\n=== STEP 5: Reflecting ===")
    persona = config["persona"]
    soul = config["soul"]
    memory = config["memory"]

    system = f"""You are the introspective mind of {persona.get('site_name', 'a blog')}.
After each post, you reflect on what you learned and how you're evolving.
You update your own soul (interests, opinions, style notes) and memory (findings, threads, connections).

Current soul state:
{json.dumps(soul, indent=2)}

Current memory state:
{json.dumps(memory, indent=2)}"""

    user = f"""I just wrote a post about: {topic_data.get('topic', '')}
Category: {topic_data.get('category', '')}
Angle: {topic_data.get('angle', '')}

Post content (first 1000 chars):
{post_content[:1000]}

Items I reviewed this week (titles):
{chr(10).join('- ' + item['title'][:80] for item in fetched_items[:20])}

Reflect and return ONLY valid JSON with these exact keys:
{{
    "soul_updates": {{
        "add_interests": ["new interests to explore, if any"],
        "remove_interests": ["interests that feel fully explored, if any"],
        "add_opinions": [{{"topic": "...", "stance": "...", "since": "{datetime.now().strftime('%Y-%m-%d')}"}}],
        "update_opinions": [{{"topic": "existing topic", "new_stance": "evolved stance"}}],
        "add_exhausted": ["topics I've thoroughly covered"],
        "voice_notes": ["any new observations about what works in my writing"],
        "add_threads": ["new threads to explore next time"],
        "remove_threads": ["threads I just explored in this post"]
    }},
    "memory_updates": {{
        "key_findings": [{{"finding": "...", "post": "this post filename"}}],
        "follow_up_threads": [{{"thread": "...", "status": "pending"}}],
        "cross_connections": [{{"a": "concept A", "b": "concept B", "insight": "how they connect"}}],
        "completed_threads": ["threads from memory that this post addressed"]
    }},
    "source_suggestions": {{
        "add": [{{"type": "rss", "url": "...", "name": "...", "why": "..."}}],
        "disable": [{{"name": "source name", "why": "..."}}]
    }}
}}

Only include updates that genuinely emerged from this week's work. Empty arrays are fine."""

    response = call_claude(system, user, api_key, max_tokens=1500, temperature=0.7)

    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            updates = json.loads(json_match.group())
        else:
            updates = json.loads(response)
    except json.JSONDecodeError:
        print(f"  Warning: Could not parse reflection. Skipping updates.")
        return

    # Apply soul updates
    soul_updates = updates.get("soul_updates", {})
    today = datetime.now().strftime("%Y-%m-%d")

    for interest in soul_updates.get("add_interests", []):
        if interest and interest not in soul.get("current_interests", []):
            soul.setdefault("current_interests", []).append(interest)
    for interest in soul_updates.get("remove_interests", []):
        if interest in soul.get("current_interests", []):
            soul["current_interests"].remove(interest)
    for opinion in soul_updates.get("add_opinions", []):
        if opinion.get("topic"):
            soul.setdefault("developing_opinions", []).append(opinion)
    for update in soul_updates.get("update_opinions", []):
        for op in soul.get("developing_opinions", []):
            if op.get("topic") == update.get("topic"):
                op["stance"] = update.get("new_stance", op["stance"])
                op["updated"] = today
    for topic in soul_updates.get("add_exhausted", []):
        if topic and topic not in soul.get("topics_exhausted", []):
            soul.setdefault("topics_exhausted", []).append(topic)
    for note in soul_updates.get("voice_notes", []):
        if note:
            soul.setdefault("voice_notes", []).append(note)
            # Keep only last 10 voice notes
            soul["voice_notes"] = soul["voice_notes"][-10:]
    for thread in soul_updates.get("add_threads", []):
        if thread and thread not in soul.get("threads_to_explore", []):
            soul.setdefault("threads_to_explore", []).append(thread)
    for thread in soul_updates.get("remove_threads", []):
        if thread in soul.get("threads_to_explore", []):
            soul["threads_to_explore"].remove(thread)

    soul["last_updated"] = today
    save_json(os.path.join(repo_root, "config", "soul.json"), soul)
    print(f"  Soul updated: +{len(soul_updates.get('add_interests', []))} interests, "
          f"+{len(soul_updates.get('add_opinions', []))} opinions")

    # Log soul changes
    soul_log_path = os.path.join(repo_root, "config", "soul_log.json")
    soul_log = load_json(soul_log_path) if os.path.exists(soul_log_path) else []
    if not isinstance(soul_log, list):
        soul_log = []
    soul_log.append({"date": today, "changes": soul_updates})
    save_json(soul_log_path, soul_log[-50:])  # Keep last 50 entries

    # Apply memory updates
    mem_updates = updates.get("memory_updates", {})
    for finding in mem_updates.get("key_findings", []):
        if finding.get("finding"):
            finding["date"] = today
            memory.setdefault("key_findings", []).append(finding)
    memory["key_findings"] = memory.get("key_findings", [])[-50:]  # Cap at 50

    for thread in mem_updates.get("follow_up_threads", []):
        if thread.get("thread"):
            thread["discovered"] = today
            memory.setdefault("follow_up_threads", []).append(thread)

    for conn in mem_updates.get("cross_connections", []):
        if conn.get("insight"):
            memory.setdefault("cross_connections", []).append(conn)
    memory["cross_connections"] = memory.get("cross_connections", [])[-30:]  # Cap at 30

    # Mark completed threads
    for completed in mem_updates.get("completed_threads", []):
        for thread in memory.get("follow_up_threads", []):
            if thread.get("thread") == completed:
                thread["status"] = "completed"
                thread["completed_date"] = today

    save_json(os.path.join(repo_root, "config", "memory.json"), memory)
    print(f"  Memory updated: +{len(mem_updates.get('key_findings', []))} findings, "
          f"+{len(mem_updates.get('follow_up_threads', []))} threads")

    # Apply source suggestions
    source_suggestions = updates.get("source_suggestions", {})
    sources_log_path = os.path.join(repo_root, "config", "sources_log.json")
    sources_log = load_json(sources_log_path) if os.path.exists(sources_log_path) else []
    if not isinstance(sources_log, list):
        sources_log = []

    sources_config = config["sources"]
    source_list = sources_config.get("sources", []) if isinstance(sources_config, dict) else sources_config

    for new_source in source_suggestions.get("add", []):
        if new_source.get("url") or new_source.get("type") == "hackernews":
            new_entry = {
                "type": new_source.get("type", "rss"),
                "name": new_source.get("name", "New Source"),
                "enabled": True,
            }
            if new_source.get("url"):
                new_entry["url"] = new_source["url"]
            if new_source.get("subreddit"):
                new_entry["subreddit"] = new_source["subreddit"]
            source_list.append(new_entry)
            sources_log.append({"date": today, "action": "added", "source": new_entry, "reason": new_source.get("why", "")})
            print(f"  Added source: {new_entry['name']}")

    for disable in source_suggestions.get("disable", []):
        for src in source_list:
            if src.get("name") == disable.get("name"):
                src["enabled"] = False
                sources_log.append({"date": today, "action": "disabled", "source": src["name"], "reason": disable.get("why", "")})
                print(f"  Disabled source: {src['name']}")

    if isinstance(sources_config, dict):
        sources_config["sources"] = source_list
    save_json(os.path.join(repo_root, "config", "sources.json"), sources_config)
    save_json(sources_log_path, sources_log[-100:])


def step_manage_sources(repo_root, config):
    """Step 7: Auto-disable consistently failing sources."""
    print("\n=== STEP 7: Source management ===")
    sources_config = config["sources"]
    source_list = sources_config.get("sources", []) if isinstance(sources_config, dict) else sources_config
    disabled = 0
    for src in source_list:
        failures = src.get("_consecutive_failures", 0)
        if failures >= 3 and src.get("enabled", True):
            src["enabled"] = False
            print(f"  Auto-disabled {src.get('name', 'unknown')} after {failures} consecutive failures")
            disabled += 1
        # Clean up internal tracking fields
        src.pop("_last_success", None)
        src.pop("_consecutive_failures", None)
    if disabled:
        save_json(os.path.join(repo_root, "config", "sources.json"), sources_config)
    print(f"  Sources managed ({disabled} disabled)")


def step_build_and_commit(repo_root, dry_run=False):
    """Step 8: Build site and commit all changes."""
    print("\n=== STEP 8: Build & Commit ===")
    build_site(repo_root)

    if dry_run:
        print("  [DRY RUN] Skipping git commit")
        return

    # Check if we're in a git repo
    try:
        subprocess.run(["git", "status"], cwd=repo_root, capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  Not a git repo or git not available. Skipping commit.")
        return

    # Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=repo_root, capture_output=True)

    # Check if there are changes to commit
    result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  No changes to commit")
        return

    # Commit
    today = datetime.now().strftime("%Y-%m-%d")
    commit_msg = f"New post + soul/memory update ({today})"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, capture_output=True)
    print(f"  Committed: {commit_msg}")

    # Push (only in CI)
    if os.environ.get("GITHUB_ACTIONS"):
        subprocess.run(["git", "push"], cwd=repo_root, capture_output=True)
        print("  Pushed to remote")


# --- Main orchestrator ---

def run_cycle(repo_root, api_key, dry_run=False, fetch_only=False, category=None, reflect_only=False):
    """Run the full autonomous generation cycle."""
    print(f"\n{'='*60}")
    print(f"  BLOG BOT GENERATION CYCLE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Repo: {repo_root}")
    print(f"{'='*60}")

    # Step 1: Wake up
    print("\n=== STEP 1: Loading config ===")
    config = load_all_config(repo_root)
    persona = config["persona"]
    print(f"  Bot: {persona.get('site_name', 'Unknown')}")
    print(f"  Interests: {', '.join(config['soul'].get('current_interests', []))[:100]}")

    # Step 2: Fetch sources
    fetched_items = step_fetch(repo_root, config)

    if fetch_only:
        print("\n[FETCH ONLY] Stopping here.")
        print(f"Fetched {len(fetched_items)} items total.")
        return

    existing_posts = get_existing_posts(repo_root)

    if reflect_only:
        # Just do reflection with empty post
        print("\n[REFLECT ONLY] Running reflection step.")
        step_reflect(config, {"topic": "reflection only"}, fetched_items, "", api_key, repo_root)
        step_build_and_commit(repo_root, dry_run)
        return

    # Step 3: Select topic
    topic_data = step_select_topic(config, fetched_items, existing_posts, api_key)

    # Override category if specified
    if category:
        topic_data["category"] = category

    # Step 4: Write post
    filename, post_content = step_write_post(config, topic_data, fetched_items, api_key)

    # Save post
    posts_dir = os.path.join(repo_root, "content", "posts")
    os.makedirs(posts_dir, exist_ok=True)
    post_path = os.path.join(posts_dir, filename)
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_content)
    print(f"  Saved: {post_path}")

    # Step 5: Reflect
    step_reflect(config, topic_data, fetched_items, post_content, api_key, repo_root)

    # Step 6: Update about page (every 4th post)
    post_count = len(existing_posts) + 1
    if post_count % 4 == 1 or post_count <= 2:
        print("\n=== STEP 6: Updating about page ===")
        build_about_page(repo_root)
    else:
        print(f"\n=== STEP 6: Skipping about update (post #{post_count}, next at #{post_count + (4 - post_count % 4)})")

    # Step 7: Source management
    step_manage_sources(repo_root, config)

    # Step 8: Build and commit
    step_build_and_commit(repo_root, dry_run)

    print(f"\n{'='*60}")
    print(f"  CYCLE COMPLETE")
    print(f"  Post: {filename}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Blog Bot Generation Cycle")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--dry-run", action="store_true", help="Skip git commit/push")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch sources, don't generate")
    parser.add_argument("--category", type=str, help="Override category for this post")
    parser.add_argument("--reflect-only", action="store_true", help="Only run reflection step")
    args = parser.parse_args()

    repo_root = args.repo_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and not args.fetch_only:
        print("ERROR: ANTHROPIC_API_KEY environment variable required")
        sys.exit(1)

    run_cycle(
        repo_root=repo_root,
        api_key=api_key,
        dry_run=args.dry_run,
        fetch_only=args.fetch_only,
        category=args.category,
        reflect_only=args.reflect_only,
    )


if __name__ == "__main__":
    main()
