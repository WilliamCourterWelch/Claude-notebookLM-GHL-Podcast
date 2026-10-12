#!/usr/bin/env python3
"""Jev publish gate: classify a post's title, H1, intro, and CTA before it ships.

Each field goes to TypeSafe Jev (model pinned, jev-1.13.0) with two questions:
  intent: on-intent / off-intent / thin / leftover-draft
  lang:   en / es
A field is flagged when intent is not on-intent (confidence >= JEV_GATE_MIN_CONF,
default 0.6) or when lang does not match the page language (/es pages = es,
English pages = en). Any flag HOLDS the ship (exit 2) with a reason per field.

Fail-open: no key, no SDK, an error, or a timeout skips the check and the page
passes (exit 0, verdict "skipped"). Jev never blocks a release.

The key is read at runtime from TYPESAFE_API_KEY, or from the box file
/home/box/.secrets/TYPESAFE_API_KEY. It is never logged or written anywhere.
Every result is appended as one JSON line to JEV_GATE_LOG (default
/home/box/var/ghl-jev-gate/log.jsonl; falls back to ~/.ghl-jev-gate.log.jsonl).

TypeSafe terms forbid training on Jev output. The log is an audit trail only.

Usage (from globalhighlevel-site/):
  python3 scripts/jev_publish_gate.py posts/<slug>.json [...]
  python3 scripts/jev_publish_gate.py --changed origin/main   # posts added/changed vs ref
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import threading
import time

MODEL_PIN = "jev-1.13.0"
KEY_FILE = "/home/box/.secrets/TYPESAFE_API_KEY"
DEFAULT_LOG = "/home/box/var/ghl-jev-gate/log.jsonl"
FIELDS = ("title", "h1", "intro", "cta")

INTENT_INSTRUCTIONS = (
    "This text is one field (named in 'field') of a published how-to article on "
    "globalhighlevel.com, a guide site for GoHighLevel (HighLevel) software users. "
    "'page_topic' is what the article is about. Judge only this field's text. "
    "For field 'cta': the text is the sentence before a call-to-action link plus the "
    "link text. A short invitation to start with HighLevel or its Bootcamp is normal "
    "finished copy and is on-intent even though it is brief and general."
)
INTENT_CRITERIA = {
    "on-intent": "Finished, publishable copy that matches the page topic and helps a GoHighLevel user.",
    "off-intent": "Finished copy, but about a different subject than the page topic, or unrelated to GoHighLevel.",
    "thin": "Too vague, generic, or empty to be useful for this field (filler, a bare keyword, no substance).",
    "leftover-draft": "Contains drafting leftovers: placeholders, TODO/TK, lorem ipsum, 'taste draft', reviewer notes, claim tags, brackets to fill in, or editor instructions.",
}
LANG_INSTRUCTIONS = "Which language is the text written in? Product names like GoHighLevel do not count."
LANG_CRITERIA = {"en": "English", "es": "Spanish"}


def _text(fragment):
    fragment = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", fragment or "")
    fragment = re.sub(r"(?s)<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def extract_fields(post):
    """title, h1, intro (first real paragraph), cta (first affiliate/CTA link text + context)."""
    body = post.get("html_content", "") or ""
    title = (post.get("title") or "").strip()
    m = re.search(r"(?is)<h1\b[^>]*>(.*?)</h1>", body)
    h1 = _text(m.group(1)) if m else title  # build.py renders title as the H1
    intro = ""
    for p in re.findall(r"(?is)<p\b[^>]*>(.*?)</p>", re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", body)):
        t = _text(p)
        if len(t) >= 60:
            intro = t[:700]
            break
    cta = ""
    for am in re.finditer(r'(?is)<a\b([^>]*)>(.*?)</a>', body):
        attrs, inner = am.group(1), am.group(2)
        if re.search(r"fp_ref=|highlevel-bootcamp|gohighlevel\.com/|/trial/|class=\"[^\"]*cta", attrs, re.I):
            t = _text(inner)
            if t:
                start = max(0, am.start() - 300)
                ctx = _text(body[start:am.start()])
                # keep whole sentences only; a cut-off word reads like a draft
                sents = re.split(r"(?<=[.!?])\s+", ctx)
                ctx = " ".join(sents[1:])[-200:] if len(sents) > 1 else ""
                ctx = ctx[ctx.find(" ") + 1:] if len(ctx) == 200 else ctx
                cta = ("Lead-in: " + ctx + " | Link text: " + t) if ctx else ("Link text: " + t)
                break
    return {"title": title, "h1": h1, "intro": intro, "cta": cta}


def expected_lang(post, path=""):
    lang = (post.get("language") or "").lower()
    if lang in ("es", "en"):
        return lang
    return "es" if "/es/" in path else "en"


def load_key(env=None):
    env = os.environ if env is None else env
    key = (env.get("TYPESAFE_API_KEY") or "").strip()
    if key:
        return key
    try:
        with open(KEY_FILE) as fh:
            return fh.read().strip()
    except OSError:
        return ""


class JevClient:
    def __init__(self, key):
        os.environ.setdefault("TYPESAFE_LOG_LEVEL", "warning")
        os.environ["TYPESAFE_API_KEY"] = key
        from typesafe_sdk import TypeSafeClient, Choice  # ImportError -> fail-open
        self._choice = Choice
        self._client = TypeSafeClient(model=MODEL_PIN).__enter__()

    def ask(self, state):
        q = {
            "intent": self._choice(instructions=INTENT_INSTRUCTIONS, criteria=INTENT_CRITERIA),
            "lang": self._choice(instructions=LANG_INSTRUCTIONS, criteria=LANG_CRITERIA),
        }
        r = self._client.system_one(state, q)
        a = r.answers
        return {
            "intent": a["intent"].choice, "intent_conf": round(float(a["intent"].confidence), 3),
            "lang": a["lang"].choice, "lang_conf": round(float(a["lang"].confidence), 3),
            "input_tokens": getattr(getattr(r, "usage", None), "input_tokens", None),
        }

    def close(self):
        try:
            self._client.__exit__(None, None, None)
        except Exception:
            pass


_TOKENISH = re.compile(r"[A-Za-z0-9_\-]{24,}")


def safe_error(exc):
    """Exception text with the API key (and anything key-shaped) removed."""
    msg = f"{type(exc).__name__}: {exc}"
    key = ""
    try:
        key = load_key()
    except BaseException:
        pass
    if key:
        msg = msg.replace(key, "[redacted]")
    return _TOKENISH.sub("[redacted]", msg)[:200]


def judge(field, ans, lang, min_conf):
    reasons = []
    if not ans:
        return reasons
    if ans["intent"] != "on-intent" and ans["intent_conf"] >= min_conf:
        reasons.append(f"{field}: {ans['intent']} ({ans['intent_conf']})")
    if ans["lang"] != lang and ans["lang_conf"] >= min_conf:
        reasons.append(f"{field}: language {ans['lang']} on a {lang} page ({ans['lang_conf']})")
    return reasons


def gate_post(path, client_factory, timeout, min_conf):
    post = json.load(open(path))
    slug = post.get("slug") or os.path.basename(path)[:-5]
    lang = expected_lang(post, path)
    fields = extract_fields(post)
    rec = {"ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "slug": slug, "lang": lang, "model": MODEL_PIN, "fields": {}, "reasons": []}
    empty = [f for f in FIELDS if not fields[f]]
    for f in empty:
        if f in ("title", "intro"):
            rec["reasons"].append(f"{f}: missing")
    topic = f"{fields['title']} (slug: {slug}; category: {post.get('category', '')})"
    # The whole SDK lifecycle (init, requests, close) runs in one daemon
    # thread bounded by the deadline: a hang anywhere fails open and can
    # never keep the process alive (daemon threads are not joined at exit).
    results = {}

    def lifecycle():
        try:
            client = client_factory()
        except BaseException as exc:  # no key / no SDK / init error
            results["_err"] = exc
            return
        try:
            def ask(f):
                try:
                    results[f] = client.ask({"field": f, "page_topic": topic, "text": fields[f]})
                except BaseException as exc:
                    results.setdefault("_err", exc)
            ts = [threading.Thread(target=ask, args=(f,), daemon=True) for f in FIELDS if fields[f]]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
        finally:
            try:
                client.close()
            except BaseException:
                pass
            results["_done"] = True

    worker = threading.Thread(target=lifecycle, daemon=True)
    worker.start()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not (results.get("_done") or "_err" in results
                                                or all(f in results for f in FIELDS if fields[f])):
        worker.join(0.02)
    asked = [f for f in FIELDS if fields[f]]
    if "_err" in results:
        exc = results["_err"]
        rec.update(verdict="skipped", error=safe_error(exc), reasons=[], fields={})
        return rec
    if not all(f in results for f in asked):
        rec.update(verdict="skipped", error=f"TimeoutError: Jev did not answer within {timeout}s",
                   reasons=[], fields={})
        return rec
    for f in asked:
        rec["fields"][f] = results[f]
        rec["reasons"] += judge(f, results[f], lang, min_conf)
    rec["verdict"] = "hold" if rec["reasons"] else "pass"
    return rec


def write_log(rec, log_path=None):
    for p in [log_path or os.environ.get("JEV_GATE_LOG") or DEFAULT_LOG,
              os.path.expanduser("~/.ghl-jev-gate.log.jsonl")]:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return p
        except OSError:
            continue
    return None


class GitDiffError(RuntimeError):
    pass


def changed_posts(ref):
    r = subprocess.run(["git", "diff", "--relative", "--name-only", "--diff-filter=AM", ref, "--", "posts/"],
                       capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise GitDiffError(f"git diff vs {ref!r} failed: {r.stderr.strip()[:200]}")
    out = r.stdout
    return [p for p in out.split() if p.endswith(".json") and os.path.exists(p)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("posts", nargs="*")
    ap.add_argument("--changed", metavar="REF", help="gate posts added/modified vs REF")
    ap.add_argument("--timeout", type=float, default=float(os.environ.get("JEV_GATE_TIMEOUT", 20)))
    ap.add_argument("--min-conf", type=float, default=float(os.environ.get("JEV_GATE_MIN_CONF", 0.6)))
    ap.add_argument("--log")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        paths = list(a.posts) + (changed_posts(a.changed) if a.changed else [])
    except GitDiffError as exc:
        # Not a Jev failure: the gate could not even list pages. Say so loudly.
        print(f"jev-gate ERROR: {exc} -- no pages were gated", file=sys.stderr)
        return 3
    if not paths:
        print("jev-gate: no posts to gate")
        return 0

    def factory():
        key = load_key()
        if not key:
            raise RuntimeError("TYPESAFE_API_KEY not set")
        return JevClient(key)

    held = 0
    for p in paths:
        rec = gate_post(p, factory, a.timeout, a.min_conf)
        where = write_log(rec, a.log)
        if a.json:
            print(json.dumps(rec, ensure_ascii=False))
        labels = ", ".join(f"{f}={v['intent']}/{v['lang']}" for f, v in rec["fields"].items())
        line = f"jev-gate {rec['verdict'].upper()} {rec['slug']} [{rec['lang']}] {labels}"
        if rec.get("error"):
            line += f" (skipped: {rec['error']})"
        print(line)
        for r in rec["reasons"]:
            print(f"  HOLD reason: {r}")
        if where is None:
            print("  warning: could not write gate log", file=sys.stderr)
        held += rec["verdict"] == "hold"
    return 2 if held else 0


if __name__ == "__main__":
    sys.exit(main())
