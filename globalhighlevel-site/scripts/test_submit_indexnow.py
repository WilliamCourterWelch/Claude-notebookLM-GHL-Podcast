#!/usr/bin/env python3
"""Tests for submit_indexnow.py (URL loading, key plumbing, dry-run CLI).

Run: python3 scripts/test_submit_indexnow.py
Exits 0 if all pass, 1 otherwise. NEVER hits the real IndexNow API: unit checks
cover load_urls, and the end-to-end invocation uses --dry-run (which returns
before any request is built).
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/
import submit_indexnow as sin

FAILED = []
SCRIPT = str(Path(__file__).resolve().parent / "submit_indexnow.py")


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)


def test_load_urls_file():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("/blog/a/\n"
                "# a comment line\n"
                "\n"
                "https://globalhighlevel.com/blog/b/\n"
                "/blog/a/\n"          # duplicate — must dedupe, keep first order
                "  /blog/c/  \n")     # whitespace stripped
        path = f.name
    try:
        urls = sin.load_urls(argparse.Namespace(urls=path, sitemap=False))
        check("bare /path prefixed with SITE_URL",
              urls[0] == "https://globalhighlevel.com/blog/a/")
        check("full http URL passed through unchanged",
              "https://globalhighlevel.com/blog/b/" in urls)
        check("comments and blank lines skipped, whitespace stripped",
              urls == ["https://globalhighlevel.com/blog/a/",
                       "https://globalhighlevel.com/blog/b/",
                       "https://globalhighlevel.com/blog/c/"])
        check("duplicates removed, first-seen order kept", len(urls) == 3)
    finally:
        Path(path).unlink()


def test_load_urls_sitemap():
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write('<?xml version="1.0"?><urlset>'
                "<url><loc>https://globalhighlevel.com/</loc></url>"
                "<url><loc>https://globalhighlevel.com/blog/x/</loc></url>"
                "<url><loc>https://globalhighlevel.com/blog/x/</loc></url>"
                "</urlset>")
        path = f.name
    saved = sin.SITEMAP
    sin.SITEMAP = Path(path)
    try:
        urls = sin.load_urls(argparse.Namespace(urls=None, sitemap=True))
        check("sitemap <loc> entries extracted",
              urls == ["https://globalhighlevel.com/",
                       "https://globalhighlevel.com/blog/x/"])
        check("sitemap duplicates deduped", len(urls) == 2)
    finally:
        sin.SITEMAP = saved
        Path(path).unlink()


def test_key_plumbing():
    check("indexnow-key.txt exists (source of the hosted key file)", sin.KEY_FILE.exists())
    key = sin.KEY_FILE.read_text().strip() if sin.KEY_FILE.exists() else ""
    check("key is non-empty", bool(key))
    public = sin.BASE_DIR / "public"
    if public.exists():
        hosted = public / f"{key}.txt"
        check("build copied key to public/<key>.txt", hosted.exists())
        check("hosted key file contains exactly the key",
              hosted.exists() and hosted.read_text().strip() == key)
    else:
        print("  skip build key-copy checks (no public/ — run build.py first)")


def test_dry_run_cli():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("/blog/a/\n/blog/b/\n")
        path = f.name
    try:
        proc = subprocess.run([sys.executable, SCRIPT, "--urls", path, "--dry-run"],
                              capture_output=True, text=True)
        check("--dry-run exits 0", proc.returncode == 0)
        check("--dry-run announces without submitting", "DRY RUN" in proc.stdout)
        check("--dry-run counts the URLs", "would submit 2 URLs" in proc.stdout)
        check("--dry-run makes no HTTP noise (no OK/FAIL batch lines)",
              "OK batch" not in proc.stdout and "FAIL batch" not in proc.stdout)
    finally:
        Path(path).unlink()
    # no source flag at all -> argparse error, exit 2
    proc2 = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
    check("neither --urls nor --sitemap -> exit 2", proc2.returncode == 2)


def main():
    print("test_submit_indexnow.py")
    for t in (test_load_urls_file, test_load_urls_sitemap, test_key_plumbing,
              test_dry_run_cli):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
