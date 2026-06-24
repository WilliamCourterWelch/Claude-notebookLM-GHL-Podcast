import html
# Curated AI/Agent-Studio silo: 1 pillar + 15 spokes, mapped to real recoverable pages
pillar={'kw':'gohighlevel ai agents / agent studio','title':'GoHighLevel AI Agents & Agent Studio — the complete guide',
        'src':'how-to-build-ai-agents-in-gohighlevel-agent-studio-guide','imp':402}
spokes=[
 (1,'Automate client support with Ask AI','automate-client-support-ask-ai-agent-studio-gohighlevel',1862,'recover'),
 (2,'Agent Studio template library','build-ai-agents-faster-gohighlevel-template-library-guide',1162,'recover'),
 (3,'Build your first AI agent (setup)','build-smarter-ai-agents-gohighlevel-agent-studio-setup',243,'recover'),
 (4,'Set up Agent Studio triggers','set-up-agent-studio-triggers-gohighlevel-real-time-automation',215,'recover'),
 (5,'Ask AI upgrades — work smarter','master-ask-ai-upgrades-gohighlevel-work-smarter',143,'recover'),
 (6,'Use variables in Agent Studio','how-to-use-variables-in-gohighlevel-agent-studio-save-time',134,'recover'),
 (7,'Connect public APIs to an agent','how-to-use-public-apis-gohighlevel-agent-studio',132,'recover'),
 (8,'Add a knowledge base (AI employees)','how-to-add-tables-to-knowledge-base-in-gohighlevel-ai-employees',79,'recover'),
 (9,'Build AI bots without code','build-ai-bots-without-code-gohighlevel-guided-form-setup',39,'recover'),
 (10,'Monitor agents with agent logs','how-to-monitor-ai-agents-in-gohighlevel-agent-logs-guide',37,'recover'),
 (11,'Use the Agent Studio Router','how-to-use-agent-studio-router-in-gohighlevel-smarter-ai-flows',16,'recover'),
 (12,'Test & debug AI agents','how-to-test-debug-ai-agents-gohighlevel',15,'recover'),
 (13,'Organize with Agent Studio folders','how-to-manage-agent-studio-folders-gohighlevel-stay-organized',7,'recover'),
 (14,'Set AI agent permissions (team security)','manage-ai-agent-permissions-gohighlevel-team-security',0,'thin'),
 (15,'Set a brand voice for your agent','how-to-use-brand-voice-in-gohighlevel-agent-studio-guide',0,'thin'),
]
tot=pillar['imp']+sum(s[3] for s in spokes)
def spoke_card(n,title,src,imp,st):
    badge=('<span class="b rec">RECOVER</span>' if st=='recover' else '<span class="b thin">RECOVER (thin)</span>')
    impc='var(--text)' if imp>=50 else 'var(--muted)'
    return f'''<div class="spoke">
      <div class="sh"><span class="num">{n:02d}</span>{badge}</div>
      <div class="st">{html.escape(title)}</div>
      <div class="meta"><span class="imp" style="color:{impc}">{imp} imp</span><span class="src">{html.escape(src[:46])}</span></div>
    </div>'''
