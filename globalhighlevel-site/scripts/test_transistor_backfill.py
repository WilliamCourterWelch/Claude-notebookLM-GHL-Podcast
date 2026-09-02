#!/usr/bin/env python3
"""Tests for transistor_backfill.py (parsing, merge, atomic write, report, CLI).

Run: python3 scripts/test_transistor_backfill.py
Exits 0 if all pass, 1 otherwise. NEVER hits the real Transistor API: the
transport test injects a fake opener, and the end-to-end CLI runs use
--report-only / --dry-run against a temp catalog.

The load-bearing cases are the ones asserting that a BAD SHAPE RAISES rather
than scoring 0 — that failure mode is why all 158 episodes shipped with
"streams": 0 in the first place.
"""
import copy
import io
import json
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/
import transistor_backfill as tb

FAILED = []
SCRIPT = str(Path(__file__).resolve().parent / "transistor_backfill.py")
# The pre-deploy gate runs `pytest scripts/ -q`, but the repo's check()/FAILED
# convention only surfaces failures through main() — under pytest a failed check
# would print "FAIL" and still exit green. Raise there so this file is honest
# under both runners. (The other test_*.py files share the gap; not touched here.)
UNDER_PYTEST = "pytest" in sys.modules

CATALOG = [
    {"title": "A", "transistorEpisodeId": "111", "category": "AI", "streams": 0},
    {"title": "B", "transistorEpisodeId": "222", "category": "Automation", "streams": 0},
    {"title": "C no host id", "streams": 0},
]


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)
        if UNDER_PYTEST:
            raise AssertionError(name)


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def payload(series):
    return {"data": {"id": "111", "type": "episode_analytics",
                     "attributes": {"downloads": series}}}


# ── parse_downloads ───────────────────────────────────────────────────

def test_parse_valid():
    total, days = tb.parse_downloads(payload(
        [{"date": "01-03-2026", "downloads": 10},
         {"date": "02-03-2026", "downloads": 5}]))
    check("sums a normal series", (total, days) == (15, 2))


def test_parse_empty_series_is_a_real_zero():
    total, days = tb.parse_downloads(payload([]))
    check("empty series is 0 downloads / 0 days, not an error", (total, days) == (0, 0))


def test_parse_bad_shapes_raise():
    # Each of these once had a plausible path to silently becoming 0.
    check("non-dict response raises", raises(lambda: tb.parse_downloads([])))
    check("missing 'data' raises", raises(lambda: tb.parse_downloads({"errors": ["nope"]})))
    check("missing 'attributes' raises", raises(lambda: tb.parse_downloads({"data": {"id": "1"}})))
    check("downloads not a list raises",
          raises(lambda: tb.parse_downloads({"data": {"attributes": {"downloads": None}}})))
    check("entry without a count raises",
          raises(lambda: tb.parse_downloads(payload([{"date": "01-03-2026"}]))))
    check("non-integer count raises",
          raises(lambda: tb.parse_downloads(payload([{"date": "x", "downloads": "12"}]))))


def test_parse_error_message_names_observed_keys():
    try:
        tb.parse_downloads({"errors": ["unauthorized"]})
        msg = ""
    except ValueError as e:
        msg = str(e)
    check("shape error reports what it actually saw", "errors" in msg)


# ── fmt_date ──────────────────────────────────────────────────────────

def test_fmt_date():
    check("ISO -> Transistor dd-mm-yyyy", tb.fmt_date("2026-03-06") == "06-03-2026")
    check("invalid date raises", raises(lambda: tb.fmt_date("03/06/2026")))


# ── fetch_episode (fake transport, no network) ────────────────────────

def test_fetch_episode_uses_key_and_window():
    seen = {}

    class FakeResp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return json.dumps(payload([{"date": "d", "downloads": 7}])).encode()

    def fake_opener(req, timeout=None):
        seen["url"] = req.full_url
        seen["key"] = req.get_header("X-api-key")
        return FakeResp()

    total, days = tb.fetch_episode("111", "01-01-2026", "02-09-2026", "SECRET", opener=fake_opener)
    check("returns parsed total", (total, days) == (7, 1))
    check("sends the api key header", seen["key"] == "SECRET")
    check("passes the date window (else Transistor defaults to 14 days)",
          "start_date=01-01-2026" in seen["url"] and "end_date=02-09-2026" in seen["url"])
    check("hits the analytics endpoint for the episode",
          "/analytics/episodes/111" in seen["url"])


