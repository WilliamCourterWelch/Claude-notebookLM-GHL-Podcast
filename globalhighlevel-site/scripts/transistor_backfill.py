#!/usr/bin/env python3
"""transistor_backfill.py — fill the dead `streams` field in data/published.json.

WHY THIS EXISTS
All 158 episodes in `published.json` carry `"streams": 0`. The field was written
by the retired pipeline and never populated, so the catalog records WHAT was
published but not WHAT WORKED. Spotify reports ~10,245 all-time plays and 561 in
the last 30 days against a catalog that has been dormant since April — but there
is no per-episode breakdown anywhere in the repo, so "make more of what works"
has no input. This script asks Transistor (the host of record — every episode
already carries a `transistorEpisodeId`) and writes the answer back.

Read-only against the site: `build.py` reads `transistorEpisodeId` and never
reads `streams`, so a backfill cannot change a single byte of built output.

DOCTRINE — a missing number must never look like a zero
The reason this field is dead is that something once wrote 0 and moved on. So:
an episode whose analytics come back in an unrecognised shape RAISES; it does
not quietly score 0. A genuine zero (Transistor returns an empty series) is
recorded as 0 with `streamsDays: 0`, which is distinguishable from "never
measured" (`streamsUpdatedAt` absent). Any per-episode failure is reported and
exits 1 — a half-backfill that looks complete is worse than no backfill.

API
    GET https://api.transistor.fm/v1/analytics/episodes/{id}?start_date=&end_date=
    Header: x-api-key: $TRANSISTOR_API_KEY
Transistor's analytics window DEFAULTS TO 14 DAYS — the date range is required
for all-time totals, and its date format is dd-mm-yyyy (not ISO). Omitting the
range is the easy way to silently backfill two weeks of data as if it were the
lifetime number.

Usage:
    export TRANSISTOR_API_KEY=...
    python3 scripts/transistor_backfill.py --dry-run          # fetch + report, write nothing
    python3 scripts/transistor_backfill.py --limit 5 --dry-run # smoke-test 5 episodes
    python3 scripts/transistor_backfill.py                     # fetch + write published.json
    python3 scripts/transistor_backfill.py --report-only       # re-report from existing data, no network

Exit 0 = every episode fetched cleanly. Exit 1 = at least one failed (loudly).
"""
import argparse
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLISHED_JSON = BASE_DIR / "data" / "published.json"
API_BASE = "https://api.transistor.fm/v1"
# Transistor's documented limit is 10 requests / 10 seconds. 1.0s between calls
# keeps a 158-episode run (~2.6 min) comfortably inside it without a backoff loop.
DEFAULT_SLEEP = 1.0
# The show's first episode is 2026-03; anything earlier is a safe floor for "all time".
DEFAULT_SINCE = "2026-01-01"
USER_AGENT = "ghl-transistor-backfill"


def fmt_date(iso: str) -> str:
    """ISO yyyy-mm-dd -> Transistor's dd-mm-yyyy. Raises on anything else."""
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%d-%m-%Y")


def load_catalog(path: Path = PUBLISHED_JSON) -> list:
    if not path.exists():
        sys.exit(f"ERROR: {path} not found")
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        sys.exit(f"ERROR: {path} is {type(data).__name__}, expected a list of episodes")
    return data


def parse_downloads(payload: dict) -> tuple[int, int]:
    """Extract (total_downloads, days_of_data) from a Transistor analytics payload.

    Returns (0, 0) for a valid response carrying an empty series — a real zero.
    Raises ValueError if the shape is not recognised, so an API change or an
    error body can never be mistaken for an episode that nobody listened to.
    """
    if not isinstance(payload, dict):
        raise ValueError(f"response is {type(payload).__name__}, expected an object")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError(f"no 'data' object in response (keys: {sorted(payload)})")
    attrs = data.get("attributes")
    if not isinstance(attrs, dict):
        raise ValueError(f"no 'data.attributes' object (data keys: {sorted(data)})")
    downloads = attrs.get("downloads")
    if not isinstance(downloads, list):
        raise ValueError(
            f"'data.attributes.downloads' is {type(downloads).__name__}, expected a list "
            f"(attribute keys: {sorted(attrs)})"
        )
    total = 0
    for entry in downloads:
        if not isinstance(entry, dict) or "downloads" not in entry:
            raise ValueError(f"unexpected entry in downloads series: {entry!r}")
        n = entry["downloads"]
        if not isinstance(n, int):
            raise ValueError(f"non-integer download count: {n!r}")
        total += n
    return total, len(downloads)


