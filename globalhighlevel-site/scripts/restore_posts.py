#!/usr/bin/env python3
"""
restore_posts.py — restore pruned firehose posts from git history (full-931 restore sprint).

Doctrine (planning/recovery-2026-06 + Tier-D refutation, 2026-07):
Commit ea68058 pruned 931 zero-affiliate-click posts. The Tier-D refutation showed
the prune was wrong (D beat A on Bing; AI engines cited D most; only 23/931 were
true zeros), so we restore ALL of them from the parent of the prune commit.

Rules enforced here, in order, per slug:
  1. COLLISION (hard): if posts/<slug>.json already exists in the working tree,
     SKIP — an existing newer post always wins. Never overwrite. This is also
     what makes a second run idempotent (exit 0, everything skipped).
  2. Source of truth: `git show <PRUNE_COMMIT>^:globalhighlevel-site/posts/<slug>.json`.
     Missing in git -> recorded as an error in the report; the run continues.
  3. TOPIC STAMP: old 8-topic taxonomy is mapped onto the current 5-topic
     taxonomy (TOPIC_MAP below). A topic that is neither an old name nor one of
     the 5 current names FAILS LOUDLY: slug + topic printed, nonzero exit, run
     stopped. A hub-less post is never written silently.
  4. STAMPS: `updatedAt` = <deploy-date>T06:00:00.000000. `publishedAt` is NEVER
     touched. Everything else stays byte-faithful to the git version except
     `topic`, `updatedAt`, and the affiliate normalization below. Original key
     order preserved; new keys appended at the end. Serialized like the current
     posts/: json indent=2, ensure_ascii=False, trailing newline.
  5. AFFILIATE NORMALIZATION (eng-review D7): any gohighlevel.com href carrying
     `fp_ref=` is rewritten to the canonical bootcamp link (fp_ref forced to
     AFFILIATE_REF, path /highlevel-bootcamp, or /highlevel-bootcamp-es for
     language=="es", utm_source/utm_medium ensured, existing utm_campaign
     preserved, all other params dropped). gohighlevel.com hrefs WITHOUT fp_ref,
     and hrefs to known affiliate-network domains (firstpromoter, shareasale,
     partnerstack, bit.ly), are NOT modified — they are flagged in the report
     for human review. EXCEPTION (Bill-approved 2026-07-23): app.gohighlevel.com
     hrefs (incl. /signup) ARE rewritten to the canonical affiliate link — a
     direct product link pays nobody.
  6. --dry-run writes NOTHING (no posts, no report file); the report JSON is
     printed to stdout instead.

Usage:
  python3 scripts/restore_posts.py --slugs slugs.txt --deploy-date 2026-07-24
  python3 scripts/restore_posts.py --all --deploy-date 2026-07-24 [--dry-run]
                                   [--report PATH] [--topic-overrides FILE]

--topic-overrides takes a {slug: topic} JSON (the approved assignment sheet);
overrides win over the taxonomy mapping, unknown topics are fatal, and the
report counts consumed overrides (overrides_applied).

Report default: globalhighlevel-site/data/restore-report-<deploy-date>.json
(falls back to the repo root if data/ does not exist).

Run tests: python3 scripts/test_restore_posts.py
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

# --- locations (module-level so tests can repoint them) ----------------------
SITE_DIR = Path(__file__).resolve().parent.parent          # globalhighlevel-site/
REPO_ROOT = SITE_DIR.parent                                # worktree root
POSTS_DIR = SITE_DIR / "posts"
DATA_DIR = SITE_DIR / "data"
AUDIT_PATH = REPO_ROOT / "planning" / "recovery-2026-06" / "killed-audit" / "ghl_audit.json"

# --- git source of truth -----------------------------------------------------
PRUNE_COMMIT = "ea68058ec0fcca9588151d080e86d8ac68af4aaf"  # "prune: remove 931 ..."
GIT_POSTS_PREFIX = "globalhighlevel-site/posts/"

# --- affiliate canon (matches assemble_spoke.py AFFILIATE_DEFAULT) -----------
AFFILIATE_REF = "amplifi-technologies12"
BOOTCAMP_DOMAIN = "https://www.gohighlevel.com"
BOOTCAMP_PATH = "/highlevel-bootcamp"
BOOTCAMP_PATH_ES = "/highlevel-bootcamp-es"
UTM_SOURCE = "globalhighlevel"
UTM_MEDIUM = "blog"
FLAG_DOMAIN_PATTERNS = ("firstpromoter", "shareasale", "partnerstack", "bit.ly")

HREF_RE = re.compile(r'href=(["\'])(.*?)\1', re.IGNORECASE)

# --- topic taxonomy: old (8) -> new (5) --------------------------------------
TOPIC_MAP = {
    "Agency & Platform": "Agency, White-Label & SaaS",
    "AI & Automation": "AI Receptionist & Lead Capture",
    "CRM & Contacts": "CRM & Communication",
    "SMS & Messaging": "CRM & Communication",
    "Email & Deliverability": "CRM & Communication",
    "Payments & Commerce": "Payments & Pricing",
    "Analytics & Reporting": "Agency, White-Label & SaaS",
    "Phone & Voice": "AI Receptionist & Lead Capture",
}
NEW_TOPICS = {
    "AI Receptionist & Lead Capture",
    "CRM & Communication",
    "Sites, Funnels & Reputation",
    "Agency, White-Label & SaaS",
    "Payments & Pricing",
}

UPDATED_AT_TIME = "T06:00:00.000000"
DEPLOY_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TopicMappingError(Exception):
    """Raised when a post's topic maps to no current hub. Fails the whole run."""

    def __init__(self, slug, topic):
        self.slug = slug
        self.topic = topic
        super().__init__(f"unmappable topic for slug '{slug}': {topic!r}")


