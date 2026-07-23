#!/usr/bin/env python3
"""Tests for submit_indexnow.py (URL loading, key plumbing, batch loop, dry-run CLI).

Run: python3 scripts/test_submit_indexnow.py
Exits 0 if all pass, 1 otherwise. NEVER hits the real IndexNow API: unit checks
cover load_urls, the batch-loop tests monkeypatch urllib.request.urlopen inside
submit_indexnow, and the end-to-end invocation uses --dry-run (which returns
before any request is built).
"""
import argparse
import io
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
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


def test_load_urls_rejects_bad_lines():
    # a bare "blog/x" would silently become SITE_URLblog/x; an off-site URL would
    # poison the batch — both must fail loudly, not be submitted.
    for bad in ("blog/x", "https://other.com/y"):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(f"{bad}\n")
            path = f.name
        try:
            sin.load_urls(argparse.Namespace(urls=path, sitemap=False))
            check(f"invalid line {bad!r} raises SystemExit", False)
        except SystemExit as exc:
            check(f"invalid line {bad!r} raises SystemExit", "invalid URL line" in str(exc))
        finally:
            Path(path).unlink()


class FakeResponse:
    """Context-manager stand-in for urlopen's response."""

    def __init__(self, status=200, body=b""):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def run_main_patched(urlopen, urls_lines=("/blog/a/", "/blog/b/")):
    """Call sin.main() in-process with --urls FILE and urlopen monkeypatched."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(urls_lines) + "\n")
        path = f.name
    saved_urlopen, saved_argv = sin.urllib.request.urlopen, sys.argv
    sin.urllib.request.urlopen = urlopen
    sys.argv = ["submit_indexnow.py", "--urls", path]
    try:
        return sin.main()
    finally:
        sin.urllib.request.urlopen = saved_urlopen
        sys.argv = saved_argv
        Path(path).unlink()


def make_urlopen(key, batch_effect, calls):
    """urlopen fake: preflight (URL string) serves the right key; batch (Request
    object) is recorded and delegated to batch_effect(request)."""
    def fake_urlopen(url_or_req, timeout=None):
        if isinstance(url_or_req, urllib.request.Request):
            calls.append(url_or_req)
            return batch_effect(url_or_req)
        return FakeResponse(200, key.encode("utf-8"))
    return fake_urlopen


def test_batch_loop():
    key = sin.KEY_FILE.read_text().strip()

    # all batches 200 -> exit 0; payload has the documented IndexNow shape
    calls = []
    rc = run_main_patched(make_urlopen(key, lambda req: FakeResponse(200), calls))
    check("all-200 run returns 0", rc == 0)
    check("exactly one batch POSTed (2 URLs, batch=10000)", len(calls) == 1)
    payload = json.loads(calls[0].data.decode("utf-8")) if calls else {}
    check("payload host matches", payload.get("host") == sin.HOST)
    check("payload key matches the key file", payload.get("key") == key)
    check("payload keyLocation is SITE_URL/<key>.txt",
          payload.get("keyLocation") == f"{sin.SITE_URL}/{key}.txt")
    check("payload urlList carries the submitted URLs",
          payload.get("urlList") == [f"{sin.SITE_URL}/blog/a/", f"{sin.SITE_URL}/blog/b/"])

    # HTTPError 429 on the batch POST -> loud failure, exit 1
    def raise_429(req):
        raise urllib.error.HTTPError(sin.ENDPOINT, 429, "Too Many Requests",
                                     {}, io.BytesIO(b"slow \x1bdown"))
    calls = []
    rc = run_main_patched(make_urlopen(key, raise_429, calls))
    check("HTTPError 429 returns 1", rc == 1)

    # network failure (URLError) -> loud failure, exit 1
    def raise_neterr(req):
        raise urllib.error.URLError("connection refused")
    calls = []
    rc = run_main_patched(make_urlopen(key, raise_neterr, calls))
    check("URLError/network exception returns 1", rc == 1)


def test_preflight_key_liveness():
    # the hosted key file serving the WRONG key must abort before any submit
    batch_calls = []

    def wrong_key_urlopen(url_or_req, timeout=None):
        if isinstance(url_or_req, urllib.request.Request):
            batch_calls.append(url_or_req)
            return FakeResponse(200)
        return FakeResponse(200, b"not-the-key")

    try:
        run_main_patched(wrong_key_urlopen)
        check("wrong hosted key -> SystemExit", False)
    except SystemExit as exc:
        check("wrong hosted key -> SystemExit", "wrong key" in str(exc))
    check("no batch submitted after failed preflight", batch_calls == [])


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
    for t in (test_load_urls_file, test_load_urls_sitemap,
              test_load_urls_rejects_bad_lines, test_key_plumbing,
              test_batch_loop, test_preflight_key_liveness, test_dry_run_cli):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
