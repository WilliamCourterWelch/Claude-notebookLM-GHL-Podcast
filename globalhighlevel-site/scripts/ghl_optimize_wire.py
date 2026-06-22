#!/usr/bin/env python3
"""ghl-capture — optimize / wire / orphan-check step (EXECUTION).

  optimize --slug SLUG --lang LANG [--max-width 1200]
      Pillow-optimize every ATTESTED raw in the manifest into
      images/<lang>/<slug>-<n>.png (n = max existing +1, never overwrite).
      Refuses any image not attested:true. Records `published` in the manifest.

  wire --post SLUG --image /images/<lang>/<file> --alt "..." --caption "..."
       --after "<marker>"
      Insert the site-standard <figure class="post-figure"> after the first
      occurrence of <marker> in the post's html_content. Refuses unless the
      image is published AND its manifest entry is attested:true.

  orphan-check [--json]
      Leak gate: published images referenced by zero posts (orphans) + post
      references with no file (broken). Exit 1 if any found.

Never publishes the site — /ship owns deploy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import ghl_capture_lib as lib


def _find_manifest_for_image(site_path: str):
    """site_path like /images/<lang>/<file>. Find the manifest entry whose
    `published` matches, across all manifests. Returns (slug, lang, entry)."""
    rel = site_path.lstrip("/")  # images/<lang>/<file>
    for mf in lib.CAPTURES.rglob("*.manifest.json"):
        data = json.loads(mf.read_text(encoding="utf-8"))
        for e in data.get("images", []):
            if e.get("published") == "/" + rel:
                return data.get("slug"), data.get("lang"), e
    return None, None, None


def cmd_optimize(args) -> int:
    manifest = lib.load_manifest(args.slug, args.lang)
    imgs = manifest.get("images", [])
    if not imgs:
        sys.exit("no captured images — run capture + attest first")
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow not installed: pip install Pillow")

    out_dir = lib.IMAGES / args.lang
    out_dir.mkdir(parents=True, exist_ok=True)
    done = 0
    for e in imgs:
        if not e.get("attested"):
            print(f"  SKIP {e['name']}: not attested (honesty gate)")
            continue
        if e.get("published"):
            print(f"  SKIP {e['name']}: already published -> {e['published']}")
            continue
        raw = lib.SITE / e["raw"]
        if not raw.exists():
            print(f"  SKIP {e['name']}: raw missing {raw}")
            continue
        n = lib.next_index(args.slug, args.lang)
        out = out_dir / f"{args.slug}-{n}.png"
        with Image.open(raw) as im:
            im = im.convert("RGB") if im.mode in ("P", "RGBA") else im
            if im.width > args.max_width:
                ratio = args.max_width / im.width
                im = im.resize((args.max_width, round(im.height * ratio)), Image.LANCZOS)
            im.save(out, "PNG", optimize=True)
        e["published"] = "/images/" + out.relative_to(lib.IMAGES).as_posix()
        e["published_at"] = lib.utc_now()
        done += 1
        print(f"  optimized {raw.name} -> {e['published']}")
    lib.save_manifest(args.slug, args.lang, manifest)
    print(f"\n{done} image(s) optimized. Manifest updated.")
    return 0


def cmd_wire(args) -> int:
    slug, lang, entry = _find_manifest_for_image(args.image)
    if entry is None:
        sys.exit(f"refuse: {args.image} has no manifest entry. optimize it first "
                 "(only attested, optimized captures may be wired).")
    if not entry.get("attested"):
        sys.exit(f"refuse: {args.image} is not attested:true (honesty gate).")
    img_file = lib.IMAGES / args.image.split("/images/", 1)[1]
    if not img_file.exists():
        sys.exit(f"refuse: image file missing on disk: {img_file}")

    data = lib.load_post(args.post)
    html_content = data.get("html_content", "")
    fragment = lib.figure_html(args.image, args.alt, args.caption)
    if args.image in html_content:
        sys.exit(f"refuse: {args.image} already referenced in {args.post}")
    try:
        data["html_content"] = lib.insert_after_marker(html_content, args.after, fragment)
    except ValueError as exc:
        sys.exit(f"refuse: {exc}")
    lib.save_post(args.post, data)
    # record wiring back-reference in manifest
    mf = json.loads(lib.manifest_path(slug, lang).read_text(encoding="utf-8"))
    for e in mf.get("images", []):
        if e.get("published") == args.image:
            e.setdefault("wired_into", []).append(args.post)
    lib.save_manifest(slug, lang, mf)
    print(f"wired {args.image} into {args.post} after marker.")
    return 0


def cmd_orphan_check(args) -> int:
    res = lib.orphan_check()
    if args.json:
        print(json.dumps({"orphans": res["orphans"], "broken": res["broken"]}, indent=2))
    else:
        if res["orphans"]:
            print("ORPHANS (published image referenced by zero posts):")
            for o in res["orphans"]:
                print(f"  {o}")
        if res["broken"]:
            print("BROKEN (post references a missing image file):")
            for b in res["broken"]:
                print(f"  {b}  (refs: {', '.join(res['referenced'][b])})")
        if not res["orphans"] and not res["broken"]:
            print("OK: no orphans, no broken references.")
    return 1 if (res["orphans"] or res["broken"]) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="ghl-capture optimize/wire/orphan-check")
    sub = ap.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("optimize")
    o.add_argument("--slug", required=True)
    o.add_argument("--lang", required=True)
    o.add_argument("--max-width", type=int, default=1200)
    o.set_defaults(func=cmd_optimize)

    w = sub.add_parser("wire")
    w.add_argument("--post", required=True)
    w.add_argument("--image", required=True, help="/images/<lang>/<file>")
    w.add_argument("--alt", required=True)
    w.add_argument("--caption", required=True)
    w.add_argument("--after", required=True, help="exact substring to insert after")
    w.set_defaults(func=cmd_wire)

    c = sub.add_parser("orphan-check")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_orphan_check)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
