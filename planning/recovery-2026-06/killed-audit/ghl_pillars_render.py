import json,html
pillars=json.load(open('/tmp/ghl_pillars.json'))
TYPECLR={'topic':'#7c9cff','persona':'#34d399','lang':'#fb7185','geo':'#a88bfa','money':'#f59e0b'}
TYPELBL={'topic':'TOPIC','persona':'PERSONA','lang':'LANGUAGE','geo':'GEO','money':'MONEY'}
def card(p):
    clr=TYPECLR.get(p['type'],'#7c9cff')
    spokes=p['pages'][:8]
    lis=""
    for s in spokes:
        live='<span class="live">LIVE</span>' if s.get('live') else ''
        imp=s.get('imp',0)
        impc='var(--text)' if imp>=50 else 'var(--muted)'
        lis+=f'<li><span class="imp" style="color:{impc}">{imp}</span><span class="sl">{html.escape((s.get("slug") or "")[:52])}</span>{live}</li>'
    more=p['n']-len(spokes)
    if more>0: lis+=f'<li class="more">+ {more} more pages in this pillar</li>'
    live_b=f'<span class="livecount">{p["live"]} live</span>' if p['live'] else ''
    return f'''<div class="pillar" style="border-top:3px solid {clr}">
      <div class="ph"><span class="ptype" style="background:{clr}22;color:{clr}">{TYPELBL.get(p['type'],'TOPIC')}</span>{live_b}</div>
      <h3>{html.escape(p['name'])}</h3>
      <div class="stats"><span class="big">{p['imp']:,}</span> impressions · <b>{p['n']}</b> pages · {p['clk']} clicks</div>
      <ul>{lis}</ul>
    </div>'''
eng=[p for p in pillars if p['type'] in('topic','persona','money')]
persona=[p for p in pillars if p['type']=='persona']
lang=[p for p in pillars if p['type'] in('lang','geo')]
topic=[p for p in pillars if p['type'] in('topic','money')]
def grid(ps): return '<div class="grid">'+''.join(card(p) for p in ps)+'</div>'
total_imp=sum(p['imp'] for p in pillars)
html_out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GoHighLevel — Topic Pillars (Caleb silos from real data)</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07080a;--surface:#111520;--surface2:#171c2a;--line:#222a3d;--amber:#f59e0b;--text:#eef2ff;--text2:#9aa6c4;--muted:#5b688a;--green:#34d399}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--text2);font-family:"DM Sans",system-ui,sans-serif;font-size:14px;line-height:1.5;padding-bottom:80px}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
h1{{color:var(--text);font-weight:800;font-size:2.2rem;letter-spacing:-1px;margin:10px 0;line-height:1.08}}
.lead{{font-size:1.05rem;color:var(--text);max-width:900px}}
header{{padding:44px 0 22px;border-bottom:1px solid var(--line);background:radial-gradient(800px 320px at 82% -20%,rgba(245,158,11,.10),transparent 60%)}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}
.c{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px}}.c .n{{font-size:1.6rem;font-weight:800;color:var(--text)}}.c .l{{font-size:.78rem;color:var(--muted)}}
section{{padding:30px 0;border-bottom:1px solid var(--line)}}
h2{{color:var(--text);font-weight:800;font-size:1.4rem;margin-bottom:4px}}
.sub{{font-size:.92rem;color:var(--muted);margin-bottom:8px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}}
.pillar{{background:#0c0f16;border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column}}
.ph{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.ptype{{font-size:10px;font-weight:800;letter-spacing:.5px;padding:2px 8px;border-radius:20px}}
.livecount{{font-size:10px;font-weight:700;color:var(--green);background:rgba(52,211,153,.13);padding:2px 8px;border-radius:20px}}
.pillar h3{{color:var(--text);font-size:1.08rem;font-weight:800;margin-bottom:4px}}
.stats{{font-size:.82rem;color:var(--muted);margin-bottom:10px}}.stats .big{{color:var(--amber);font-weight:800;font-size:1.05rem}}.stats b{{color:var(--text2)}}
.pillar ul{{list-style:none;margin-top:auto;display:flex;flex-direction:column;gap:5px}}
.pillar li{{display:flex;align-items:center;gap:8px;font-size:.8rem;border-top:1px solid var(--line);padding-top:5px}}
.pillar li:first-child{{border-top:0}}
.imp{{font-weight:700;min-width:34px;text-align:right;font-variant-numeric:tabular-nums}}
.sl{{font-family:ui-monospace,monospace;font-size:.72rem;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.live{{font-size:8.5px;font-weight:800;color:var(--green);background:rgba(52,211,153,.14);padding:1px 5px;border-radius:10px;margin-left:auto}}
.more{{color:var(--muted);font-style:italic;font-size:.75rem}}
.note{{background:var(--surface);border-left:3px solid var(--amber);border-radius:0 10px 10px 0;padding:14px 18px;margin-top:16px;font-size:.95rem}}.note b{{color:var(--text)}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr 1fr}}.cards{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<header><div class="wrap">
<div class="eyebrow">Topic pillars · Caleb silos built from your real pages + GSC</div>
<h1>Every page you had, clustered into pillars by demand.</h1>
<p class="lead">948 pages (931 killed + 17 live) sorted into {len(pillars)} topic silos, ranked by the Google impressions they actually pulled. Each pillar = a Caleb Tier-1 pillar; the pages under it are its Tier-2 variations (spokes). This is the blueprint — build the high-demand pillars first.</p>
<div class="cards">
<div class="c"><div class="n">{len(pillars)}</div><div class="l">topic pillars</div></div>
<div class="c"><div class="n">948</div><div class="l">pages to draw from</div></div>
<div class="c"><div class="n">{total_imp:,}</div><div class="l">total impressions across pillars</div></div>
<div class="c"><div class="n">AI Agents</div><div class="l">#1 pillar by demand (4,651 imp)</div></div>
</div></div></header>

<section><div class="wrap">
<h2>English topic pillars <span class="sub" style="display:inline">— ranked by real demand</span></h2>
<div class="sub">Blue = feature/topic silo · Green = persona silo (service / agency) · Amber = the money page</div>
{grid(topic)}
</div></section>

<section><div class="wrap">
<h2>Persona pillars (the "Which are you?" silos)</h2>
<div class="sub">These rank for audience keywords ("gohighlevel agency", "gohighlevel for service business"). Note how THIN Service Businesses is — it was barely built (7 pages). Agency has real material.</div>
{grid(persona)}
</div></section>

<section><div class="wrap">
<h2>Language &amp; geo silos (separate sites, parallel)</h2>
<div class="sub">Spanish/LATAM and India are their own language/geo silos — not English topic pillars. Big demand, kept separate per Caleb (no cross-linking across silos).</div>
{grid(lang)}
</div></section>

<section><div class="wrap">
<div class="note"><b>What this tells us to build, in order:</b> the demand is loudest in <b>AI Agents &amp; Agent Studio</b> (4,651 imp), <b>Workflows &amp; Automation</b> (3,274), and <b>Agency/White-Label/SaaS</b> (1,423) — and you already have the pages for them, killed and recoverable. <b>Service Businesses</b> is nearly empty (7 pages) — that pillar is genuinely new ground we'd build from scratch. "Other/Misc" (154 pages) needs a second pass to split into real pillars.</div>
</div></section>
</body></html>'''
open('/Users/kerapassante/Documents/ghl-topic-pillars.html','w').write(html_out)
print("wrote ghl-topic-pillars.html")
