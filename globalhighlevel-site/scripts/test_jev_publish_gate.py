"""Offline tests for the Jev publish gate. No network, no key."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import jev_publish_gate as g  # noqa: E402

POST = {
    "slug": "demo", "title": "How to Set Up Workflows in GoHighLevel", "language": "en",
    "category": "Automation",
    "html_content": "<p>Short.</p><p>Open Automation, click Create Workflow, pick a trigger, and add your first action step.</p>"
                    "<p>Ready to build? <a href=\"https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=x\">Start the Bootcamp</a></p>",
}


class Fake:
    def __init__(self, intent="on-intent", lang="en", conf=0.9, err=None, delay=0):
        self.intent, self.lang, self.conf, self.err, self.delay = intent, lang, conf, err, delay
        self.states = []

    def ask(self, state):
        self.states.append(state)
        if self.delay:
            time.sleep(self.delay)
        if self.err:
            raise self.err
        intent = self.intent(state) if callable(self.intent) else self.intent
        return {"intent": intent, "intent_conf": self.conf, "lang": self.lang, "lang_conf": self.conf}

    def close(self):
        pass


def _write(tmp_path, post):
    p = tmp_path / f"{post['slug']}.json"
    p.write_text(json.dumps(post))
    return str(p)


def test_extract_fields():
    f = g.extract_fields(POST)
    assert f["title"] == f["h1"] == POST["title"]
    assert f["intro"].startswith("Open Automation")
    assert "Link text: Start the Bootcamp" in f["cta"]


def test_pass(tmp_path):
    fake = Fake()
    r = g.gate_post(_write(tmp_path, POST), lambda: fake, 5, 0.6)
    assert r["verdict"] == "pass" and set(r["fields"]) == set(g.FIELDS)
    assert {s["field"] for s in fake.states} == set(g.FIELDS)
    assert all(set(s) == {"field", "page_topic", "text"} for s in fake.states)


def test_hold_on_draft_field(tmp_path):
    fake = Fake(intent=lambda s: "leftover-draft" if s["field"] == "intro" else "on-intent")
    r = g.gate_post(_write(tmp_path, POST), lambda: fake, 5, 0.6)
    assert r["verdict"] == "hold" and r["reasons"] == ["intro: leftover-draft (0.9)"]


def test_low_confidence_flag_is_ignored(tmp_path):
    r = g.gate_post(_write(tmp_path, POST), lambda: Fake(intent="thin", conf=0.4), 5, 0.6)
    assert r["verdict"] == "pass"


def test_es_page_needs_es(tmp_path):
    post = dict(POST, slug="es-demo", language="es")
    r = g.gate_post(_write(tmp_path, post), lambda: Fake(lang="en"), 5, 0.6)
    assert r["verdict"] == "hold"
    assert any("language en on a es page" in x for x in r["reasons"])


def test_en_page_rejects_es(tmp_path):
    r = g.gate_post(_write(tmp_path, POST), lambda: Fake(lang="es"), 5, 0.6)
    assert r["verdict"] == "hold"


def test_error_fails_open(tmp_path):
    r = g.gate_post(_write(tmp_path, POST), lambda: Fake(err=RuntimeError("503")), 5, 0.6)
    assert r["verdict"] == "skipped" and r["reasons"] == [] and "503" in r["error"]


def test_timeout_fails_open(tmp_path):
    r = g.gate_post(_write(tmp_path, POST), lambda: Fake(delay=1), 0.05, 0.6)
    assert r["verdict"] == "skipped"


def test_no_key_fails_open(tmp_path):
    def factory():
        raise RuntimeError("TYPESAFE_API_KEY not set")
    r = g.gate_post(_write(tmp_path, POST), factory, 5, 0.6)
    assert r["verdict"] == "skipped"


def test_main_exit_codes_and_log(tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"
    path = _write(tmp_path, POST)
    monkeypatch.setattr(g, "load_key", lambda env=None: "k")
    monkeypatch.setattr(g, "JevClient", lambda key: Fake(intent="off-intent"))
    assert g.main([path, "--log", str(log)]) == 2
    monkeypatch.setattr(g, "JevClient", lambda key: Fake(err=TimeoutError()))
    assert g.main([path, "--log", str(log)]) == 0
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    assert [r["verdict"] for r in rows] == ["hold", "skipped"]
    assert all("TYPESAFE_API_KEY" not in json.dumps(r) or r["verdict"] == "skipped" for r in rows)


def test_key_never_logged(tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"
    secret = "sk-test-SECRET-123"
    monkeypatch.setattr(g, "load_key", lambda env=None: secret)
    monkeypatch.setattr(g, "JevClient", lambda key: Fake(err=RuntimeError("boom")))
    g.main([_write(tmp_path, POST), "--log", str(log)])
    assert secret not in log.read_text()
