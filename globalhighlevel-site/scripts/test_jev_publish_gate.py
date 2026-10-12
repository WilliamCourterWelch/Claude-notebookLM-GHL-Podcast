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


def test_cli_exits_despite_hung_request(tmp_path):
    """A hung SDK call must not keep the process alive past the timeout."""
    import subprocess
    path = _write(tmp_path, POST)
    code = (
        "import sys,time; sys.path.insert(0,%r); import jev_publish_gate as g\n"
        "class H:\n def ask(self,s): time.sleep(60)\n def close(self): pass\n"
        "g.load_key=lambda env=None:'k'; g.JevClient=lambda k:H()\n"
        "sys.exit(g.main([%r,'--timeout','0.2','--log',%r]))\n"
    ) % (os.path.dirname(__file__), path, str(tmp_path / "l.jsonl"))
    t0 = time.time()
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0 and "SKIPPED" in r.stdout
    assert time.time() - t0 < 10


def test_changed_paths_are_relative_to_site_dir():
    import inspect
    assert "--relative" in inspect.getsource(g.changed_posts)


def test_secret_in_exception_is_redacted(tmp_path, monkeypatch):
    secret = "tsk_live_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"
    monkeypatch.setattr(g, "load_key", lambda env=None: secret)
    log = tmp_path / "log.jsonl"
    monkeypatch.setattr(g, "JevClient", lambda key: Fake(err=RuntimeError(f"bad key {key}")))
    g.main([_write(tmp_path, POST), "--log", str(log), "--json"])
    def boom(key):
        raise RuntimeError(f"init failed for {key}")
    monkeypatch.setattr(g, "JevClient", boom)
    g.main([_write(tmp_path, POST), "--log", str(log)])
    text = log.read_text()
    assert secret not in text and text.count("[redacted]") == 2


def test_hung_init_and_close_fail_open(tmp_path):
    def slow_init():
        time.sleep(30)
    t0 = time.time()
    r = g.gate_post(_write(tmp_path, POST), slow_init, 0.2, 0.6)
    assert r["verdict"] == "skipped" and time.time() - t0 < 3

    class SlowClose(Fake):
        def close(self):
            time.sleep(30)
    t0 = time.time()
    r = g.gate_post(_write(tmp_path, POST), lambda: SlowClose(), 0.5, 0.6)
    assert time.time() - t0 < 3 and r["verdict"] in ("pass", "skipped")


def test_bad_ref_is_reported_not_silent(capsys):
    assert g.main(["--changed", "no-such-ref-xyz"]) == 3
    assert "no pages were gated" in capsys.readouterr().err


def test_help_link_is_not_the_cta():
    post = dict(POST, html_content=(
        '<p>Source: <a href="https://help.gohighlevel.com/support/solutions/articles/1">HighLevel help</a>.</p>'
        '<p>Ready? <a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=x">Start the Bootcamp</a></p>'))
    cta = g.extract_fields(post)["cta"]
    assert "Start the Bootcamp" in cta and "HighLevel help" not in cta


def test_renamed_post_is_gated(tmp_path, monkeypatch):
    import subprocess
    run = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    run("init", "-q"); run("config", "user.email", "t@t"); run("config", "user.name", "t")
    (tmp_path / "posts").mkdir()
    body = json.dumps(dict(POST, html_content=POST["html_content"] * 5))
    (tmp_path / "posts" / "old.json").write_text(body)
    run("add", "-A"); run("commit", "-qm", "base")
    run("mv", "posts/old.json", "posts/new.json")
    (tmp_path / "posts" / "new.json").write_text(body.replace("Short.", "Short!"))
    run("add", "-A"); run("commit", "-qm", "rename")
    monkeypatch.chdir(tmp_path)
    assert g.changed_posts("HEAD~1") == ["posts/new.json"]
