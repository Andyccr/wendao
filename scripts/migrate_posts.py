#!/usr/bin/env python3
"""Convert Andyccr/Blog static HTML posts into Hugo Markdown."""

from __future__ import annotations

import base64
import hashlib
import html as html_lib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/tmp/old-blog")
POSTS_DIR = ROOT / "content" / "posts"
IMAGES_DIR = ROOT / "static" / "images" / "posts"
REPORT = ROOT / "scripts" / "migration-report.json"

ORIGINAL_HOST = "https://andychen.net"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

LOCAL_HOSTS = {
    "blog.andyccr.com",
    "192.144.164.198",
    "andychen.net",
    "www.andychen.net",
    "andyccr.com",
    "www.andyccr.com",
}

WAYBACK_KNOWN = {
    "http://blog.andyccr.com/wp-content/uploads/2021/10/屏幕截图304-1024x576.png": "20220224075424",
    "http://blog.andyccr.com/wp-content/uploads/2021/10/QQ图片20211007163236-485x1024.jpg": "20220224075420",
    "http://blog.andyccr.com/wp-content/uploads/2021/10/QQ图片20211007163243-485x1024.jpg": "20220206174734",
    "http://blog.andyccr.com/wp-content/uploads/2021/10/QQ图片20211007163254-1024x768.jpg": "20220224135257",
}

