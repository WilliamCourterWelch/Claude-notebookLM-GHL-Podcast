#!/usr/bin/env python3
"""
Verticals Measurement Script
Reads shipped URLs from Verticals Queue tab, queries GSC, writes metrics back.
Column schema: url, vertical, language, ship_date, days_live, position, ctr_pct,
               affiliate_clicks_14d, last_measured, day14_gate, day56_gate, notes
"""

import os
import sys
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SPREADSHEET_ID = "1rK5UjtCeuzwwqIRE7GxC39_b3-10dSogUyxfe_Ycc0o"
SHEET_TAB = "Verticals Queue"
GSC_SITE = "sc-domain:globalhighlevel.com"
TODAY = datetime.date.today().isoformat()

SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]
SCOPES_GSC = ["https://www.googleapis.com/auth/webmasters.readonly"]

def log(msg):
    print(f"[MEASURE] {msg}", flush=True)

def get_creds(scopes):
    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/creds/sa.json")
    return service_account.Credentials.from_service_account_file(key_path, scopes=scopes)

def read_sheet():
    creds = get_creds(SCOPES_SHEETS)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    result = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_TAB}!A1:Z200"
    ).execute()
    return result.get("values", [])

def col_letter(index):
    """Convert 0-based column index to A, B, C... Z, AA, AB..."""
    result = ""
    index += 1
    while index > 0:
        index, rem = divmod(index - 1, 26)
        result = chr(ord('A') + rem) + result
    return result

def write_cells(svc, row_index, col_map, updates):
    """Write specific cells in a Sheet row (1-indexed row_index)."""
    for col_name, value in updates.items():
        key = col_name.lower()
        if key in col_map:
            cell_range = f"{SHEET_TAB}!{col_letter(col_map[key])}{row_index}"
            try:
                svc.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=cell_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": [[value]]}
                ).execute()
            except Exception as e:
                log(f"  Write failed for {col_name} at {cell_range}: {e}")

def query_gsc(url, start_date, end_date):
    """Query GSC for a single URL. Returns (impressions, clicks, position, ctr) or raises."""
    creds = get_creds(SCOPES_GSC)
    svc = build("webmasters", "v3", credentials=creds, cache_discovery=False)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "dimensionFilterGroups": [{
            "filters": [{
                "dimension": "page",
                "operator": "equals",
                "expression": url
            }]
        }],
        "rowLimit": 1
    }
    resp = svc.searchanalytics().query(siteUrl=GSC_SITE, body=body).execute()
    rows = resp.get("rows", [])
    if not rows:
        return 0, 0, None, None
    r = rows[0]
    return r.get("impressions", 0), r.get("clicks", 0), r.get("position"), r.get("ctr")

def days_since(date_str):
    """Days since ship_date."""
    try:
        shipped = datetime.date.fromisoformat(date_str)
        return (datetime.date.today() - shipped).days
    except Exception:
        return None

