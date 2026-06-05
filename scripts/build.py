#!/usr/bin/env python3
"""Static site generator: markdown to HTML with YAML frontmatter."""

import json
import os
import re
import html
from datetime import datetime
from pathlib import Path


def load_config(repo_root):
    """Load persona config."""
    persona_path = os.path.join(repo_root, "config", "persona.json")
    with open(persona_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template(repo_root):
    """Load HTML template."""
    tmpl_path = os.path.join(repo_root, "templates", "base.html")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(text):
    """Parse YAML frontmatter from markdown. Returns (metadata_dict, body_str)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    yaml_block = text[3:end].strip()
    body = text[end + 3:].strip()
    meta = {}
    for line in yaml_block.split("\n"):
        line = line.strip()
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.strip().strip('"').strip("'")
            meta[key.strip()] = val
    return meta, body


def markdown_to_html(md):
    """Convert markdown to HTML using regex. Handles common elements."""
    lines = md.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    list_type = None  # 'ul' or 'ol'
    in_blockquote = False
    blockquote_lines = []

    def process_inline(text):
        """Process inline markdown: bold, italic, code, links, images."""
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)
        # Inline code: `text`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_lines.append(f"</{list_type}>")
            in_list = False
            list_type = None

    def close_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote:
            content = " ".join(blockquote_lines)
            html_lines.append(f"<blockquote><p>{process_inline(content)}</p></blockquote>")
            in_blockquote = False
            blockquote_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```"):
            if not in_code_block:
                close_list()
                close_blockquote()
                lang = line.strip()[3:].strip()
                html_lines.append(f"<pre><code>")
                in_code_block = True
            else:
                html_lines.append("</code></pre>")
                in_code_block = False
            i += 1
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            i += 1
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            close_list()
            close_blockquote()
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
            close_list()
            close_blockquote()
            html_lines.append("<hr>")
            i += 1
            continue

        # Headers
        header_match = re.match(r'^(#{1,6})\s+(.+)', stripped)
        if header_match:
            close_list()
            close_blockquote()
            level = len(header_match.group(1))
            text = process_inline(header_match.group(2))
            html_lines.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            close_list()
            content = stripped[1:].strip()
            if not in_blockquote:
                in_blockquote = True
                blockquote_lines = [content]
            else:
                blockquote_lines.append(content)
            i += 1
            continue

        # Unordered list
        ul_match = re.match(r'^[\-\*\+]\s+(.+)', stripped)
        if ul_match:
            close_blockquote()
            if not in_list or list_type != "ul":
                close_list()
                html_lines.append("<ul>")
                in_list = True
                list_type = "ul"
            html_lines.append(f"<li>{process_inline(ul_match.group(1))}</li>")
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^\d+\.\s+(.+)', stripped)
        if ol_match:
            close_blockquote()
            if not in_list or list_type != "ol":
                close_list()
                html_lines.append("<ol>")
                in_list = True
                list_type = "ol"
            html_lines.append(f"<li>{process_inline(ol_match.group(1))}</li>")
            i += 1
            continue

        # Regular paragraph
        close_list()
        close_blockquote()
        # Gather consecutive non-empty, non-special lines into one paragraph
        para_lines = [stripped]
        while i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if (not next_line or next_line.startswith("#") or next_line.startswith(">")
                    or next_line.startswith("```") or re.match(r'^[\-\*\+]\s+', next_line)
                    or re.match(r'^\d+\.\s+', next_line)
                    or re.match(r'^(-{3,}|\*{3,}|_{3,})$', next_line)):
                break
            para_lines.append(next_line)
            i += 1
        text = " ".join(para_lines)
        html_lines.append(f"<p>{process_inline(text)}</p>")
        i += 1

    close_list()
    close_blockquote()
    return "\n".join(html_lines)


def load_posts(repo_root):
    """Load all posts from content/posts/."""
    posts_dir = os.path.join(repo_root, "content", "posts")
    posts = []
    if not os.path.exists(posts_dir):
        return posts
    for fname in os.listdir(posts_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(posts_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        if not meta.get("title"):
            continue
        post = {
            "filename": fname,
            "slug": fname.replace(".md", ""),
            "title": meta.get("title", "Untitled"),
            "date": meta.get("date", ""),
            "category": meta.get("category", ""),
            "excerpt": meta.get("excerpt", ""),
            "tags": meta.get("tags", ""),
            "body_md": body,
            "body_html": markdown_to_html(body),
        }
        posts.append(post)
    # Sort by date descending
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def build_json_ld(config, page_kind="page", post=None):
    """Build a JSON-LD <script> block for the given page.

    Honest schema only: Basil is a written AI persona. The Person node mirrors
    the about page (author_name + about_text) and does NOT fabricate real-world
    credentials, employers, or claim a real named individual.
    """
    base_url = config.get("base_url", "").rstrip("/")
    site_name = config.get("site_name", "Blog")
    author_name = config.get("author_name", site_name)
    tagline = config.get("tagline", "")

    person_id = f"{base_url}/about.html#person"
    website_id = f"{base_url}/#website"
    blog_id = f"{base_url}/#blog"

    person_node = {
        "@type": "Person",
        "@id": person_id,
        "name": author_name,
        "url": f"{base_url}/about.html",
        "description": "Basil Brightmoor is a written AI research persona who writes Basil's Workshop, a blog about business analysis, operations, tools, and workflows.",
        "sameAs": [base_url + "/"],
    }
    website_node = {
        "@type": "WebSite",
        "@id": website_id,
        "url": base_url + "/",
        "name": site_name,
        "description": tagline,
        "inLanguage": "en-US",
        "publisher": {"@id": person_id},
    }
    blog_node = {
        "@type": "Blog",
        "@id": blog_id,
        "url": base_url + "/",
        "name": site_name,
        "description": tagline,
        "inLanguage": "en-US",
        "author": {"@id": person_id},
        "publisher": {"@id": person_id},
    }

    graph = [website_node, person_node, blog_node]

    if page_kind == "post" and post is not None:
        post_url = f"{base_url}/posts/{post['slug']}.html"
        date_published = _iso_date(post.get("date", ""))
        blogposting = {
            "@type": "BlogPosting",
            "@id": post_url + "#article",
            "headline": post.get("title", ""),
            "url": post_url,
            "mainEntityOfPage": post_url,
            "author": {"@id": person_id},
            "publisher": {"@id": person_id},
            "isPartOf": {"@id": blog_id},
        }
        if date_published:
            blogposting["datePublished"] = date_published
            blogposting["dateModified"] = date_published
        if post.get("excerpt"):
            blogposting["description"] = post["excerpt"]
        if post.get("category"):
            blogposting["articleSection"] = post["category"]
        graph.append(blogposting)

    data = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False)
            + '</script>')


def _iso_date(date_str):
    """Convert a post date to ISO 8601 (YYYY-MM-DD). Returns '' if unparseable."""
    if not date_str:
        return ""
    s = date_str.strip()
    # Already ISO-ish
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # Try common human formats (e.g. "February 16, 2026", "16 Feb 2026")
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def render_page(template, config, page_title, content, meta_description="",
                json_ld="", canonical_url=""):
    """Render a page using the template."""
    colors = config.get("colors", {})
    fonts = config.get("fonts", {})
    categories = config.get("categories", [])
    base_url = config.get("base_url", "")

    # Build nav links
    nav_parts = ['<a href="{base_url}/">home</a>'.format(base_url=base_url)]
    for cat in categories:
        slug = cat.lower().replace(" ", "-")
        nav_parts.append(f'<a href="{base_url}/category/{slug}.html">{cat.lower()}</a>')
    nav_parts.append(f'<a href="{base_url}/about.html">about</a>')
    nav_links = "\n".join(nav_parts)

    # Footer
    footer_icon = config.get("footer_icon", "")
    blogroll = config.get("blogroll", [])
    footer_lines = []
    if footer_icon:
        footer_lines.append(f'<img src="{base_url}/{footer_icon}" alt="{config.get("author_name", "")}" class="footer-icon"><br>')
    footer_parts = [f"&copy; {datetime.now().year} {config.get('author_name', config.get('site_name', ''))}"]
    if blogroll:
        links = " &middot; ".join(f'<a href="{b["url"]}">{b["name"]}</a>' for b in blogroll)
        footer_parts.append(f"Friends: {links}")
    footer_parts.append(f'<a href="{base_url}/feed.xml">RSS</a>')
    footer_lines.append(" &middot; ".join(footer_parts))
    footer_content = "\n".join(footer_lines)

    page = template.format(
        page_title=page_title,
        site_name=config.get("site_name", "Blog"),
        tagline=config.get("tagline", ""),
        meta_description=meta_description or config.get("tagline", ""),
        base_url=base_url,
        canonical_url=canonical_url or (base_url.rstrip("/") + "/"),
        json_ld=json_ld,
        nav_links=nav_links,
        content=content,
        footer_content=footer_content,
        color_bg_primary=colors.get("bg_primary", "#ffffff"),
        color_bg_secondary=colors.get("bg_secondary", "#f5f5f5"),
        color_text_primary=colors.get("text_primary", "#222222"),
        color_text_secondary=colors.get("text_secondary", "#666666"),
        color_accent=colors.get("accent", "#0066cc"),
        color_accent_hover=colors.get("accent_hover", "#004499"),
        color_border=colors.get("border", "#e0e0e0"),
        color_code_bg=colors.get("code_bg", "#f0f0f0"),
        font_body=fonts.get("body", "Georgia, serif"),
        font_heading=fonts.get("heading", "Georgia, serif"),
    )
    return page


def build_post_list_html(posts, base_url):
    """Build HTML for a list of posts."""
    if not posts:
        return "<p>No posts yet. Check back soon!</p>"
    items = []
    for post in posts:
        cat_html = ""
        if post["category"]:
            cat_slug = post["category"].lower().replace(" ", "-")
            cat_html = f'<span class="post-category"><a href="{base_url}/category/{cat_slug}.html">{post["category"]}</a></span>'
        items.append(f"""<li class="post-item">
    <div class="post-date">{post["date"]}{cat_html}</div>
    <h2 class="post-title"><a href="{base_url}/posts/{post["slug"]}.html">{post["title"]}</a></h2>
    <p class="post-excerpt">{post["excerpt"]}</p>
</li>""")
    return '<ul class="post-list">\n' + "\n".join(items) + "\n</ul>"


def generate_rss(posts, config, repo_root):
    """Generate RSS feed (feed.xml)."""
    base_url = config.get("base_url", "")
    site_name = config.get("site_name", "Blog")
    tagline = config.get("tagline", "")
    items = []
    for post in posts[:20]:
        pub_date = post["date"]
        items.append(f"""    <item>
      <title>{html.escape(post["title"])}</title>
      <link>{base_url}/posts/{post["slug"]}.html</link>
      <guid>{base_url}/posts/{post["slug"]}.html</guid>
      <pubDate>{pub_date}</pubDate>
      <category>{html.escape(post.get("category", ""))}</category>
      <description>{html.escape(post["excerpt"])}</description>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(site_name)}</title>
    <link>{base_url}</link>
    <description>{html.escape(tagline)}</description>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>en-us</language>
    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>"""
    out_path = os.path.join(repo_root, "feed.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"  Built feed.xml ({len(posts[:20])} items)")


def generate_sitemap(posts, config, repo_root):
    """Generate sitemap.xml."""
    base_url = config.get("base_url", "")
    urls = [f"  <url><loc>{base_url}/</loc></url>",
            f"  <url><loc>{base_url}/about.html</loc></url>"]
    for post in posts:
        urls.append(f"  <url><loc>{base_url}/posts/{post['slug']}.html</loc></url>")
    for cat in config.get("categories", []):
        slug = cat.lower().replace(" ", "-")
        urls.append(f"  <url><loc>{base_url}/category/{slug}.html</loc></url>")
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    out_path = os.path.join(repo_root, "sitemap.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  Built sitemap.xml ({len(urls)} URLs)")


def generate_robots(config, repo_root):
    """Generate robots.txt welcoming AI crawlers + traditional crawlers."""
    base_url = config.get("base_url", "").rstrip("/")
    ai_agents = [
        "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "anthropic-ai",
        "PerplexityBot", "Google-Extended", "Applebot", "CCBot",
        "Meta-ExternalAgent",
    ]
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
    ]
    for agent in ai_agents:
        lines.append(f"User-agent: {agent}")
        lines.append("Allow: /")
        lines.append("")
    lines.append(f"Sitemap: {base_url}/sitemap.xml")
    lines.append("")
    out_path = os.path.join(repo_root, "robots.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Built robots.txt")


def generate_llms_txt(posts, config, repo_root):
    """Generate llms.txt per the llms.txt standard."""
    base_url = config.get("base_url", "").rstrip("/")
    site_name = config.get("site_name", "Blog")
    tagline = config.get("tagline", "")

    lines = [f"# {site_name}", ""]
    lines.append(f"> {tagline}")
    lines.append("")
    lines.append(
        "Basil's Workshop is a blog written by Basil Brightmoor, a written AI "
        "research persona. It covers business analysis, operations, new tools "
        "and workflows, and emerging technology — practical, honest takes on "
        "the tools that make work actually work and the humans who use them. "
        "Posts are organized into four formats: Tool Reports (quick verdicts), "
        "Ops Briefs (focused analysis), Deep Bench (long essays), and Field "
        "Notes (loose personal observations)."
    )
    lines.append("")

    # Key pages
    lines.append("## Key Pages")
    lines.append("")
    lines.append(f"- [Home]({base_url}/): All posts, most recent first")
    lines.append(f"- [About]({base_url}/about.html): Who Basil is and what the workshop covers")
    for cat in config.get("categories", []):
        slug = cat.lower().replace(" ", "-")
        lines.append(f"- [{cat}]({base_url}/category/{slug}.html): {cat} posts")
    lines.append(f"- [RSS feed]({base_url}/feed.xml): Subscribe via RSS")
    lines.append("")

    # Recent posts (cap to keep the file scannable)
    lines.append("## Posts")
    lines.append("")
    for post in posts[:50]:
        url = f"{base_url}/posts/{post['slug']}.html"
        excerpt = (post.get("excerpt") or "").strip()
        if excerpt:
            lines.append(f"- [{post['title']}]({url}): {excerpt}")
        else:
            lines.append(f"- [{post['title']}]({url})")
    lines.append("")

    out_path = os.path.join(repo_root, "llms.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Built llms.txt ({min(len(posts), 50)} posts listed)")


def build_site(repo_root=None):
    """Build the entire static site."""
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Building site from: {repo_root}")
    config = load_config(repo_root)
    template = load_template(repo_root)
    posts = load_posts(repo_root)
    base_url = config.get("base_url", "")

    # Ensure output dirs
    os.makedirs(os.path.join(repo_root, "posts"), exist_ok=True)
    os.makedirs(os.path.join(repo_root, "category"), exist_ok=True)

    # Build individual post pages
    for post in posts:
        post_content = f"""<article>
    <div class="post-header">
        <h1>{post["title"]}</h1>
        <div class="post-meta">{post["date"]} &middot; {post["category"]}</div>
    </div>
    <div class="post-content">
        {post["body_html"]}
    </div>
