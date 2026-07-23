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


def test_affiliate_escaped_amp():
    # Firehose bodies HTML-escape the query separator. parse_qsl on the raw value
    # would read "amp;utm_campaign" and drop campaign tracking (codex 2026-07-23).
    html = ('<a href="https://www.gohighlevel.com/x?fp_ref=old&amp;'
            'utm_campaign=spring">go</a>')
    new_html, rewrites, flagged = rp.normalize_affiliate_links(html, "en")
    check("escaped &amp; href: utm_campaign survives the rewrite",
          "utm_campaign=spring" in new_html)
    check("escaped &amp; href: output re-escaped with &amp;",
          "&amp;" in new_html and "?fp_ref=amplifi-technologies12&amp;" in new_html)
    check("escaped &amp; href: raw '&' never emitted into the attribute",
          "&utm_" not in new_html)
    check("escaped &amp; href: counted as one rewrite", rewrites == 1)
    # an escaped no-fp_ref gohighlevel href is flagged in UNescaped form
    html2 = '<a href="https://www.gohighlevel.com/pricing?a=1&amp;b=2">bare</a>'
    new_html2, rewrites2, flagged2 = rp.normalize_affiliate_links(html2, "en")
    check("escaped no-fp_ref href untouched", new_html2 == html2 and rewrites2 == 0)
    check("escaped no-fp_ref href flagged with UNescaped form",
          flagged2 == ["https://www.gohighlevel.com/pricing?a=1&b=2"])


def test_slug_blocklist():
    bad_slugs = ["../evil", "a/b", "", "  pad "]

    def run(tmp):
        report = rp.run_restore(bad_slugs + ["ok-slug"], "2026-07-24", audit={})
        return report, sorted(x.name for x in tmp.iterdir())
    report, files = with_env([make_post(slug="ok-slug")], run)
    check("4 invalid slugs recorded as errors",
          len(report["errors"]) == 4
          and all("invalid slug" in e["error"] for e in report["errors"]))
    check("only ok-slug restored", report["restored"] == ["ok-slug"])
    check("no stray files written", files == ["ok-slug.json"])

    # blocklist, not ASCII allowlist: real restore slugs carry accented chars
    def run_accent(tmp):
        return rp.run_restore(["prospección-x"], "2026-07-24", audit={})
    report2 = with_env([make_post(slug="prospección-x")], run_accent)
    check("accented slug NOT rejected (restores fine)",
          report2["restored"] == ["prospección-x"] and report2["errors"] == [])


class FakeGitPreflight:
    """Stand-in for restore_posts' subprocess module: `git cat-file -e` succeeds."""

    class _Proc:
        returncode = 0
        stdout = ""
        stderr = ""

    @staticmethod
    def run(*a, **kw):
        return FakeGitPreflight._Proc()