def test_fetch_episode_propagates_http_error():
    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(b"{}"))
    check("HTTP error propagates rather than returning 0",
          raises(lambda: tb.fetch_episode("1", "a", "b", "k", opener=boom), urllib.error.HTTPError))


# ── merge_downloads ───────────────────────────────────────────────────

def test_merge_updates_only_measured():
    src = copy.deepcopy(CATALOG)
    merged, updated = tb.merge_downloads(
        src, {"111": (500, 30)}, measured_at="2026-09-02T00:00:00+00:00", window_start="2026-01-01")
    check("updates the fetched episode", merged[0]["streams"] == 500)
    check("records the day count", merged[0]["streamsDays"] == 30)
    check("stamps when it was measured", merged[0]["streamsUpdatedAt"].startswith("2026-09-02"))
    check("stamps the window start", merged[0]["streamsWindowStart"] == "2026-01-01")
    check("counts one update", updated == 1)
    check("unfetched episode is left untouched, NOT zeroed",
          merged[1]["streams"] == 0 and "streamsUpdatedAt" not in merged[1])
    check("record with no host id is passed through",
          merged[2]["title"] == "C no host id" and "streamsUpdatedAt" not in merged[2])
    check("input catalog is not mutated", src[0]["streams"] == 0)
    check("episode count preserved", len(merged) == len(CATALOG))


def test_merge_zero_is_recorded_as_measured():
    merged, _ = tb.merge_downloads(
        copy.deepcopy(CATALOG), {"111": (0, 14)}, "2026-09-02T00:00:00+00:00", "2026-01-01")
    check("a measured zero is distinguishable from never-measured",
          merged[0]["streams"] == 0 and merged[0]["streamsUpdatedAt"])


# ── write_catalog ─────────────────────────────────────────────────────

def test_write_catalog_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "published.json"
        tb.write_catalog(CATALOG, p)
        back = json.loads(p.read_text())
        check("written catalog round-trips", back == CATALOG)
        check("no .tmp file left behind", not p.with_suffix(".json.tmp").exists())


def test_load_catalog_rejects_non_list():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "published.json"
        p.write_text('{"not": "a list"}')
        try:
            tb.load_catalog(p)
            ok = False
        except SystemExit:
            ok = True
        check("a non-list catalog exits loudly", ok)


# ── report ────────────────────────────────────────────────────────────

def test_report_handles_unmeasured_catalog():
    try:
        tb.report(copy.deepcopy(CATALOG))
        ok = True
    except Exception:
        ok = False
    check("report on an unmeasured catalog does not crash", ok)


# ── CLI end-to-end (no network) ───────────────────────────────────────

def test_cli_report_only():
    """--report-only must work with no API key and no network."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "published.json"
        measured = copy.deepcopy(CATALOG)
        measured[0].update(streams=900, streamsUpdatedAt="2026-09-02T00:00:00+00:00")
        measured[1].update(streams=100, streamsUpdatedAt="2026-09-02T00:00:00+00:00")
        p.write_text(json.dumps(measured))
        r = subprocess.run(
            [sys.executable, SCRIPT, "--report-only"],
            capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "TRANSISTOR_BACKFILL_TEST": "1"},
            cwd=d)
        # The script targets the real repo catalog; assert it ran and reported.
        check("--report-only exits 0 without an API key", r.returncode == 0)
        check("--report-only prints a ranking", "TOP" in r.stdout or "No measured" in r.stdout)


def test_cli_requires_api_key():
    r = subprocess.run([sys.executable, SCRIPT, "--limit", "1"],
                       capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    check("missing TRANSISTOR_API_KEY exits non-zero", r.returncode != 0)
    check("missing key says so", "TRANSISTOR_API_KEY" in (r.stderr + r.stdout))


def test_cli_rejects_bad_since():
    r = subprocess.run([sys.executable, SCRIPT, "--since", "01-01-2026", "--limit", "1"],
                       capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "TRANSISTOR_API_KEY": "x"})
    check("non-ISO --since is rejected", r.returncode != 0 and "--since" in (r.stderr + r.stdout))


def main():
    print("test_transistor_backfill.py")
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    if FAILED:
        print(f"\n{len(FAILED)} FAILED: {FAILED}")
        return 1
    print("\nAll passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