def fetch_episode(episode_id: str, start: str, end: str, api_key: str,
                  opener=urllib.request.urlopen) -> tuple[int, int]:
    """Fetch one episode's all-time downloads. Raises on transport or shape failure."""
    qs = urllib.parse.urlencode({"start_date": start, "end_date": end})
    req = urllib.request.Request(
        f"{API_BASE}/analytics/episodes/{urllib.parse.quote(str(episode_id))}?{qs}",
        headers={"x-api-key": api_key, "User-Agent": USER_AGENT},
    )
    with opener(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    return parse_downloads(json.loads(body))


def merge_downloads(catalog: list, results: dict, measured_at: str,
                    window_start: str) -> tuple[list, int]:
    """Return (new_catalog, updated_count). Pure — does no I/O.

    Records without a transistorEpisodeId, and ids absent from `results`, are
    passed through untouched rather than zeroed.
    """
    out, updated = [], 0
    for ep in catalog:
        ep = dict(ep)
        ep_id = str(ep.get("transistorEpisodeId") or "")
        if ep_id and ep_id in results:
            total, days = results[ep_id]
            ep["streams"] = total
            ep["streamsDays"] = days
            ep["streamsUpdatedAt"] = measured_at
            ep["streamsWindowStart"] = window_start
            updated += 1
        out.append(ep)
    return out, updated


def write_catalog(catalog: list, path: Path = PUBLISHED_JSON) -> None:
    """Atomic write — a crash mid-write must not truncate the catalog."""
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def report(catalog: list, top: int = 15) -> None:
    """Print the ranking this whole script exists to produce."""
    measured = [e for e in catalog if e.get("streamsUpdatedAt")]
    if not measured:
        print("\nNo measured episodes yet — run without --report-only first.")
        return
    total = sum(e.get("streams", 0) for e in measured)
    ranked = sorted(measured, key=lambda e: e.get("streams", 0), reverse=True)
    print(f"\n{'='*72}\nTOP {top} EPISODES BY DOWNLOADS  ({len(measured)} measured, {total:,} total)\n{'='*72}")
    for i, ep in enumerate(ranked[:top], 1):
        n = ep.get("streams", 0)
        share = (n / total * 100) if total else 0
        print(f"{i:3}. {n:>7,}  {share:>5.1f}%  {ep.get('category','?'):<18} {ep.get('title','')[:60]}")

    # The number that decides whether a restart is worth it: how concentrated is demand?
    cum, head = 0, 0
    for ep in ranked:
        cum += ep.get("streams", 0)
        head += 1
        if total and cum >= total * 0.8:
            break
    print(f"\n80% of all downloads come from {head} of {len(measured)} episodes "
          f"({head/len(measured)*100:.0f}% of the catalog).")
    zero = sum(1 for e in measured if e.get("streams", 0) == 0)
    print(f"Episodes with zero downloads: {zero}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="fetch and report, write nothing")
    ap.add_argument("--report-only", action="store_true", help="report from existing data, no network")
    ap.add_argument("--limit", type=int, help="only fetch the first N episodes (smoke test)")
    ap.add_argument("--since", default=DEFAULT_SINCE, help=f"window start, ISO yyyy-mm-dd (default {DEFAULT_SINCE})")
    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help="seconds between API calls")
    ap.add_argument("--top", type=int, default=15, help="how many episodes to rank in the report")
    args = ap.parse_args()

    catalog = load_catalog()
    print(f"Catalog: {len(catalog)} episodes in {PUBLISHED_JSON}")

    if args.report_only:
        report(catalog, args.top)
        return 0

    api_key = os.environ.get("TRANSISTOR_API_KEY", "").strip()
    if not api_key:
        sys.exit("ERROR: TRANSISTOR_API_KEY not set — export it before running "
                 "(Transistor dashboard -> Account -> Your API key)")

    try:
        start = fmt_date(args.since)
    except ValueError:
        sys.exit(f"ERROR: --since must be ISO yyyy-mm-dd, got {args.since!r}")
    end = fmt_date(datetime.date.today().isoformat())

    targets = [e for e in catalog if e.get("transistorEpisodeId")]
    skipped = len(catalog) - len(targets)
    if skipped:
        print(f"  {skipped} record(s) have no transistorEpisodeId — left untouched")
    if args.limit:
        targets = targets[:args.limit]
    print(f"Fetching {len(targets)} episodes, window {start} -> {end}\n")

    results, failures = {}, []
    for i, ep in enumerate(targets, 1):
        ep_id = str(ep["transistorEpisodeId"])
        title = (ep.get("title") or "")[:48]
        try:
            total, days = fetch_episode(ep_id, start, end, api_key)
            results[ep_id] = (total, days)
            print(f"  [{i}/{len(targets)}] {ep_id}  {total:>6,} downloads  {title}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200]
            failures.append((ep_id, f"HTTP {e.code}: {detail}"))
            print(f"  [{i}/{len(targets)}] {ep_id}  FAIL HTTP {e.code} — {title}")
        except Exception as e:  # shape errors included — never silently a zero
            failures.append((ep_id, str(e)))
            print(f"  [{i}/{len(targets)}] {ep_id}  FAIL {e} — {title}")
        if i < len(targets) and args.sleep:
            time.sleep(args.sleep)

    print(f"\nFetched {len(results)}/{len(targets)} episodes; {len(failures)} failed.")

    if args.dry_run:
        print("DRY RUN: published.json not written.")
    elif results:
        merged, updated = merge_downloads(
            catalog, results,
            measured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            window_start=args.since,
        )
        write_catalog(merged)
        print(f"Wrote {PUBLISHED_JSON} ({updated} episodes updated).")
        catalog = merged
    else:
        print("Nothing fetched — published.json not written.")

    report(catalog, args.top)

    if failures:
        print(f"\n{len(failures)} FAILURE(S) — not swallowed, fix and re-run:")
        for ep_id, err in failures[:20]:
            print(f"  {ep_id}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
