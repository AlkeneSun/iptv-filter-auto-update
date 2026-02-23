#!/usr/bin/env python3
"""Fetch and filter an IPTV M3U playlist by group-title."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

DEFAULT_SOURCE_URLS = [
    "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
    "https://gh-proxy.org/https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
]

DEFAULT_GROUP_KEYWORDS = [
    "[三网]央卫视直播",
    "[联通]咪视界直播",
]

GROUP_TITLE_PATTERN = re.compile(r'group-title="([^"]*)"')


def fetch_text(urls: list[str], timeout: int = 30) -> tuple[str, str]:
    headers = {"User-Agent": "Mozilla/5.0 (playlist-filter/1.0)"}
    last_error: Exception | None = None

    for url in urls:
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
            return raw.decode("utf-8-sig", errors="replace"), url
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc

    if last_error is None:
        raise RuntimeError("no source URLs were provided")
    raise RuntimeError(f"failed to fetch source playlist: {last_error}") from last_error


def extract_group_title(extinf_line: str) -> str:
    match = GROUP_TITLE_PATTERN.search(extinf_line)
    return match.group(1) if match else ""


def filter_playlist(text: str, keywords: list[str]) -> tuple[str, Counter]:
    lines = text.splitlines()

    header = "#EXTM3U"
    for line in lines:
        normalized = line.lstrip("\ufeff").strip()
        if normalized.startswith("#EXTM3U"):
            header = normalized
            break

    output_lines = [header]
    kept_by_group: Counter = Counter()

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line.startswith("#EXTINF"):
            index += 1
            continue

        group_title = extract_group_title(line)
        should_keep = any(keyword in group_title for keyword in keywords)

        next_index = index + 1
        stream_url = None
        while next_index < len(lines):
            candidate = lines[next_index].strip()
            if not candidate:
                next_index += 1
                continue
            if candidate.startswith("#"):
                next_index += 1
                continue
            stream_url = candidate
            break

        if stream_url and should_keep:
            output_lines.append(line)
            output_lines.append(stream_url)
            kept_by_group[group_title] += 1

        index = next_index + 1 if stream_url else index + 1

    return "\n".join(output_lines) + "\n", kept_by_group


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter an M3U playlist by group-title keywords."
    )
    parser.add_argument(
        "--source-url",
        action="append",
        dest="source_urls",
        help="Source M3U URL. Can be provided multiple times.",
    )
    parser.add_argument(
        "--group-keyword",
        action="append",
        dest="group_keywords",
        help="group-title keyword to keep. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        default="playlist.m3u",
        help="Output playlist file path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_urls = args.source_urls or DEFAULT_SOURCE_URLS
    group_keywords = args.group_keywords or DEFAULT_GROUP_KEYWORDS
    output_path = Path(args.output)

    text, selected_url = fetch_text(source_urls)
    filtered_text, kept_by_group = filter_playlist(text, group_keywords)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(filtered_text, encoding="utf-8")

    total_entries = sum(kept_by_group.values())
    print(f"source: {selected_url}")
    print(f"output: {output_path}")
    print(f"kept entries: {total_entries}")
    for group, count in sorted(kept_by_group.items()):
        print(f"  {group}: {count}")

    if total_entries == 0:
        print("warning: no entries matched the configured group keywords", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
