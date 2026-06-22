#!/usr/bin/env python3
"""ghl-capture — capture step (EXECUTION).

Drives the already-authed GStack Browser (canon `browse` binary) to screenshot
GHL screens named in a capture plan, saving raws to captures/<lang>/ and writing
a provenance manifest with MACHINE-captured url + timestamp. Then runs an
interactive attestation pass where the human (Bill) confirms each image is
PII-clean against the fixed checklist and each caption is truthful.

This script does NOT log in (assumes Bill is already authed in the GStack
Browser; GHL uses localStorage tokens, headless password login fails) and does
NOT auto-detect PII. Honesty is human-attested, recorded as `attested: true`.

Subcommands:
  capture --plan PLAN.json --slug SLUG --lang LANG
  attest  --slug SLUG --lang LANG

Plan JSON: [{"name","url_or_app_area","claim_supported","forbidden_overclaims"}]
`name` becomes the raw basename: captures/<lang>/<name>.png
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import ghl_capture_lib as lib


def _browse_bin() -> str:
    # Only the trusted global install — never a repo-local binary (a poisoned
    # checkout shipping its own .claude/skills/gstack/browse would otherwise run
    # arbitrary code, flagged by review).
    c = Path.home() / ".claude/skills/gstack/browse/dist/browse"
    if c.exists() and os.access(c, os.X_OK):
        return str(c)
    sys.exit("browse binary not found at ~/.claude/skills/gstack/browse/dist/browse. "
             "Run gstack setup, or connect the GStack Browser (/connect-chrome).")


def _browse(bin_: str, *args: str, timeout: float = 60.0) -> str:
    try:
        res = subprocess.run([bin_, *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"browse {args[0] if args else ''} timed out after {timeout}s "
                           "(is the GStack Browser still connected?)")
    if res.returncode != 0:
        raise RuntimeError(f"browse {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout.strip()


def cmd_capture(args) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if not isinstance(plan, list) or not plan:
        sys.exit("plan must be a non-empty JSON array")
    try:
        lib.safe_component(args.slug, "slug")
        lib.safe_component(args.lang, "lang")
        for entry in plan:
            lib.safe_component(entry["name"], "plan name")
    except (ValueError, KeyError, TypeError) as exc:
        sys.exit(f"refuse: {exc}")
    bin_ = _browse_bin()
    cap_dir = lib.CAPTURES / args.lang
    cap_dir.mkdir(parents=True, exist_ok=True)
    manifest = lib.load_manifest(args.slug, args.lang)

    print(f"Capturing {len(plan)} screen(s) for {args.slug} [{args.lang}].")
    print("Assumes you are already logged into the GHL sandbox in the GStack Browser.\n")
    for entry in plan:
        name = entry["name"]
        target = entry["url_or_app_area"]
        out = cap_dir / f"{name}.png"
        lib.assert_under(out, cap_dir)  # defense in depth after name validation
        if target.startswith("http"):
            _browse(bin_, "goto", target)
            try:
                live_url = _browse(bin_, "url")
            except RuntimeError:
                live_url = target
        else:
            # app-area capture: no address-bar URL to read (spec finding N2)
            live_url = f"app-area:{target}"
            print(f"  [{name}] navigate to '{target}' in the browser, then press Enter…")
            input()
        # GHL is a heavy SPA: wait for it to render before shooting, or we
        # capture the loading spinner. Poll readyState then settle, capped.
        deadline = time.time() + args.settle
        ready = False
        while time.time() < deadline:
            try:
                if _browse(bin_, "js", "document.readyState").strip().strip('"') == "complete":
                    ready = True
                    break
            except RuntimeError:
                pass
            time.sleep(0.5)
        if not ready:
            print(f"  WARNING [{name}]: page never reached readyState=complete in "
                  f"{args.settle}s — the screenshot may be a spinner. Read the PNG before attesting.")
        time.sleep(args.settle_after)  # let SPA paint past the spinner
        _browse(bin_, "screenshot", str(out))
        e = lib.manifest_entry(manifest, name) or {"name": name}
        e.update({
            "raw": f"captures/{args.lang}/{name}.png",
            "url": live_url,                       # machine-captured, not typed
            "captured_at": lib.utc_now(),          # machine clock, not hand-entered
            "claim_supported": entry.get("claim_supported", ""),
            "forbidden_overclaims": entry.get("forbidden_overclaims", ""),
            "attested": False,
            "published": None,
        })
        if not lib.manifest_entry(manifest, name):
            manifest.setdefault("images", []).append(e)
        print(f"  captured {out.name}  ({live_url})")

    lib.save_manifest(args.slug, args.lang, manifest)
    print(f"\nWrote {lib.manifest_path(args.slug, args.lang)}")
    print("NEXT: run `attest` to sign off PII-clean + truthful captions before optimize/wire.")
    return 0


def cmd_attest(args) -> int:
    manifest = lib.load_manifest(args.slug, args.lang)
    imgs = manifest.get("images", [])
    if not imgs:
        sys.exit("no captured images in manifest — run `capture` first")

    # Non-interactive path: record a sign-off decision already made by the human
    # (e.g. via a UI prompt). The decision MUST originate from the human, not the
    # script — this just persists it. Honesty stays human-attested.
    if args.name:
        e = lib.manifest_entry(manifest, args.name)
        if e is None:
            sys.exit(f"no captured image named {args.name!r} in manifest")
        clean = args.decision == "yes"
        e["attested"] = clean
        e["attested_at"] = lib.utc_now()
        e["attested_by"] = args.by
        lib.save_manifest(args.slug, args.lang, manifest)
        print(f"recorded {args.name}: attested={clean} (by {args.by})")
        return 0

    print("PII / data-leak checklist — confirm EACH capture shows NONE of these:")
    for item in lib.PII_CHECKLIST:
        print(f"  - {item}")
    print("Also confirm the caption you will use states only what the image shows "
          "(no invented metric/result).\n")
    changed = False
    for e in imgs:
        raw = lib.SITE / e["raw"]
        ans = input(f"[{e['name']}] {raw}\n  clean + caption truthful? (y/N) ").strip().lower()
        if ans == "y":
            e["attested"] = True
            e["attested_at"] = lib.utc_now()
            changed = True
        else:
            e["attested"] = False
            print("  -> NOT attested; this image will be refused by optimize/wire.")
    if changed:
        lib.save_manifest(args.slug, args.lang, manifest)
        print(f"\nUpdated {lib.manifest_path(args.slug, args.lang)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ghl-capture: capture + attest GHL screenshots")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--plan", required=True)
    c.add_argument("--slug", required=True)
    c.add_argument("--lang", required=True)
    c.add_argument("--settle", type=float, default=8.0,
                   help="max seconds to wait for document.readyState=complete")
    c.add_argument("--settle-after", type=float, default=3.0,
                   help="extra seconds after ready for the SPA to paint past the spinner")
    c.set_defaults(func=cmd_capture)
    a = sub.add_parser("attest")
    a.add_argument("--slug", required=True)
    a.add_argument("--lang", required=True)
    a.add_argument("--name", help="non-interactive: record a decision for one image")
    a.add_argument("--decision", choices=["yes", "no"], default="yes",
                   help="with --name: yes=attested clean, no=rejected")
    a.add_argument("--by", default="owner", help="who attested (recorded in manifest)")
    a.set_defaults(func=cmd_attest)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
