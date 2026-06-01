"""
money-queries.py
Find buyer-intent ("money") search queries from GSC: demand we already get
impressions for but aren't cashing in. Bottom-funnel terms = people deciding
to buy = where the affiliate dollars are.

Run: venv/bin/python3 scripts/money-queries.py
Read-only (webmasters.readonly). Refresh-only auth (no interactive prompt).
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
GSC_TOKEN_FILE = BASE_DIR / "token-gsc.json"
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GSC_SITE_URL = "sc-domain:globalhighlevel.com"
TRIAL_PAGE = "https://globalhighlevel.com/blog/gohighlevel-free-trial-30-days-extended/"

# Buyer / money intent markers (bottom-funnel)
MONEY_TERMS = [
    "price", "pricing", "cost", "how much", "worth", " vs ", "versus",
    "alternative", "review", "free trial", "trial", "discount", "coupon",
    "promo", "deal", "best ", "cheap", "plan", "plans", "is gohighlevel",
    "should i", "compare",
]


def get_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(GSC_TOKEN_FILE), GSC_SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            GSC_TOKEN_FILE.write_text(creds.to_json())
        else:
            raise SystemExit("Token invalid and no refresh_token. Re-auth needed (run gsc-diagnose.py once interactively).")
    return build("searchconsole", "v1", credentials=creds)


def q(service, body):
    return service.searchanalytics().query(siteUrl=GSC_SITE_URL, body=body).execute()


def is_money(query_text):
    t = " " + query_text.lower() + " "
    return any(term in t for term in MONEY_TERMS)


def main():
    service = get_service()
    end = datetime.now().date()
    start = end - timedelta(days=90)
    print(f"\nGSC {GSC_SITE_URL} | {start} -> {end} (last 90d, ~2-3d lag)\n")

    # All queries
    res = q(service, {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["query"],
        "rowLimit": 1000,
    })
    rows = res.get("rows", [])
    money = [r for r in rows if is_money(r["keys"][0])]
    money.sort(key=lambda r: r.get("impressions", 0), reverse=True)

    print("=" * 92)
    print("BUYER-INTENT QUERIES (you already get impressions; ranked by demand)")
    print("=" * 92)
    print(f"{'QUERY':<52}{'IMPR':>7}{'CLICKS':>7}{'CTR%':>7}{'POS':>7}")
    print("-" * 92)
    for r in money[:40]:
        kw = r["keys"][0][:50]
        i = r.get("impressions", 0)
        c = r.get("clicks", 0)
        ctr = round(r.get("ctr", 0) * 100, 1)
        pos = round(r.get("position", 0), 1)
        print(f"{kw:<52}{i:>7}{c:>7}{ctr:>7}{pos:>7}")
    print(f"\n{len(money)} buyer-intent queries total (of {len(rows)} all queries).")

    # Queries that bring people to the proven winner (the trial page)
    res2 = q(service, {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["query"],
        "dimensionFilterGroups": [{
            "filters": [{"dimension": "page", "operator": "equals", "expression": TRIAL_PAGE}]
        }],
        "rowLimit": 50,
    })
    wr = res2.get("rows", [])
    wr.sort(key=lambda r: r.get("impressions", 0), reverse=True)
    print("\n" + "=" * 92)
    print("QUERIES HITTING THE PROVEN WINNER (trial page) -- the shape of a money query")
    print("=" * 92)
    print(f"{'QUERY':<52}{'IMPR':>7}{'CLICKS':>7}{'CTR%':>7}{'POS':>7}")
    print("-" * 92)
    for r in wr[:25]:
        kw = r["keys"][0][:50]
        print(f"{kw:<52}{r.get('impressions',0):>7}{r.get('clicks',0):>7}{round(r.get('ctr',0)*100,1):>7}{round(r.get('position',0),1):>7}")


if __name__ == "__main__":
    main()