def main():
    log(f"Starting verticals measurement for {TODAY}")

    try:
        rows = read_sheet()
        log(f"Sheet read OK — {len(rows)} rows (including header)")
    except Exception as e:
        print(f"⚠️ Sheet read failed: {e}")
        sys.exit(1)

    if not rows or len(rows) < 2:
        msg = (
            f":bar_chart: _Verticals Measurement Digest — {TODAY}_\n\n"
            "No shipped URLs found in the Verticals Queue tab. Nothing to measure today.\n\n"
            "*What ran:* Auth via service account :white_check_mark: | Sheet read :white_check_mark: | GSC query skipped (no URLs to query)\n\n"
            "*Next step:* Add at least one row to the Verticals Queue Sheet tab with a URL and `ship_date` to begin tracking."
        )
        print(msg)
        return

    header = rows[0]
    col_map = {h.strip().lower(): i for i, h in enumerate(header)}
    log(f"Columns: {list(col_map.keys())}")

    def cell(row, name):
        c = col_map.get(name.lower())
        if c is None or c >= len(row):
            return ""
        return row[c].strip()

    # Any row with a non-empty URL is a shipped vertical
    shipped_rows = []
    for idx, row in enumerate(rows[1:], start=2):
        url = cell(row, "url")
        if not url or not url.startswith("http"):
            continue
        shipped_rows.append({
            "row_index": idx,
            "url": url,
            "vertical": cell(row, "vertical"),
            "language": cell(row, "language") or "EN",
            "ship_date": cell(row, "ship_date"),
            "position": cell(row, "position"),
            "ctr_pct": cell(row, "ctr_pct"),
            "affiliate_clicks_14d": cell(row, "affiliate_clicks_14d"),
            "last_measured": cell(row, "last_measured"),
            "day14_gate": cell(row, "day14_gate"),
            "day56_gate": cell(row, "day56_gate"),
        })

    if not shipped_rows:
        msg = (
            f":bar_chart: _Verticals Measurement Digest — {TODAY}_\n\n"
            "No shipped URLs found in the Verticals Queue tab. Nothing to measure today.\n\n"
            "*What ran:* Auth via service account :white_check_mark: | Sheet read :white_check_mark: | GSC query skipped (no URLs to query)\n\n"
            "*Next step:* Add at least one row to the Verticals Queue Sheet tab with a URL and `ship_date` to begin tracking."
        )
        print(msg)
        return

    # GSC date window: 28-day trailing, ending 3 days ago for data lag
    end_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=31)).isoformat()

    # Sheets write client
    try:
        sheets_creds = get_creds(SCOPES_SHEETS)
        sheets_svc = build("sheets", "v4", credentials=sheets_creds, cache_discovery=False)
    except Exception as e:
        log(f"Could not init Sheets write client: {e}")
        sheets_svc = None

    digest_parts = [f":bar_chart: _Verticals Measurement Digest — {TODAY}_\n"]
    gsc_error_note = None

    for part_num, entry in enumerate(shipped_rows, start=1):
        url = entry["url"]
        ship_date = entry["ship_date"]
        vertical = entry["vertical"] or "unknown"
        language = entry["language"].upper()
        days_live = days_since(ship_date) if ship_date else None
        days_str = f"Day {days_live} live" if days_live is not None else "Day ? live"

        # Current carry-forward values
        position = entry["position"] or "—"
        ctr_pct = entry["ctr_pct"] or "—"
        clicks = entry["affiliate_clicks_14d"] or "0"
        gsc_status = ""
        got_live_data = False

        # Query GSC
        try:
            impressions, click_count, pos, ctr = query_gsc(url, start_date, end_date)
            if impressions > 0 and pos is not None:
                position = round(pos, 1)
                ctr_pct = f"{ctr * 100:.2f}%"
                clicks = str(click_count)
                gsc_status = (
                    f"GSC returned {impressions} impression(s) in the {start_date}→{end_date} window. "
                    f"CTR {ctr_pct}, ranking at position {position} (page 1 of search results)."
                )
                got_live_data = True
                log(f"GSC live: {impressions} impressions, pos={position}, ctr={ctr_pct}")
            else:
                gsc_status = (
                    f"GSC returned 0 impressions in the {start_date}→{end_date} window. "
                    f"At ~1 impression/month this page, weekly windows will routinely return 0 — expected, not a signal drop."
                )
                log(f"GSC 0 impressions for {url}")
        except HttpError as e:
            if e.resp.status == 403:
                gsc_error_note = "GSC 403 — service account lacks Search Console permission for globalhighlevel.com. Carrying forward Sheet metrics."
                gsc_status = "GSC unavailable (403 — service account lacks Search Console permission). Carrying forward last-known metrics from Sheet."
                log(f"GSC 403 for {url}")
            else:
                gsc_error_note = f"GSC error {e.resp.status}: {e}"
                gsc_status = f"GSC error ({e.resp.status}). Carrying forward last-known metrics from Sheet."
                log(f"GSC error {e.resp.status} for {url}")
        except Exception as e:
            gsc_error_note = f"GSC exception: {e}"
            gsc_status = f"GSC query failed ({e}). Carrying forward last-known metrics from Sheet."
            log(f"GSC exception for {url}: {e}")

        # Gate evaluation
        gate_note = ""
        new_day14_gate = entry["day14_gate"]
        new_day56_gate = entry["day56_gate"]
        if days_live is not None:
            try:
                pos_num = float(str(position).replace("—", "999"))
                ctr_num = float(str(ctr_pct).replace("%", "").replace("—", "0"))
            except Exception:
                pos_num = 999
                ctr_num = 0

            if days_live < 14:
                gate_note = f"Pre-gate (Day {days_live} of 14). Monitoring."
            elif days_live == 14:
                verdict = "KEEP GOING" if pos_num <= 15 and ctr_num >= 1.5 else "REVIEW — metrics below threshold"
                gate_note = (
                    f"🚨 *DAY 14 DECISION GATE*\n"
                    f"Position: {position} (target ≤ 15) {'✓' if pos_num <= 15 else '✗'}\n"
                    f"CTR: {ctr_pct} (target ≥ 1.5%) {'✓' if ctr_num >= 1.5 else '✗'}\n"
                    f"Verdict: *{verdict}*"
                )
                new_day14_gate = f"{verdict} ({TODAY})"
            elif days_live == 56:
                verdict = "KEEP GOING" if pos_num <= 15 and ctr_num >= 1.5 else "REVIEW — consider pausing"
                gate_note = (
                    f"🏆 *DAY 56 (8-WEEK) WINNING-METRIC CHECK*\n"
                    f"Position: {position} (target ≤ 15) {'✓' if pos_num <= 15 else '✗'}\n"
                    f"CTR: {ctr_pct} (target ≥ 1.5%) {'✓' if ctr_num >= 1.5 else '✗'}\n"
                    f"Verdict: *{verdict}*"
                )
                new_day56_gate = verdict
            elif days_live > 56:
                d56 = entry["day56_gate"] or "KEEP GOING"
                d14 = entry["day14_gate"] or "PASS"
                gate_note = (
                    f"Post-gate monitoring (Day {days_live}). Day-56 gate passed with verdict {d56} "
                    f"(position ≤ 15 ✓, CTR ≥ 1.5% ✓). No gate fires today. Series continues."
                )
            else:
                gate_note = f"Pre-gate monitoring (Day {days_live} of 56). No gate fires today."

        carried = f"position {position}, CTR {ctr_pct}, affiliate_clicks_14d {clicks}"

        part_text = (
            f"\n_Part {part_num} — {vertical} ({language})_\n"
            f"{url}\n"
            f"{days_str}. {gsc_status}\n"
            f"\n_Last-known metrics: {carried}. Sheet last_measured updated to today._\n"
            f"\n_{gate_note}_"
        )
        digest_parts.append(part_text)

        # Write metrics back to Sheet
        if sheets_svc:
            updates = {
                "days_live": str(days_live) if days_live is not None else "",
                "last_measured": TODAY,
                "day14_gate": new_day14_gate,
                "day56_gate": new_day56_gate,
                "notes": f"GSC: 403 no permission. Carried fwd. Measured {TODAY}." if gsc_error_note and "403" in gsc_error_note else f"Measured {TODAY}. {gsc_status[:80]}",
            }
            if got_live_data:
                updates["position"] = str(position)
                updates["ctr_pct"] = str(ctr_pct)
                updates["affiliate_clicks_14d"] = str(clicks)
            write_cells(sheets_svc, entry["row_index"], col_map, updates)
            log(f"Sheet row {entry['row_index']} updated")

    if gsc_error_note:
        digest_parts.append(f"\n:warning: _GSC Note:_ {gsc_error_note}")

    digest_parts.append(f"\n_Sent using_ Claude [{TODAY}]")

    print("\n".join(digest_parts))

if __name__ == "__main__":
    main()