def run_main(posts, slugs, tmp_report_dir, extra_args=()):
    """Call rp.main() in-process, fully hermetic (fake git, temp posts dir)."""
    saved = (rp.read_post_from_git, rp.POSTS_DIR, rp.load_audit, rp.subprocess)
    report_path = Path(tmp_report_dir) / "report.json"
    slug_file = Path(tmp_report_dir) / "slugs.txt"
    slug_file.write_text("\n".join(slugs) + "\n", encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        rp.read_post_from_git = FakeGit(posts)
        rp.POSTS_DIR = Path(tmp)
        rp.load_audit = lambda: {}
        rp.subprocess = FakeGitPreflight
        try:
            rc = rp.main(["--slugs", str(slug_file), "--deploy-date", "2026-07-24",
                          "--report", str(report_path), *extra_args])
        finally:
            rp.read_post_from_git, rp.POSTS_DIR, rp.load_audit, rp.subprocess = saved
    report = json.loads(report_path.read_text()) if report_path.exists() else None
    return rc, report


def test_main_exit_codes():
    # errored slug -> exit 1, report file records the error
    with tempfile.TemporaryDirectory() as rdir:
        rc, report = run_main([make_post(slug="s1")], ["s1", "not-in-git"], rdir)
        check("errored slug: main returns 1", rc == 1)
        check("errored slug: report file records the error",
              report is not None and len(report["errors"]) == 1
              and report["errors"][0]["slug"] == "not-in-git")
        check("errored slug: good slug still restored", report and report["restored"] == ["s1"])

    # TopicMappingError mid-run -> exit 2, partial report with aborted_at
    with tempfile.TemporaryDirectory() as rdir:
        posts = [make_post(slug="s1"), make_post(slug="s2", topic="Nonsense Topic")]
        rc, report = run_main(posts, ["s1", "s2"], rdir)
        check("unmappable topic mid-run: main returns 2", rc == 2)
        check("unmappable topic: partial report file exists with aborted_at",
              report is not None and report.get("aborted_at", {}).get("slug") == "s2")
        check("unmappable topic: partial report keeps earlier restores",
              report and report["restored"] == ["s1"])


def test_affiliate_canon_matches_assemble_spoke():
    # restore_posts' canonical URL constants and assemble_spoke's AFFILIATE_DEFAULT
    # must describe the SAME link (modulo utm param order) — two canons would let
    # a restore rewrite hrefs away from what new spokes ship with.
    from urllib.parse import parse_qsl, urlsplit
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # globalhighlevel-site/
    import assemble_spoke  # import-safe: main() is __main__-guarded
    ours = urlsplit(f"{rp.BOOTCAMP_DOMAIN}{rp.BOOTCAMP_PATH}"
                    f"?fp_ref={rp.AFFILIATE_REF}&utm_source={rp.UTM_SOURCE}"
                    f"&utm_medium={rp.UTM_MEDIUM}")
    theirs = urlsplit(assemble_spoke.AFFILIATE_DEFAULT)
    check("affiliate canon: scheme+host match",
          (ours.scheme, ours.netloc) == (theirs.scheme, theirs.netloc))
    check("affiliate canon: path is /highlevel-bootcamp",
          ours.path == theirs.path == "/highlevel-bootcamp")
    ours_q, theirs_q = dict(parse_qsl(ours.query)), dict(parse_qsl(theirs.query))
    check("affiliate canon: fp_ref matches", ours_q.get("fp_ref") == theirs_q.get("fp_ref"))
    check("affiliate canon: query params identical modulo order", ours_q == theirs_q)


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


def test_bad_json_blob():
    # A corrupt git blob is recorded as an error and the run CONTINUES (unlike an
    # unmappable topic, which fails loudly) — and no file is written for it.
    def run(tmp):
        rp.read_post_from_git.blobs["bad"] = "{this is not json"
        report = rp.run_restore(["bad", "s1"], "2026-07-24", audit={})
        return report, sorted(x.name for x in tmp.iterdir())
    report, files = with_env([make_post()], run)
    check("bad JSON blob recorded as error",
          len(report["errors"]) == 1 and report["errors"][0]["slug"] == "bad"
          and "bad JSON" in report["errors"][0]["error"])
    check("run continued past bad blob (good slug restored)", report["restored"] == ["s1"])
    check("no file written for the bad blob", files == ["s1.json"])


def test_cli_deploy_date_validation():
    import subprocess
    script = str(Path(__file__).resolve().parent / "restore_posts.py")
    for bad in ("2026-7-4", "24-07-2026", "tomorrow"):
        proc = subprocess.run([sys.executable, script, "--slugs", "/dev/null",
                               "--deploy-date", bad], capture_output=True, text=True)
        check(f"--deploy-date {bad!r} rejected (exit 2, nothing run)",
              proc.returncode == 2 and "deploy-date" in proc.stderr)


def test_signup_rewrite():
    html = '<a href="https://app.gohighlevel.com/signup">Sign up</a> <a href="https://app.gohighlevel.com">app</a> <a href="https://developers.gohighlevel.com/docs">docs</a>'
    out, n, flagged = rp.normalize_affiliate_links(html, "en")
    check("app signup rewritten to affiliate", "fp_ref=amplifi-technologies12" in out and "app.gohighlevel.com" not in out)
    check("two app links rewritten", n == 2)
    check("developers docs link untouched + not counted", "developers.gohighlevel.com/docs" in out)


def test_topic_overrides():
    raw = json.dumps({"slug": "s1", "topic": "AI & Automation", "publishedAt": "2026-01-01",
                      "html_content": "<p>x</p>"}, ensure_ascii=False)
    text, _, _ = rp.restore_post(raw, "s1", "2026-07-24", None,
                                 overrides={"s1": "Payments & Pricing"})
    check("override beats the 8->5 map", json.loads(text)["topic"] == "Payments & Pricing")
    text2, _, _ = rp.restore_post(raw, "s1", "2026-07-24", None, overrides={"other": "CRM & Communication"})
    check("non-matching override falls through to map",
          json.loads(text2)["topic"] == "AI Receptionist & Lead Capture")
    try:
        rp.restore_post(raw, "s1", "2026-07-24", None, overrides={"s1": "Bogus Hub"})
        check("bogus override topic raises", False)
    except rp.TopicMappingError:
        check("bogus override topic raises", True)


def test_signup_rewrite_es_and_escaped():
    # es-language posts must get the -es bootcamp path on app-link rewrites
    out_es, n_es, _ = rp.normalize_affiliate_links(
        '<a href="https://app.gohighlevel.com/signup">alta</a>', "es")
    check("es app link rewritten to -es bootcamp path",
          rp.BOOTCAMP_PATH_ES in out_es and "app.gohighlevel.com" not in out_es)
    check("es app rewrite counted", n_es == 1)

    # firehose-escaped app href: output must re-escape & (no raw '&' in attribute)
    out_amp, n_amp, _ = rp.normalize_affiliate_links(
        '<a href="https://app.gohighlevel.com/signup?src=x&amp;y=1">go</a>', "en")
    attr = out_amp.split('href="', 1)[1].split('"', 1)[0]
    check("escaped app href: output re-escaped with &amp;", "&amp;" in attr)
    check("escaped app href: raw '&' never emitted into the attribute",
          "&" not in attr.replace("&amp;", ""))
    check("escaped app href counted as one rewrite", n_amp == 1)


def test_cli_topic_overrides():
    # bad topic in the override file -> exit 2 BEFORE anything is restored
    with tempfile.TemporaryDirectory() as rdir:
        ov = Path(rdir) / "overrides.json"
        ov.write_text(json.dumps({"s1": "Not A Real Hub"}), encoding="utf-8")
        rc, report = run_main([make_post(slug="s1")], ["s1"],
                              rdir, extra_args=["--topic-overrides", str(ov)])
        check("CLI: bogus override topic -> exit 2", rc == 2)
        check("CLI: bogus override file -> nothing restored (no report written)",
              report is None)

    # good override file -> override applied end-to-end through main()
    with tempfile.TemporaryDirectory() as rdir:
        ov = Path(rdir) / "overrides.json"
        ov.write_text(json.dumps({"s1": "Payments & Pricing"}), encoding="utf-8")
        rc, report = run_main([make_post(slug="s1"), make_post(slug="s2")], ["s1", "s2"],
                              rdir, extra_args=["--topic-overrides", str(ov)])
        check("CLI: run with overrides exits 0", rc == 0)
        check("CLI: both slugs restored", report and sorted(report["restored"]) == ["s1", "s2"])
        check("overrides_applied counts consumed overrides", report["overrides_applied"] == 1)


def main():
    print("test_restore_posts.py")
    for t in (test_topic_mapping, test_collision_skip, test_stamps,
              test_affiliate, test_affiliate_escaped_amp, test_slug_blocklist,
              test_main_exit_codes, test_affiliate_canon_matches_assemble_spoke,
              test_idempotency, test_dry_run_and_errors,
              test_bad_json_blob, test_cli_deploy_date_validation,
              test_signup_rewrite,
        test_signup_rewrite_es_and_escaped, test_topic_overrides,
        test_cli_topic_overrides):
        t()
    print(f"\n{'PASS' if not FAILED else 'FAIL'} — {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
