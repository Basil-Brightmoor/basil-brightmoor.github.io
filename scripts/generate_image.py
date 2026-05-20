#!/usr/bin/env python3
"""Hero image generator using Gemini 2.5 Flash Image.

Stdlib-only. Reads GEMINI_API_KEY from env. Returns the saved filename
relative to repo root (e.g. "images/2026-05-18-foo.png"), or None on failure.
Soft-fails — never raises — so the post pipeline survives if the key is
missing or the API hiccups.
"""

import base64
import json
import os
import ssl
import urllib.error
import urllib.request

GEMINI_MODEL = "gemini-2.5-flash-image"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


def generate_hero_image(prompt, repo_root, out_basename):
    """Generate one image from prompt, save under images/, return relative path.

    out_basename: filename stem without extension, e.g. "2026-05-18-wires-not-chips".
    Returns "images/<basename>.png" on success, None on any failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("  [image] GEMINI_API_KEY not set — skipping image generation")
        return None

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  [image] Gemini API error {e.code}: {body[:300]}")
        return None
    except Exception as e:
        print(f"  [image] Request failed: {e}")
        return None

    image_b64 = None
    for cand in result.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                image_b64 = inline["data"]
                break
        if image_b64:
            break

    if not image_b64:
        finish = (result.get("candidates") or [{}])[0].get("finishReason", "?")
        print(f"  [image] No image data in response (finishReason={finish})")
        return None

    images_dir = os.path.join(repo_root, "images")
    os.makedirs(images_dir, exist_ok=True)
    out_path = os.path.join(images_dir, f"{out_basename}.png")
    try:
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(image_b64))
    except Exception as e:
        print(f"  [image] Write failed: {e}")
        return None

    rel = f"images/{out_basename}.png"
    print(f"  [image] Saved: {rel}")
    return rel
