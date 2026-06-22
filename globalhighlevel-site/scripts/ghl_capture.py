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
from pathlib import Path

import ghl_capture_lib as lib


def _browse_bin() -> str:
    root = Path(__file__).resolve()
    candidates = [
        Path.home() / ".claude/skills/gstack/browse/dist/browse",
    ]
    # repo-local gstack (team mode) if present
    for p in root.parents:
        c = p / ".claude/skills/gstack/browse/dist/browse"
        if c.exists():
            candidates.insert(0, c)
            break
    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return str(c)
    sys.exit("browse binary not found. Run gstack setup, or connect the GStack Browser "
             "(/connect-chrome) so the daemon is up.")


def _browse(bin_: str, *args: str) -> str:
    res = subprocess.run([bin_, *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"browse {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout.strip()


def cmd_capture(args) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if not isinstance(plan, list) or not plan:
        sys.exit("plan must be a non-empty JSON array")
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
    c.set_defaults(func=cmd_capture)
    a = sub.add_parser("attest")
    a.add_argument("--slug", required=True)
    a.add_argument("--lang", required=True)
    a.set_defaults(func=cmd_attest)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
