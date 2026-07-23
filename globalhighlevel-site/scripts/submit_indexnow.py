#!/usr/bin/env python3
"""submit_indexnow.py — push URLs to Bing via IndexNow after a deploy (D4, 2026-07-23).

Doctrine (full-restore sprint): IndexNow is the recrawl-notification channel that
fixes the Bing submission bottleneck — submit-bing.py (seo-ops-agent) stays as the
daily quota-capped fallback. Run this AFTER every deploy that adds or changes pages;
batch-1 (priority) URLs first when restoring.

The site must serve /<key>.txt containing the key (build.py copies it from
indexnow-key.txt into public/). IndexNow accepts up to 10,000 URLs per POST.

Usage:
    python3 scripts/submit_indexnow.py --urls FILE      # one URL or /path per line
    python3 scripts/submit_indexnow.py --sitemap        # every URL in public/sitemap.xml
    python3 scripts/submit_indexnow.py --urls FILE --dry-run

Exit 0 = every batch accepted (HTTP 200/202). Any non-2xx is printed LOUDLY and
exits 1 — a failed submit must never be swallowed (sprint failure-mode #7).
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SITE_URL = "https://globalhighlevel.com"
HOST = "globalhighlevel.com"
KEY_FILE = BASE_DIR / "indexnow-key.txt"
SITEMAP = BASE_DIR / "public" / "sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10000  # IndexNow per-POST limit


def load_urls(args) -> list[str]:
    if args.urls:
        lines = [ln.strip() for ln in Path(args.urls).read_text().splitlines()]
        urls = [ln if ln.startswith("http") else f"{SITE_URL}{ln}" for ln in lines if ln and not ln.startswith("#")]
    else:
        if not SITEMAP.exists():
            sys.exit(f"ERROR: {SITEMAP} not found — run build.py first (or pass --urls FILE)")
        urls = re.findall(r"<loc>(.*?)</loc>", SITEMAP.read_text())
    # dedupe, keep order
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", help="file with one URL or /path per line")
    ap.add_argument("--sitemap", action="store_true", help="submit every URL in public/sitemap.xml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.urls and not args.sitemap:
        ap.error("pass --urls FILE or --sitemap")

    key = KEY_FILE.read_text().strip() if KEY_FILE.exists() else ""
    if not key:
        sys.exit(f"ERROR: {KEY_FILE} missing or empty — generate the key first")

    urls = load_urls(args)
    if not urls:
        sys.exit("ERROR: no URLs to submit")
    print(f"IndexNow: {len(urls)} URLs -> {ENDPOINT} (host={HOST})")

    failed = 0
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        payload = {
            "host": HOST,
            "key": key,
            "keyLocation": f"{SITE_URL}/{key}.txt",
            "urlList": chunk,
        }
        if args.dry_run:
            print(f"  DRY RUN: would submit {len(chunk)} URLs (first: {chunk[0]})")
            continue
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:  # network failure is a loud failure, not a skip
            print(f"  FAIL batch {i // BATCH + 1}: {e}")
            failed += 1
            continue
        if 200 <= status < 300:
            print(f"  OK batch {i // BATCH + 1}: HTTP {status} ({len(chunk)} URLs)")
        else:
            print(f"  FAIL batch {i // BATCH + 1}: HTTP {status} ({len(chunk)} URLs) — NOT swallowed, fix and re-run")
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