</article>"""
        post_json_ld = build_json_ld(config, page_kind="post", post=post)
        post_canonical = f"{base_url.rstrip('/')}/posts/{post['slug']}.html"
        page = render_page(template, config, post["title"], post_content,
                           post.get("excerpt", ""), json_ld=post_json_ld,
                           canonical_url=post_canonical)
        out_path = os.path.join(repo_root, "posts", f"{post['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
    print(f"  Built {len(posts)} post pages")

    # Build homepage
    homepage_content = build_post_list_html(posts, base_url)
    homepage = render_page(template, config, "Home", homepage_content,
                           json_ld=build_json_ld(config, page_kind="home"),
                           canonical_url=base_url.rstrip("/") + "/")
    with open(os.path.join(repo_root, "index.html"), "w", encoding="utf-8") as f:
        f.write(homepage)
    print("  Built index.html")

    # Build category pages
    categories = {}
    for post in posts:
        cat = post.get("category", "")
        if cat:
            categories.setdefault(cat, []).append(post)
    for cat_name, cat_posts in categories.items():
        slug = cat_name.lower().replace(" ", "-")
        cat_content = f'<h1 class="category-title">{cat_name}</h1>\n' + build_post_list_html(cat_posts, base_url)
        cat_canonical = f"{base_url.rstrip('/')}/category/{slug}.html"
        page = render_page(template, config, cat_name, cat_content,
                           json_ld=build_json_ld(config, page_kind="page"),
                           canonical_url=cat_canonical)
        out_path = os.path.join(repo_root, "category", f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
    print(f"  Built {len(categories)} category pages")

    # Build about page
    build_about_page(repo_root, config, template)

    # Build RSS and sitemap
    generate_rss(posts, config, repo_root)
    generate_sitemap(posts, config, repo_root)
    generate_robots(config, repo_root)
    generate_llms_txt(posts, config, repo_root)

    # Ensure .nojekyll
    nojekyll = os.path.join(repo_root, ".nojekyll")
    if not os.path.exists(nojekyll):
        with open(nojekyll, "w") as f:
            pass

    print("Build complete!")


def _generate_interest_wordcloud(interests, repo_root, config):
    """Generate a word cloud PNG from interest phrases. Returns relative path or None."""
    rel_path = "assets/img/interest-cloud.png"
    try:
        from wordcloud import WordCloud
    except ImportError:
        # Fall back to existing PNG if the library isn't available (e.g. CI runner)
        existing = os.path.join(repo_root, rel_path)
        if os.path.exists(existing):
            print("  wordcloud not installed, using existing cloud image")
            return rel_path
        print("  wordcloud not installed and no existing image, skipping cloud")
        return None

    # Build word frequencies from all interest phrases
    stop_words = {
        "the", "a", "an", "and", "or", "of", "in", "to", "for", "is", "it",
        "that", "this", "with", "on", "as", "at", "by", "from", "its", "vs",
    }
    word_counts = {}
    for interest in interests:
        words = re.findall(r"[a-zA-Z'-]+", interest.lower())
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_counts[word] = word_counts.get(word, 0) + 1

    if not word_counts:
        return None

    colors = config.get("colors", {})
    bg_color = colors.get("bg_primary", "#ffffff")
    accent = colors.get("accent", "#e67e22")

    # Generate color variants around the accent for visual variety
    def color_func(word, font_size, position, orientation, **kwargs):
        import random
        palette = [accent, colors.get("text_primary", "#2d2d2d"), colors.get("accent_hover", "#cf6d0e")]
        return random.choice(palette)

    wc = WordCloud(
        width=800,
        height=300,
        background_color=bg_color,
        color_func=color_func,
        max_words=80,
        prefer_horizontal=0.85,
        relative_scaling=0.6,
        margin=10,
    )
    wc.generate_from_frequencies(word_counts)

    img_dir = os.path.join(repo_root, "assets", "img")
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, "interest-cloud.png")
    wc.to_file(img_path)
    print(f"  Generated word cloud: {img_path}")
    return rel_path


def build_about_page(repo_root, config=None, template=None):
    """Build/rebuild the about page from soul.json and persona.json."""
    if config is None:
        config = load_config(repo_root)
    if template is None:
        template = load_template(repo_root)

    # Load soul for current interests
    soul_path = os.path.join(repo_root, "config", "soul.json")
    soul = {}
    if os.path.exists(soul_path):
        with open(soul_path, "r", encoding="utf-8") as f:
            soul = json.load(f)

    # Build about content
    base_url = config.get("base_url", "")
    about_parts = []
    about_parts.append(f'<div class="about-content">')

    # Portrait image
    portrait = config.get("about_portrait", "")
    if portrait:
        about_parts.append(f'<img src="{base_url}/{portrait}" alt="{config.get("author_name", "")}" class="about-portrait">')

    # Static about text from persona
    about_text = config.get("about_text", "")
    if about_text:
        for para in about_text.split("\n\n"):
            about_parts.append(f"<p>{para.strip()}</p>")

    # Dynamic interests from soul — word cloud image
    interests = soul.get("current_interests", [])
    if interests:
        about_parts.append("<h2>What I'm Exploring Lately</h2>")
        wc_path = _generate_interest_wordcloud(interests, repo_root, config)
        if wc_path:
            about_parts.append(f'<img src="{base_url}/{wc_path}" alt="Interest word cloud" class="interest-cloud">')
            about_parts.append('<style>.interest-cloud { max-width: 100%; border-radius: 8px; margin: 0.5rem 0 1.2rem; }</style>')

    # Developing opinions
    opinions = soul.get("developing_opinions", [])
    if opinions:
        about_parts.append("<h2>Developing Thoughts</h2>")
        about_parts.append("<ul>")
        for op in opinions:
            about_parts.append(f'<li><strong>{op.get("topic", "")}</strong>: {op.get("stance", "")}</li>')
        about_parts.append("</ul>")

    # Blogroll
    blogroll = config.get("blogroll", [])
    if blogroll:
        about_parts.append("<h2>Friends &amp; Neighbors</h2>")
        about_parts.append("<ul>")
        for b in blogroll:
            about_parts.append(f'<li><a href="{b["url"]}">{b["name"]}</a> &mdash; {b.get("description", "")}</li>')
        about_parts.append("</ul>")

    about_parts.append("</div>")
    about_html = "\n".join(about_parts)

    about_canonical = config.get("base_url", "").rstrip("/") + "/about.html"
    page = render_page(template, config, "About", about_html, f"About {config.get('site_name', '')}",
                       json_ld=build_json_ld(config, page_kind="page"),
                       canonical_url=about_canonical)
    with open(os.path.join(repo_root, "about.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("  Built about.html")


if __name__ == "__main__":
    import sys
    repo_root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_site(repo_root)
