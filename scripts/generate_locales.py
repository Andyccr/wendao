#!/usr/bin/env python3
"""Build Traditional Chinese and English content trees from Simplified sources."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
ZHS = ROOT / "content" / "zhs"
ZHT = ROOT / "content" / "zht"
EN = ROOT / "content" / "en"

KEEP_KEYS = {"slug", "date", "original_url", "layout", "translationKey"}
FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def split_front_matter(text: str) -> tuple[str, str]:
    match = FM_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end() :]


def prose_stats(body: str) -> tuple[int, int]:
    stripped = re.sub(r"```[\s\S]*?```", " ", body)
    stripped = re.sub(r"`[^`]+`", " ", stripped)
    stripped = re.sub(r"https?://\S+", " ", stripped)
    stripped = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", stripped)
    stripped = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", stripped)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", stripped))
    latin = len(re.findall(r"[A-Za-z]", stripped))
    return cjk, latin


def fm_title(fm: str) -> str:
    for line in fm.splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def is_english_original(title: str, body: str) -> bool:
    if re.search(r"[\u4e00-\u9fff]", title):
        return False
    cjk, latin = prose_stats(body)
    if cjk == 0 and latin >= 20:
        return True
    if latin >= 40 and cjk / (cjk + latin) < 0.20:
        return True
    return False


def convert_front_matter(fm: str, converter: OpenCC) -> str:
    out = []
    for line in fm.splitlines():
        if ":" not in line:
            out.append(line)
            continue
        key, _, value = line.partition(":")
        if key.strip() in KEEP_KEYS:
            out.append(line)
        else:
            out.append(f"{key}:{converter.convert(value)}")
    return "\n".join(out)


def convert_file(src: Path, dest: Path, converter: OpenCC | None) -> None:
    text = src.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    if converter:
        fm = convert_front_matter(fm, converter)
        body = converter.convert(body)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


def main() -> int:
    if not ZHS.exists():
        print(f"missing {ZHS}", file=sys.stderr)
        return 1

    converter = OpenCC("s2t")
    if ZHT.exists():
        shutil.rmtree(ZHT)
    if EN.exists():
        shutil.rmtree(EN)

    english_posts: list[str] = []
    for src in ZHS.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(ZHS)
        convert_file(src, ZHT / rel, converter)
        if rel.parts[:1] == ("posts",) and src.suffix == ".md" and src.name != "_index.md":
            fm, body = split_front_matter(src.read_text(encoding="utf-8"))
            if is_english_original(fm_title(fm), body):
                convert_file(src, EN / rel, None)
                english_posts.append(str(rel))

    en_about = """---
title: About
---

Andy Chen's personal blog Wendao.

GitHub: [Andyccr](https://github.com/Andyccr)
"""
    en_archives = """---
title: Archive
layout: archives
---
"""
    en_index = """---
---
"""
    en_posts_index = """---
title: Posts
---
"""
    (EN / "about.md").write_text(en_about, encoding="utf-8")
    (EN / "archives.md").write_text(en_archives, encoding="utf-8")
    (EN / "_index.md").write_text(en_index, encoding="utf-8")
    (EN / "posts").mkdir(parents=True, exist_ok=True)
    (EN / "posts" / "_index.md").write_text(en_posts_index, encoding="utf-8")

    print(f"zht files: {sum(1 for _ in ZHT.rglob('*') if _.is_file())}")
    print(f"en posts: {len(english_posts)}")
    for name in english_posts:
        print(" ", name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
