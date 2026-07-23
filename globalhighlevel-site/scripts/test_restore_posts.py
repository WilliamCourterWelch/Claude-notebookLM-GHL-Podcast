#!/usr/bin/env python3
"""Tests for restore_posts.py (topic mapping, collision skip, stamps, affiliate
normalization, idempotency).

Run: python3 scripts/test_restore_posts.py
Exits 0 if all pass, 1 otherwise. No network, no real git: read_post_from_git is
monkeypatched with an in-memory blob store, and POSTS_DIR is repointed at a
temp directory per test.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/
import restore_posts as rp

FAILED = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        FAILED.append(name)


def make_post(**over):
    post = {
        "title": "T",
        "slug": "s1",
        "description": "d",
        "html_content": "<p>hello</p>",
        "category": "Guides",
        "tags": ["a"],
        "language": "en",
        "publishedAt": "2026-04-04T02:48:32.720243",
        "author": "William Welch",
        "topic": "AI & Automation",
    }
    post.update(over)
    return post


class FakeGit:
    """Monkeypatch target: slug -> raw JSON text (or missing)."""

    def __init__(self, posts):
        self.blobs = {p["slug"]: json.dumps(p, indent=2, ensure_ascii=False) + "\n"
                      for p in posts}

    def __call__(self, slug):
        return self.blobs.get(slug)


def with_env(posts, run):
    """Run `run(tmp_posts_dir)` with fake git + temp POSTS_DIR; restore after."""
    saved_git, saved_dir = rp.read_post_from_git, rp.POSTS_DIR
    with tempfile.TemporaryDirectory() as tmp:
        rp.read_post_from_git = FakeGit(posts)
        rp.POSTS_DIR = Path(tmp)
        try:
            return run(Path(tmp))
        finally:
            rp.read_post_from_git, rp.POSTS_DIR = saved_git, saved_dir


def test_topic_mapping():
    expected = {
        "Agency & Platform": "Agency, White-Label & SaaS",
        "AI & Automation": "AI Receptionist & Lead Capture",
        "CRM & Contacts": "CRM & Communication",
        "SMS & Messaging": "CRM & Communication",
        "Email & Deliverability": "CRM & Communication",
        "Payments & Commerce": "Payments & Pricing",
        "Analytics & Reporting": "Agency, White-Label & SaaS",
        "Phone & Voice": "AI Receptionist & Lead Capture",
    }
    for old, new in expected.items():
        got = rp.resolve_topic("s", {"topic": old}, None)
        check(f"map {old!r} -> {new!r}", got == new)
    for new in sorted(rp.NEW_TOPICS):
        check(f"new-taxonomy topic kept: {new!r}",
              rp.resolve_topic("s", {"topic": new}, None) == new)
    # falls back to the audit row when the post JSON has no topic
    check("audit-row topic fallback",
          rp.resolve_topic("s", {}, {"topic": "Phone & Voice"})
          == "AI Receptionist & Lead Capture")
    # unknown / missing topic raises (main() turns this into a nonzero exit)
    for bad in ("Gardening", None):
        try:
            rp.resolve_topic("bad-slug", {"topic": bad}, None)
            check(f"unknown topic {bad!r} raises", False)
        except rp.TopicMappingError as exc:
            check(f"unknown topic {bad!r} raises", exc.slug == "bad-slug")

    def run(tmp):
        try:
            rp.run_restore(["s1"], "2026-07-24", audit={})
            return False
        except rp.TopicMappingError:
            return not (tmp / "s1.json").exists()
    check("run stops on unmappable topic, file not written",
          with_env([make_post(topic="Nonsense Topic")], run))


def test_collision_skip():
    def run(tmp):
        existing = (tmp / "s1.json")
        existing.write_text('{"slug": "s1", "note": "newer post wins"}\n')
        report = rp.run_restore(["s1"], "2026-07-24", audit={})
        return existing.read_text(), report
    content, report = with_env([make_post()], run)
    check("existing file untouched", content == '{"slug": "s1", "note": "newer post wins"}\n')
    check("slug reported as skipped_collision", report["skipped_collision"] == ["s1"])
    check("nothing reported restored", report["restored"] == [])


def test_stamps():
    def run(tmp):
        rp.run_restore(["s1"], "2026-07-24", audit={})
        return json.loads((tmp / "s1.json").read_text())
    out = with_env([make_post()], run)
    check("updatedAt stamped", out["updatedAt"] == "2026-07-24T06:00:00.000000")
    check("publishedAt unchanged", out["publishedAt"] == "2026-04-04T02:48:32.720243")
    check("updatedAt appended last (key order preserved)",
          list(out.keys())[-1] == "updatedAt")
    check("topic keeps its original position",
          list(out.keys()).index("topic") == list(make_post().keys()).index("topic"))


def test_affiliate():
    html = (
        '<a href="https://www.gohighlevel.com/some-old-page?fp_ref=oldref&utm_campaign=spring">go</a> '
        '<a href="https://www.gohighlevel.com/pricing">bare</a> '
        '<a href="https://bit.ly/3xyz">short</a> '
        '<a href="https://globalhighlevel.com/es/trial/">own site</a>'
    )
    new_html, rewrites, flagged = rp.normalize_affiliate_links(html, "en")
    canonical = ("https://www.gohighlevel.com/highlevel-bootcamp?"
                 "fp_ref=amplifi-technologies12&utm_source=globalhighlevel"
                 "&utm_medium=blog&utm_campaign=spring")
    check("fp_ref href rewritten to canonical (campaign preserved)",
          f'href="{canonical}"' in new_html)
    check("one rewrite counted", rewrites == 1)
    check("bare gohighlevel href untouched",
          'href="https://www.gohighlevel.com/pricing"' in new_html)
    check("bare gohighlevel + bit.ly flagged",
          flagged == ["https://www.gohighlevel.com/pricing", "https://bit.ly/3xyz"])
    check("own-site href not flagged, untouched",
          'href="https://globalhighlevel.com/es/trial/"' in new_html)

    es_html, es_rewrites, _ = rp.normalize_affiliate_links(
        '<a href="https://www.gohighlevel.com/x?fp_ref=oldref">es</a>', "es")
    check("es language gets -es bootcamp path",
          "/highlevel-bootcamp-es?fp_ref=amplifi-technologies12" in es_html)
    check("es rewrite counted", es_rewrites == 1)

    # already-canonical link: not counted as a rewrite, not flagged
    same_html, same_rewrites, same_flagged = rp.normalize_affiliate_links(
        f'<a href="{rp.BOOTCAMP_DOMAIN}{rp.BOOTCAMP_PATH}?fp_ref={rp.AFFILIATE_REF}'
        f'&utm_source={rp.UTM_SOURCE}&utm_medium={rp.UTM_MEDIUM}">ok</a>', "en")
    check("already-canonical href: zero rewrites, zero flags",
          same_rewrites == 0 and same_flagged == [])

    def run(tmp):
        rp.run_restore(["s1"], "2026-07-24", audit={})
        report = rp.run_restore(["s2"], "2026-07-24", audit={})
        return report
    posts = [
        make_post(slug="s1"),
        make_post(slug="s2", html_content=html),
    ]
    report = with_env(posts, run)
    check("report counts rewrites per post", report["affiliate_rewrites"] == {"s2": 1})
    check("report flags carry slug + href",
          {"slug": "s2", "href": "https://bit.ly/3xyz"} in report["flagged"])


def test_idempotency():
    def run(tmp):
        first = rp.run_restore(["s1"], "2026-07-24", audit={})
        stamped = (tmp / "s1.json").read_text()
        second = rp.run_restore(["s1"], "2026-07-24", audit={})
        return first, second, stamped, (tmp / "s1.json").read_text()
    first, second, stamped, after = with_env([make_post()], run)
    check("first run restores", first["restored"] == ["s1"])
    check("second run skips (collision rule)", second["skipped_collision"] == ["s1"]
          and second["restored"] == [])
    check("second run reports no errors (would exit 0)", second["errors"] == [])
    check("file unchanged by second run", stamped == after)


def test_dry_run_and_errors():
    def run(tmp):
        report = rp.run_restore(["s1", "not-in-git"], "2026-07-24",
                                dry_run=True, audit={})
        return report, list(Path(tmp).iterdir())
    report, leftover = with_env([make_post()], run)
    check("dry-run writes nothing", leftover == [])
    check("dry-run still reports restorable slug", report["restored"] == ["s1"])
    check("missing-in-git recorded as error, run continued",
          len(report["errors"]) == 1 and report["errors"][0]["slug"] == "not-in-git")
    check("counts summary present",
          report["counts"]["restored"] == 1 and report["counts"]["errors"] == 1)


def main():
    print("test_restore_posts.py")
    for t in (test_topic_mapping, test_collision_skip, test_stamps,
              test_affiliate, test_idempotency, test_dry_run_and_errors):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