cards=''.join(spoke_card(*s) for s in spokes)
out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI / Agent Studio — Caleb silo</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07080a;--surface:#111520;--surface2:#171c2a;--line:#222a3d;--amber:#f59e0b;--text:#eef2ff;--text2:#9aa6c4;--muted:#5b688a;--green:#34d399;--blue:#7c9cff}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--text2);font-family:"DM Sans",system-ui,sans-serif;font-size:14px;line-height:1.5;padding-bottom:80px}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
h1{{color:var(--text);font-weight:800;font-size:2.1rem;letter-spacing:-1px;margin:10px 0;line-height:1.1}}
.lead{{font-size:1.04rem;color:var(--text);max-width:880px}}
header{{padding:42px 0 22px;border-bottom:1px solid var(--line);background:radial-gradient(800px 320px at 82% -20%,rgba(245,158,11,.10),transparent 60%)}}
section{{padding:28px 0;border-bottom:1px solid var(--line)}}
.pillarbox{{background:linear-gradient(180deg,rgba(124,156,255,.12),#0c0f16);border:1px solid rgba(124,156,255,.45);border-radius:14px;padding:22px;text-align:center;max-width:680px;margin:0 auto}}
.pillarbox .tier{{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--blue)}}
.pillarbox h2{{color:var(--text);font-size:1.5rem;font-weight:800;margin:8px 0;line-height:1.15}}
.pillarbox .kw{{font-family:ui-monospace,monospace;font-size:.8rem;color:var(--amber);background:var(--surface2);padding:3px 10px;border-radius:6px;display:inline-block}}
.pillarbox .src{{font-size:.78rem;color:var(--muted);margin-top:10px}}
.stem{{width:2px;height:26px;background:var(--line);margin:0 auto}}
.tier2lbl{{text-align:center;font-size:11px;font-weight:800;letter-spacing:1px;color:var(--muted);margin:6px 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.spoke{{background:#0c0f16;border:1px solid var(--line);border-radius:11px;padding:13px;border-left:3px solid var(--blue)}}
.sh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}
.num{{font-weight:800;color:var(--muted);font-size:.82rem}}
.b{{font-size:9px;font-weight:800;padding:2px 7px;border-radius:10px;letter-spacing:.4px}}
.b.rec{{background:rgba(52,211,153,.15);color:var(--green)}} .b.thin{{background:rgba(245,158,11,.15);color:var(--amber)}}
.st{{color:var(--text);font-weight:700;font-size:.94rem;line-height:1.25}}
.meta{{display:flex;justify-content:space-between;align-items:center;margin-top:8px;gap:8px}}
.imp{{font-weight:700;font-size:.8rem;font-variant-numeric:tabular-nums}}
.src{{font-family:ui-monospace,monospace;font-size:.66rem;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}
.c{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px}}.c .n{{font-size:1.5rem;font-weight:800;color:var(--text)}}.c .l{{font-size:.76rem;color:var(--muted)}}
h3{{color:var(--text);font-weight:800;font-size:1.25rem;margin-bottom:6px}}
.rules{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}}
.rule{{background:var(--surface);border-left:3px solid var(--green);border-radius:0 10px 10px 0;padding:13px 16px;font-size:.92rem}}
.rule b{{color:var(--text)}}
@media(max-width:860px){{.grid{{grid-template-columns:1fr 1fr}}.cards{{grid-template-columns:1fr 1fr}}.rules{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div class="wrap">
<div class="eyebrow">Pillar #1 · AI Agents &amp; Agent Studio · the Caleb silo</div>
<h1>The biggest pillar, mapped: 1 pillar + 15 spokes.</h1>
<p class="lead">Your top-demand silo, structured Caleb's way. Every one of the 15 spokes maps to a page you already wrote and can recover — so this whole pillar is a reorganize-and-upgrade job, not a write-from-scratch.</p>
<div class="cards">
<div class="c"><div class="n">{tot:,}</div><div class="l">impressions in this silo</div></div>
<div class="c"><div class="n">15 / 15</div><div class="l">spokes have a recoverable page</div></div>
<div class="c"><div class="n">13</div><div class="l">solid · 2 thin (need a rebuild)</div></div>
<div class="c"><div class="n">pos 8-12</div><div class="l">where most already rank</div></div>
</div></div></header>

<section><div class="wrap">
<div class="pillarbox">
  <div class="tier">TIER 1 · PILLAR PAGE</div>
  <h2>{html.escape(pillar['title'])}</h2>
  <span class="kw">target: {html.escape(pillar['kw'])}</span>
  <div class="src">base page to expand: {html.escape(pillar['src'])} · {pillar['imp']} imp</div>
</div>
<div class="stem"></div>
<div class="tier2lbl">TIER 2 · 15 VARIATION SPOKES (each its own keyword)</div>
<div class="grid">{cards}</div>
</div></section>

<section><div class="wrap">
<h3>How they link (Caleb's silo rules)</h3>
<div class="rules">
  <div class="rule"><b>Pillar → all 15 spokes.</b> The pillar page links down to every spoke with a unique, descriptive body anchor ("set up Agent Studio triggers", not "click here").</div>
  <div class="rule"><b>Every spoke → back to the pillar.</b> One link up to the pillar from each spoke's body.</div>
  <div class="rule"><b>Spokes form link circles.</b> Spoke 1 → 2 → 3 → … → 1, so equity flows around the silo.</div>
  <div class="rule"><b>No cross-silo links.</b> Nothing here links to the Agency or Payments silos — even "clone agents to sub-accounts" stays out (it'd cross into the Agency silo).</div>
</div>
<div class="rule" style="border-left-color:var(--amber);margin-top:12px"><b>Build = recover + upgrade.</b> 13 spokes recover cleanly from existing pages (most already rank pos 8-12). 2 are thin and get rebuilt via the content-planner method. The pillar page gets expanded from the 402-imp guide into a true overview that links to all 15. Republish at original slugs to recover the impressions.</div>
</div></section>
</body></html>'''
open('/Users/kerapassante/Documents/ghl-ai-silo.html','w').write(out)
print("wrote ghl-ai-silo.html")
