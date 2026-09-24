# Pattern — fold one daily AI episode onto the site

Use this for the next weekday create. The first fold is AI Booking Bots on the Conversation AI Flow Builder page (2026-09-24). Voice AI Outbound (`https://share.transistor.fm/s/bb4012cd`) and the earlier booking video (`https://www.youtube.com/watch?v=n5daF3BI4F4`) are not on the site yet. Run this checklist for each of them. Do not batch them into one PR.

## Decide before you write HTML

1. Read the help article the episode cites. Put every product claim in a fact ledger with the article URL and the "Modified on" date. If the article skips step numbers, do not fill the gap.
2. Search post bodies, not only slugs, for the action name.
3. Read Bing `top_pages` and GSC for that URL and for the Agent Studio guide. Cite the pull. A page missing from a 250-row Bing page list is not a measured zero.
4. Prefer expand. A new URL has to clear all of these: a distinct head query in the pulls, no existing page whose H2s already teach the action, and no split of the Agent Studio guide (423 Bing impressions / 3 clicks / position 4.0 on the 2026-09-24 28-day pull).
5. If two HighLevel surfaces share a verb ("book"), keep them in separate headings. This fold kept the flow-canvas Book Appointment action separate from the workflow action.

## What to add on the host page

- A 5-step list in plain `<h3 id="extractable-steps">` plus `<ol>`, after the intro and before the first `<h2>`. No `#f0f4ff` box. `sanitize_content` deletes those boxes.
- One `<h2 id="...">` for the episode so the template TOC (first 8 h2s) can point at it.
- Transistor: iframe `https://share.transistor.fm/e/{id}` and a visible link to `https://share.transistor.fm/s/{id}`. Leave `transistorEpisodeId` alone when it already embeds a different episode, and say so next to the new player.
- YouTube: `https://www.youtube-nocookie.com/embed/{id}` plus the watch URL. Unlisted is fine if the embed returns 200.
- Bootcamp CTAs through the affiliate URL with `fp_ref=amplifi-technologies12`, `utm_source=globalhighlevel`, `utm_medium=blog`, a campaign that names the episode, and a new `utm_content` slot. Do not reuse `extractable-steps`, `cta3`, `tldr`, `nav`, or `in_article`. One slot per CTA. `rel="nofollow noopener"` and `target="_blank"`.
- Help-center links stay citations. No `fp_ref` on `help.gohighlevel.com`.

## Links

- Same language and same topic only. `unwrap_cross_silo_links` drops the href and keeps the words when the topic differs. Multi-calendar booking is CRM & Communication, so this AI page does not link it.
- One new paragraph, one `<a>`, unique anchor text. The sitewide cap is 3 identical anchor-to-URL pairs, and the hash is ignored when the cap is counted, so four spokes must not share anchor text to the same path.
- Link the host out to the nearest same-silo spokes, and put one sentence back on each spoke and on the topic pillar. Pillar `/blog/` HTML strips internal links; the category hub keeps a same-silo href.
- Do not add an outbound link on the money page.

## Leave alone

- Free-trial and agency sub-account titles and H1s through 2026-10-13.
- Agent Studio title and H1: `GoHighLevel Agent Studio: Build AI Agents Step by Step`, unless a fresh pull says that string is the thing hurting clicks.
- Homepage. Meta Pixel. India, Spanish, and Arabic twins in the same PR.
- `seo-cooldown.json` (retired). gbrain timeline when gbrain is actually connected; do not block the fold on it.

## Gates

From `globalhighlevel-site/`: `python3 -m pytest scripts/ -q`, then `python3 build.py`, then `python3 verify.py`. Grep the built HTML for the new iframe src and the `utm_content` slot. A green verify does not prove an internal link survived.