def read_post_from_git(slug):
    """Return the raw JSON text of a pruned post from git, or None if missing.

    The single point of git access — tests monkeypatch this function.
    """
    ref = f"{PRUNE_COMMIT}^:{GIT_POSTS_PREFIX}{slug}.json"
    proc = subprocess.run(
        ["git", "show", ref],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def load_audit():
    """Load the 931-row killed-post audit as {slug: row}."""
    rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    return {row["slug"]: row for row in rows}


def resolve_topic(slug, post, audit_row, overrides=None):
    """Map the old topic to the current 5-topic taxonomy. Unknown -> raise.

    A per-slug override (from the Bill-approved assignment sheet) beats the
    generic 8->5 map — the sheet is the human-reviewed source of truth, the map
    is only its default. Overrides must still name a current topic."""
    if overrides and slug in overrides:
        t = overrides[slug]
        if t in NEW_TOPICS:
            return t
        raise TopicMappingError(slug, t)
    topic = post.get("topic") or (audit_row or {}).get("topic")
    if topic in TOPIC_MAP:
        return TOPIC_MAP[topic]
    if topic in NEW_TOPICS:
        return topic
    raise TopicMappingError(slug, topic)


def normalize_affiliate_links(html, language):
    """Rewrite recognized gohighlevel.com fp_ref hrefs AND all app.gohighlevel.com
    hrefs (Bill-approved 2026-07-23) to the canonical bootcamp link; flag
    (untouched) other bare gohighlevel.com hrefs and affiliate-network domains.
    Returns (new_html, rewrite_count, flagged_hrefs)."""
    rewrites = 0
    flagged = []

    def _sub(match):
        nonlocal rewrites
        quote, href = match.group(1), match.group(2)
        # Firehose bodies HTML-escape the query separator (&amp;). parse_qsl on
        # the raw attribute value would read the next key as "amp;utm_campaign"
        # and silently DROP campaign tracking (codex 2026-07-23). Unescape for
        # parsing; re-escape the rewritten URL iff the original was escaped.
        was_escaped = "&amp;" in href
        href_plain = href.replace("&amp;", "&")
        parts = urlsplit(href_plain)
        host = parts.netloc.lower().split(":")[0]
        if host == "app.gohighlevel.com":
            # Direct product signup/login links pay NOBODY. Bill-approved
            # 2026-07-23: rewrite to the canonical affiliate link (same treatment
            # for /signup and bare app links — both are lost commissions).
            path = BOOTCAMP_PATH_ES if language == "es" else BOOTCAMP_PATH
            canonical = f"{BOOTCAMP_DOMAIN}{path}?" + urlencode([
                ("fp_ref", AFFILIATE_REF), ("utm_source", UTM_SOURCE), ("utm_medium", UTM_MEDIUM)])
            rewrites += 1
            if was_escaped:
                canonical = canonical.replace("&", "&amp;")
            return f"href={quote}{canonical}{quote}"
        if host == "gohighlevel.com" or host.endswith(".gohighlevel.com"):
            params = dict(parse_qsl(parts.query, keep_blank_values=True))
            if "fp_ref" not in params:
                flagged.append(href_plain)
                return match.group(0)
            path = BOOTCAMP_PATH_ES if language == "es" else BOOTCAMP_PATH
            pairs = [
                ("fp_ref", AFFILIATE_REF),
                ("utm_source", UTM_SOURCE),
                ("utm_medium", UTM_MEDIUM),
            ]
            if "utm_campaign" in params:
                pairs.append(("utm_campaign", params["utm_campaign"]))
            canonical = f"{BOOTCAMP_DOMAIN}{path}?{urlencode(pairs)}"
            if canonical != href_plain:
                rewrites += 1
            if was_escaped:
                canonical = canonical.replace("&", "&amp;")
            return f"href={quote}{canonical}{quote}"
        if any(pat in host for pat in FLAG_DOMAIN_PATTERNS):
            flagged.append(href_plain)
        return match.group(0)

    return HREF_RE.sub(_sub, html), rewrites, flagged


def restore_post(raw_json, slug, deploy_date, audit_row, overrides=None):
    """Transform one pruned post's raw JSON into restore-ready serialized text.

    Returns (serialized_text, rewrite_count, flagged_hrefs).
    Raises TopicMappingError on an unmappable topic.
    """
    post = json.loads(raw_json)  # dict preserves the file's key order
    new_topic = resolve_topic(slug, post, audit_row, overrides)

    html = post.get("html_content", "")
    new_html, rewrites, flagged = normalize_affiliate_links(html, post.get("language"))
    if "html_content" in post:
        post["html_content"] = new_html

    # dict insertion order: an existing key keeps its original position, a new
    # key ("topic" absent from old JSON, "updatedAt" always) appends at the end
    post["topic"] = new_topic
    post["updatedAt"] = f"{deploy_date}{UPDATED_AT_TIME}"

    text = json.dumps(post, indent=2, ensure_ascii=False) + "\n"
    return text, rewrites, flagged


def default_report_path(deploy_date):
    name = f"restore-report-{deploy_date}.json"
    return (DATA_DIR / name) if DATA_DIR.is_dir() else (REPO_ROOT / name)


def run_restore(slugs, deploy_date, dry_run=False, audit=None, overrides=None):
    """Restore each slug per the doctrine above. Returns the report dict.

    Raises TopicMappingError (fail-loud, stop-the-run) on an unmappable topic.
    """
    audit = audit if audit is not None else load_audit()
    report = {
        "deploy_date": deploy_date,
        "restored": [],
        "skipped_collision": [],
        "errors": [],
        "flagged": [],
        "affiliate_rewrites": {},
        "overrides_applied": 0,
    }

    for slug in slugs:
        # Slugs come from a file/audit JSON and become both a git ref and a
        # filesystem path — reject path separators and traversal so a stray
        # "../" or "/" can never address outside posts/ (hardening, review
        # 2026-07-23). Blocklist, not ASCII allowlist: 2 of the 931 real slugs
        # carry accented characters (prospección-..., ...-membresía-...).
        if (not slug or ".." in slug
                or any(c in slug for c in "/\\") or slug != slug.strip()):
            report["errors"].append({"slug": slug, "error": "invalid slug (path separator/traversal)"})
            continue
        dest = POSTS_DIR / f"{slug}.json"
        if dest.exists():
            report["skipped_collision"].append(slug)
            continue
        raw = read_post_from_git(slug)
        if raw is None:
            report["errors"].append({"slug": slug, "error": "not found in git at prune parent"})
            continue
        try:
            text, rewrites, flagged = restore_post(raw, slug, deploy_date, audit.get(slug), overrides)
            if overrides and slug in overrides:
                report["overrides_applied"] += 1
        except TopicMappingError as exc:
            # fail loudly: no file written for this slug, run stops (caller exits
            # nonzero). Attach the partial report — files restored BEFORE the bad
            # slug are already on disk and their flagged-href data would otherwise
            # be lost with no manifest (red-team 2026-07-23).
            report["aborted_at"] = {"slug": slug, "topic": exc.topic}
            exc.report = report
            raise
        except (json.JSONDecodeError, ValueError) as exc:
            report["errors"].append({"slug": slug, "error": f"unparseable git blob (bad JSON or URL): {exc}"})
            continue
        if not dry_run:
            # Atomic write: a crash mid-write would leave truncated JSON that the
            # collision rule then protects forever and build.load_posts silently
            # drops — permanent invisible post loss (adversarial review 2026-07-23).
            tmp = dest.with_suffix(".json.tmp")
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, dest)
        report["restored"].append(slug)
        if rewrites:
            report["affiliate_rewrites"][slug] = rewrites
        for href in flagged:
            report["flagged"].append({"slug": slug, "href": href})

    report["counts"] = {
        "requested": len(slugs),
        "restored": len(report["restored"]),
        "skipped_collision": len(report["skipped_collision"]),
        "errors": len(report["errors"]),
        "flagged": len(report["flagged"]),
        "affiliate_rewrites": sum(report["affiliate_rewrites"].values()),
    }
    return report


