"""Pins the 2026-10-12 in-place rewrite of the Marketplace AI templates guide."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
SLUG = "list-ai-templates-gohighlevel-marketplace-sell-agents"
post = json.loads((ROOT / "posts" / f"{SLUG}.json").read_text())
h = post["html_content"]
errs = []
if post.get("transistorEpisodeId") != "38e5d1f1": errs.append("episode changed")
if not post.get("publishedAt", "").startswith("2026-04-10"): errs.append("publishedAt changed")
for n in ("01", "02"):
    if f"/images/blog/{SLUG}/shot-en-{n}.png" not in h: errs.append(f"missing shot {n}")
    if not (ROOT / "images" / "blog" / SLUG / f"shot-en-{n}.png").exists(): errs.append(f"missing file {n}")
for bad in ("TASTE DRAFT", "draft-banner", "noindex", "data-claim", "SHOT-EN", "Annotate:", "shot-gap"):
    if bad in h: errs.append(f"draft marker: {bad}")
for need in ('id="faq"', "Manage → Versions", "Major", "155000005412"):
    if need not in h: errs.append(f"missing: {need}")
if errs:
    print("FAIL", errs); sys.exit(1)
print("PASS")