MORE_RE = re.compile(r"<!-?\s*<ul><li>\s*more\s*--></li></ul>", re.IGNORECASE)
INLINE_UL_RE = re.compile(r"<ul><li>(.*?)</li></ul>", re.DOTALL)
BANG_LINK_RE = re.compile(
    r"!<a href=\"([^\"]+)\"(?:[^>]*)>(.*?)</a>",
    re.DOTALL | re.IGNORECASE,
)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})")
INDEX_ITEM_RE = re.compile(
    r'<a href="([^"]+)">([^<]*)</a>\s*<div class="post-date">([^<]+)</div>',
    re.DOTALL,
)
IMAGE_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def iri_to_uri(url: str) -> str:
    parts = urllib.parse.urlsplit(url.strip())
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(parts.query, safe="=&%:@!$&'()*+,;=-._~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def parse_index(index_html: str) -> list[dict]:
    items = []
    for href, title, date in INDEX_ITEM_RE.findall(index_html):
        items.append(
            {
                "file": href,
                "title": BeautifulSoup(title, "html.parser").get_text(),
                "date": date.strip(),
            }
        )
    return items


def extract_body_html(raw: str) -> tuple[str | None, str]:
    dt_match = DATE_RE.search(raw)
    timestamp = None
    if dt_match:
        timestamp = f"{dt_match.group(1)} {dt_match.group(2)}"
        body = raw[dt_match.end() :]
    else:
        body = raw
    body = re.split(r"</body>", body, maxsplit=1, flags=re.IGNORECASE)[0]
    body = re.sub(r"^(\s*<br\s*/?>)+", "", body, flags=re.IGNORECASE)
    body = MORE_RE.sub("", body)
    body = INLINE_UL_RE.sub(r"*\1", body)
    body = BANG_LINK_RE.sub(r'<img src="\1" alt="\2">', body)
    return timestamp, body.strip()


def replace_tag_with_text(soup: BeautifulSoup, tag, text: str) -> None:
    tag.replace_with(NavigableString(text))


PRE_RE = re.compile(r"<pre\b[^>]*>([\s\S]*?)</pre>", re.IGNORECASE)
CODE_WRAP_RE = re.compile(r"^<code\b[^>]*>([\s\S]*)</code>$", re.IGNORECASE)


def fence_pre(inner: str) -> str:
    inner = inner.strip()
    wrapped = CODE_WRAP_RE.match(inner)
    if wrapped:
        inner = wrapped.group(1)
    inner = html_lib.unescape(inner)
    return f"\n```\n{inner.strip('\n')}\n```\n"


def html_to_markdown(body_html: str) -> str:
    placeholders: list[str] = []

    def stash_pre(match: re.Match[str]) -> str:
        placeholders.append(fence_pre(match.group(1)))
        return f"\n[[[PRE{len(placeholders) - 1}]]]\n"

    body_html = PRE_RE.sub(stash_pre, body_html)
    soup = BeautifulSoup(body_html, "html.parser")
    for tag in soup.find_all(["script", "style", "button"]):
        tag.decompose()

    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        alt = (img.get("alt") or "").strip()
        replace_tag_with_text(soup, img, f"![{alt}]({src})")

    for anchor in soup.find_all("a"):
        href = (anchor.get("href") or "").strip()
        text = anchor.get_text()
        if href:
            replace_tag_with_text(soup, anchor, f"[{text}]({href})")
        else:
            anchor.unwrap()

    for tag_name, wrap in (("strong", "**"), ("b", "**"), ("em", "*"), ("i", "*")):
        for el in soup.find_all(tag_name):
            replace_tag_with_text(soup, el, f"{wrap}{el.get_text()}{wrap}")

    for level, name in enumerate(("h1", "h2", "h3", "h4"), start=1):
        for el in soup.find_all(name):
            replace_tag_with_text(soup, el, f"\n{'#' * level} {el.get_text().strip()}\n")

    for br in soup.find_all("br"):
        replace_tag_with_text(soup, br, "\n")

    text = soup.get_text()
    for index, block in enumerate(placeholders):
        text = text.replace(f"[[[PRE{index}]]]", block)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def ascii_name(name: str) -> str:
    stem = Path(name).stem
    suffix = Path(name).suffix.lower() or ".bin"
    safe = []
    for ch in stem:
        if ch.isascii() and (ch.isalnum() or ch in "-_."):
            safe.append(ch)
        else:
            safe.append("-")
    cleaned = re.sub(r"-{2,}", "-", "".join(safe)).strip("-") or "file"
    if len(cleaned) > 60:
        cleaned = cleaned[:60]
    return cleaned + suffix


def fetch_bytes(url: str, timeout: int = 20) -> bytes | None:
    try:
        encoded = iri_to_uri(url)
    except Exception:
        encoded = url
    req = urllib.request.Request(encoded, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if not data:
                return None
            ctype = resp.headers.get("Content-Type", "")
            if "text/html" in ctype and len(data) < 8000:
                return None
            return data
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None


def wayback_candidates(url: str) -> list[str]:
    variants = [url, url.replace("https://", "http://")]
    decoded = urllib.parse.unquote(url)
    if decoded not in variants:
        variants.append(decoded)
    out = []
    for original, stamp in WAYBACK_KNOWN.items():
        original_path = urllib.parse.unquote(urllib.parse.urlsplit(original).path)
        for variant in variants:
            variant_path = urllib.parse.unquote(urllib.parse.urlsplit(variant).path)
            if original_path == variant_path or original == variant:
                out.append(f"https://web.archive.org/web/{stamp}id_/{iri_to_uri(original)}")
                break
    return out


def is_local_media(url: str) -> bool:
    if url.startswith("data:image/"):
        return True
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return host in LOCAL_HOSTS


def save_image(slug: str, url: str, used: dict[str, str], failed: list[dict]) -> str:
    url = url.strip().strip("<>")
    if url in used:
        return used[url]

    if url.startswith("data:image/"):
        header, _, data = url.partition(",")
        ext = "png"
        if "jpeg" in header or "jpg" in header:
            ext = "jpg"
        elif "gif" in header:
            ext = "gif"
        elif "webp" in header:
            ext = "webp"
        raw = base64.b64decode(data)
        name = f"embedded-{hashlib.sha1(raw).hexdigest()[:10]}.{ext}"
        dest_dir = IMAGES_DIR / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / name).write_bytes(raw)
        rel = f"images/posts/{slug}/{name}"
        used[url] = rel
        return rel

    if not is_local_media(url):
        used[url] = url
        return url

    parsed = urllib.parse.urlsplit(url)
    filename = ascii_name(urllib.parse.unquote(Path(parsed.path).name or "image"))
    dest_dir = IMAGES_DIR / slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    if dest.exists() and dest.stat().st_size > 0:
        rel = f"images/posts/{slug}/{filename}"
        used[url] = rel
        return rel

    host = (parsed.hostname or "").lower()
    candidates: list[str] = []
    # These origins are currently unreachable; prefer Wayback when we have a capture.
    if host not in {"blog.andyccr.com", "192.144.164.198"}:
        candidates.append(url)
        if url.startswith("http://"):
            candidates.append("https://" + url[len("http://") :])
    candidates.extend(wayback_candidates(url))

    data = None
    for candidate in candidates:
        data = fetch_bytes(candidate)
        if data:
            break
    if not data:
        failed.append({"slug": slug, "url": url})
        used[url] = url
        return url

    dest.write_bytes(data)
    rel = f"images/posts/{slug}/{filename}"
    used[url] = rel
    return rel


def rewrite_images(markdown: str, slug: str, used: dict[str, str], failed: list[dict]) -> str:
    def md_repl(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2).strip().strip("<>")
        local = save_image(slug, url, used, failed)
        return f"![{alt}]({local})"

    return IMAGE_MD_RE.sub(md_repl, markdown)


def dump_front_matter(data: dict) -> str:
    dumped = yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    return f"---\n{dumped}---\n"


def main() -> int:
    if not SOURCE.exists():
        print(f"missing source tree: {SOURCE}", file=sys.stderr)
        return 1

    index = parse_index((SOURCE / "index.html").read_text(encoding="utf-8"))
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for old in POSTS_DIR.glob("*.md"):
        old.unlink()

    report = {
        "imported": [],
        "images_saved": [],
        "images_failed": [],
        "skipped": ["index.html", "ads.txt", "CNAME", "dark.js", "styles.css", "README.md"],
    }
    used_images: dict[str, str] = {}

    for item in index:
        src = SOURCE / item["file"]
        raw = src.read_text(encoding="utf-8")
        timestamp, body_html = extract_body_html(raw)
        if timestamp:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(item["date"], "%Y-%m-%d")
        slug = Path(item["file"]).stem
        markdown = html_to_markdown(body_html)
        markdown = rewrite_images(markdown, slug, used_images, report["images_failed"])
        fm = {
            "title": item["title"],
            "date": dt.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "slug": slug,
            "original_url": f"{ORIGINAL_HOST}/{item['file']}",
        }
        dest = POSTS_DIR / f"{slug}.md"
        dest.write_text(dump_front_matter(fm) + "\n" + markdown, encoding="utf-8")
        report["imported"].append(
            {
                "title": item["title"],
                "date": item["date"],
                "slug": slug,
                "file": str(dest.relative_to(ROOT)),
            }
        )

    report["images_saved"] = sorted(
        {v for v in used_images.values() if not v.startswith("http") and not v.startswith("data:")}
    )
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"imported {len(report['imported'])} posts")
    print(f"images saved {len(report['images_saved'])}")
    print(f"images failed {len(report['images_failed'])}")
    for item in report["images_failed"]:
        print("  fail", item["url"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