def print_summary(report, dry_run):
    c = report["counts"]
    mode = "DRY-RUN (nothing written)" if dry_run else "WRITE"
    print(f"restore_posts.py — {mode} — deploy date {report['deploy_date']}")
    print(f"  requested:          {c['requested']}")
    print(f"  restored:           {c['restored']}")
    print(f"  skipped (collision):{c['skipped_collision']}")
    print(f"  errors:             {c['errors']}")
    print(f"  affiliate rewrites: {c['affiliate_rewrites']} (across {len(report['affiliate_rewrites'])} posts)")
    print(f"  flagged hrefs:      {c['flagged']}")
    for err in report["errors"]:
        print(f"  ERROR {err['slug']}: {err['error']}")
    for f in report["flagged"][:20]:
        print(f"  FLAG  {f['slug']}: {f['href']}")
    if len(report["flagged"]) > 20:
        print(f"  ... and {len(report['flagged']) - 20} more flagged (see report)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Restore pruned posts from git history.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--slugs", metavar="FILE", help="file with one slug per line")
    src.add_argument("--all", action="store_true", help="every slug in ghl_audit.json")
    ap.add_argument("--deploy-date", required=True, metavar="YYYY-MM-DD")
    ap.add_argument("--dry-run", action="store_true", help="write nothing; print report to stdout")
    ap.add_argument("--report", metavar="PATH", help="report path (default: data/restore-report-<date>.json)")
    ap.add_argument("--topic-overrides", metavar="FILE",
                    help="JSON {slug: topic} from the approved assignment sheet; beats the 8->5 map")
    args = ap.parse_args(argv)

    if not DEPLOY_DATE_RE.match(args.deploy_date):
        ap.error(f"--deploy-date must be YYYY-MM-DD, got {args.deploy_date!r}")

    # Preflight: probe the prune commit's PARENT — that's the tree every slug is
    # read from. A shallow clone can hold the prune commit but not its parent,
    # which would pass a prune-commit-only probe and then error on every slug
    # (adversarial review + codex P2, 2026-07-23).
    probe = subprocess.run(["git", "cat-file", "-e", f"{PRUNE_COMMIT}^^{{commit}}"],
                           cwd=REPO_ROOT, capture_output=True)
    if probe.returncode != 0:
        print(f"FATAL: parent of prune commit {PRUNE_COMMIT[:12]} not reachable in "
              f"this clone (shallow checkout?) — cannot restore.", file=sys.stderr)
        return 2

    audit = load_audit()
    if args.all:
        slugs = list(audit.keys())
    else:
        lines = Path(args.slugs).read_text(encoding="utf-8").splitlines()
        slugs = [ln.strip() for ln in lines if ln.strip()]

    overrides = None
    if args.topic_overrides:
        try:
            overrides = json.loads(Path(args.topic_overrides).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FATAL: cannot read topic overrides {args.topic_overrides}: {exc}", file=sys.stderr)
            return 2
        bad = [t for t in set(overrides.values()) if t not in NEW_TOPICS]
        if bad:
            print(f"FATAL: override file names unknown topic(s): {bad}", file=sys.stderr)
            return 2
        print(f"topic overrides loaded: {len(overrides)} slugs")

    try:
        report = run_restore(slugs, args.deploy_date, dry_run=args.dry_run, audit=audit,
                             overrides=overrides)
    except TopicMappingError as exc:
        print(f"FATAL: slug {exc.slug!r} has unmappable topic {exc.topic!r} — "
              f"no current hub for it; nothing written for that slug, run stopped.",
              file=sys.stderr)
        partial = getattr(exc, "report", None)
        if partial is not None and not args.dry_run:
            report_path = Path(args.report) if args.report else default_report_path(args.deploy_date)
            report_path.write_text(json.dumps(partial, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
            print(f"partial report written (aborted run): {report_path}", file=sys.stderr)
        return 2

    print_summary(report, args.dry_run)
    if args.dry_run:
        print("\n--- report (dry-run, not written) ---")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        report_path = Path(args.report) if args.report else default_report_path(args.deploy_date)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
        print(f"\nreport written: {report_path}")
    if report["errors"]:
        # A restore with errors must not chain silently into build/deploy — a
        # shallow clone errors on EVERY slug and would otherwise exit 0 having
        # restored nothing (adversarial review 2026-07-23).
        print(f"EXIT 1: {len(report['errors'])} slug(s) errored — see report", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
