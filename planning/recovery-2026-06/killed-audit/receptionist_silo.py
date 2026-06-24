import html
pillar={'kw':'ai receptionist · virtual receptionist · ai answering service','vol':'~11,000/mo combined','kd':'11',
        'title':'AI Receptionist &amp; Answering Service for Small Business'}
# 15 spokes: keyword, volume, KD, status (NEW = never targeted / RECOVER = have a GHL page)
spokes=[
 (1,'Virtual receptionist services',2400,'—','NEW'),
 (2,'AI receptionist for small business',1000,'13','NEW'),
 (3,'Answering service for small business',880,'—','NEW'),
 (4,'AI phone answering service',720,'—','NEW'),
 (5,'Best answering service for small business',720,'—','NEW'),
 (6,'AI receptionist software',390,'—','NEW'),
 (7,'Phone answering service for small business',390,'—','NEW'),
 (8,'Medical / niche virtual receptionist',390,'—','NEW'),
 (9,'Best AI receptionist tools (vs Smith.ai, Ruby…)',480,'—','NEW'),
 (10,'AI receptionist vs human receptionist',200,'—','NEW'),
 (11,'AI receptionist pricing &amp; cost',200,'—','NEW'),
 (12,'24/7 &amp; after-hours answering',300,'—','NEW'),
 (13,'Missed-call text-back (setup)',390,'0','RECOVER'),
 (14,'Set up Voice AI in GoHighLevel',122,'7','RECOVER'),
 (15,'Automated review requests',40,'0','RECOVER'),
]
def card(n,kw,vol,kd,st):
    badge=('<span class="b new">NEW — gap</span>' if st=='NEW' else '<span class="b rec">RECOVER</span>')
    kdtxt=f'KD {kd}' if kd!='—' else ''
    return f'''<div class="spoke"><div class="sh"><span class="num">{n:02d}</span>{badge}</div>
      <div class="st">{kw}</div>
      <div class="meta"><span class="vol">{vol:,}/mo</span><span class="kd">{kdtxt}</span></div></div>'''
cards=''.join(card(*s) for s in spokes)
out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Receptionist hub — Caleb silo</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07080a;--surface:#111520;--surface2:#171c2a;--line:#222a3d;--amber:#f59e0b;--text:#eef2ff;--text2:#9aa6c4;--muted:#5b688a;--green:#34d399;--blue:#7c9cff}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--text2);font-family:"DM Sans",system-ui,sans-serif;font-size:14px;line-height:1.5;padding-bottom:80px}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
h1{{color:var(--text);font-weight:800;font-size:2.05rem;letter-spacing:-1px;margin:10px 0;line-height:1.1}}
.lead{{font-size:1.04rem;color:var(--text);max-width:880px}}
header{{padding:42px 0 22px;border-bottom:1px solid var(--line);background:radial-gradient(800px 320px at 82% -20%,rgba(245,158,11,.10),transparent 60%)}}
section{{padding:28px 0;border-bottom:1px solid var(--line)}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}
.c{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}}.c .n{{font-size:1.5rem;font-weight:800;color:var(--text)}}.c .l{{font-size:.76rem;color:var(--muted)}}
.pillarbox{{background:linear-gradient(180deg,rgba(245,158,11,.12),#0c0f16);border:1px solid rgba(245,158,11,.5);border-radius:14px;padding:24px;text-align:center;max-width:720px;margin:0 auto}}
.pillarbox .tier{{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--amber)}}
.pillarbox h2{{color:var(--text);font-size:1.6rem;font-weight:800;margin:8px 0;line-height:1.15}}
.pillarbox .kw{{font-family:ui-monospace,monospace;font-size:.78rem;color:var(--amber);background:var(--surface2);padding:4px 11px;border-radius:6px;display:inline-block}}
.pillarbox .vol{{font-size:.85rem;color:var(--text2);margin-top:10px}}
.stem{{width:2px;height:26px;background:var(--line);margin:0 auto}}
.tier2lbl{{text-align:center;font-size:11px;font-weight:800;letter-spacing:1px;color:var(--muted);margin:6px 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.spoke{{background:#0c0f16;border:1px solid var(--line);border-radius:11px;padding:13px;border-left:3px solid var(--amber)}}
.sh{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}.num{{font-weight:800;color:var(--muted);font-size:.82rem}}
.b{{font-size:9px;font-weight:800;padding:2px 7px;border-radius:10px;letter-spacing:.4px}}
.b.new{{background:rgba(124,156,255,.16);color:var(--blue)}} .b.rec{{background:rgba(52,211,153,.15);color:var(--green)}}
.st{{color:var(--text);font-weight:700;font-size:.95rem;line-height:1.25}}
.meta{{display:flex;justify-content:space-between;align-items:center;margin-top:8px}}
.vol{{color:var(--amber);font-weight:800;font-size:.85rem;font-variant-numeric:tabular-nums}}.kd{{color:var(--muted);font-size:.78rem}}
.note{{background:var(--surface);border-left:3px solid var(--green);border-radius:0 10px 10px 0;padding:14px 18px;margin-top:16px;font-size:.95rem}}.note b{{color:var(--text)}}
@media(max-width:860px){{.grid{{grid-template-columns:1fr 1fr}}.cards{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<header><div class="wrap">
<div class="eyebrow">The service-business hub · by what they search, not who they are</div>
<h1>AI Receptionist &amp; Lead Capture — the Caleb silo.</h1>
<p class="lead">This is the "service business" hub, built around the features service owners actually search. The demand is bigger than any other hub on the site — and almost all of it is brand-new ground you never targeted.</p>
<div class="cards">
<div class="c"><div class="n">~15k</div><div class="l">monthly searches in this cluster</div></div>
<div class="c"><div class="n">KD 0-18</div><div class="l">winnable across the board</div></div>
<div class="c"><div class="n">12 / 15</div><div class="l">spokes are NEW (the gap)</div></div>
<div class="c"><div class="n">3</div><div class="l">recover from killed GHL pages</div></div>
</div></div></header>
<section><div class="wrap">
<div class="pillarbox">
  <div class="tier">TIER 1 · PILLAR PAGE</div>
  <h2>{pillar['title']}</h2>
  <span class="kw">target: {pillar['kw']}</span>
  <div class="vol">{pillar['vol']} · KD {pillar['kd']} · content speaks to contractors, salons, clinics — GoHighLevel Voice AI as the solution</div>
</div>
<div class="stem"></div>
<div class="tier2lbl">TIER 2 · 15 VARIATION SPOKES (each its own keyword)</div>
<div class="grid">{cards}</div>
<div class="note"><b>Why this is the find of the project:</b> "ai receptionist" alone is 5,400/mo at KD 11 — bigger and easier than "gohighlevel agency" (313) or anything in the old firehose. Service owners never search "gohighlevel for service business" (~0); they search "ai receptionist" and "missed-call text-back". This silo captures them. <b>Affiliate angle:</b> each page recommends GoHighLevel's Voice AI as the tool, with the trial CTA. It's a comparison/solution play (vs Smith.ai, Ruby, RingCentral), not a branded page.</div>
</div></section>
</body></html>'''
open('/Users/kerapassante/Documents/ghl-receptionist-silo.html','w').write(out)
print("wrote ghl-receptionist-silo.html")
