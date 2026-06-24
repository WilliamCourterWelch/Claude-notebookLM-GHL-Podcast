import json
rows=json.load(open('/tmp/ghl_audit.json'))
from collections import Counter
silos=Counter(r['silo'] for r in rows)
tiers={k:[r for r in rows if r['tier']==k] for k in 'ABCD'}
tot_imp=sum(r['imp'] for r in rows)
withimp=sum(1 for r in rows if r['imp']>0)
def tierimp(k): return sum(r['imp'] for r in tiers[k])
# data for JS (trim html), sort by imp desc
data=sorted(rows,key=lambda x:(-x['imp'],x['tier']))
jsdata=json.dumps([{k:r[k] for k in('slug','title','silo','words','h2','imp','clk','pos','tier','lang','pub')} for r in data])
SILO_ROWS="".join(f'<div class="bar"><span class="bl">{k}</span><span class="bt" style="width:{v/254*100:.0f}%"></span><span class="bn">{v}</span></div>' for k,v in silos.most_common())
html=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GlobalHighLevel — Killed-Pages Audit (931)</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07080a;--surface:#111520;--surface2:#171c2a;--line:#222a3d;--amber:#f59e0b;--text:#eef2ff;--text2:#9aa6c4;--muted:#5b688a;--green:#34d399;--red:#fb7185;--blue:#7c9cff}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--text2);font-family:"DM Sans",system-ui,sans-serif;font-size:14px;line-height:1.5;padding-bottom:80px}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
header{{padding:44px 0 22px;border-bottom:1px solid var(--line);background:radial-gradient(800px 320px at 82% -20%,rgba(245,158,11,.10),transparent 60%)}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
h1{{color:var(--text);font-weight:800;font-size:2.3rem;letter-spacing:-1px;margin:10px 0;line-height:1.08}}
.lead{{font-size:1.05rem;color:var(--text);max-width:880px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:26px 0}}
.c{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px}}
.c .n{{font-size:1.7rem;font-weight:800;color:var(--text)}}.c .l{{font-size:.78rem;color:var(--muted);margin-top:2px}}
.c.amber .n{{color:var(--amber)}}.c.green .n{{color:var(--green)}}
section{{padding:28px 0;border-bottom:1px solid var(--line)}}
h2{{color:var(--text);font-weight:800;font-size:1.3rem;margin-bottom:6px}}
.insight{{background:var(--surface);border-left:3px solid var(--amber);border-radius:0 10px 10px 0;padding:16px 20px;margin-top:14px}}
.insight b{{color:var(--text)}}.insight.red{{border-left-color:var(--red)}}.insight.green{{border-left-color:var(--green)}}
.bar{{display:flex;align-items:center;gap:10px;margin:7px 0}}
.bl{{width:120px;font-size:.85rem;color:var(--text2);text-align:right}}
.bt{{height:18px;background:linear-gradient(90deg,var(--amber),#fbbf24);border-radius:4px;min-width:3px}}
.bn{{font-size:.8rem;color:var(--muted)}}
.tierrow{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}}
.tc{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px}}
.tc .tg{{font-weight:800;font-size:1.1rem}}.tc.A{{border-color:rgba(52,211,153,.4)}}.tc.A .tg{{color:var(--green)}}
.tc.B .tg{{color:var(--amber)}}.tc.C .tg{{color:var(--blue)}}.tc.D .tg{{color:var(--muted)}}
.tc .tn{{font-size:1.5rem;font-weight:800;color:var(--text);margin-top:6px}}.tc .td{{font-size:.8rem;color:var(--muted)}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 10px;align-items:center}}
.controls input{{background:var(--surface2);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:8px 12px;font-family:inherit;font-size:.9rem;min-width:220px}}
.fbtn{{background:var(--surface);border:1px solid var(--line);color:var(--text2);border-radius:20px;padding:6px 13px;font-size:.82rem;cursor:pointer;font-family:inherit}}
.fbtn.on{{background:var(--amber);color:#07080a;border-color:var(--amber);font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:.85rem}}
th{{text-align:left;padding:9px 10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.6px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;position:sticky;top:0;background:var(--bg)}}
th:hover{{color:var(--amber)}}
td{{padding:8px 10px;border-bottom:1px solid var(--line);color:var(--text2);vertical-align:top}}
tr:hover td{{background:var(--surface)}}
.tt{{color:var(--text);font-weight:500}}.sl{{font-family:ui-monospace,monospace;font-size:.76rem;color:var(--muted)}}
.pill{{font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px}}
.s-AGENCY{{background:rgba(124,156,255,.15);color:var(--blue)}}.s-SERVICE{{background:rgba(52,211,153,.15);color:var(--green)}}
.s-AI\\/AUTO{{background:rgba(245,158,11,.15);color:var(--amber)}}.s-SPANISH{{background:rgba(251,113,133,.13);color:var(--red)}}
.s-INDIA{{background:rgba(168,139,250,.15);color:#a88bfa}}.s-PAYMENTS{{background:var(--surface2);color:var(--text2)}}
.s-FEATURE\\/OTHER{{background:var(--surface2);color:var(--muted)}}.s-ARABIC{{background:var(--surface2);color:var(--muted)}}
.tier{{font-weight:800}}.tier.A{{color:var(--green)}}.tier.B{{color:var(--amber)}}.tier.C{{color:var(--blue)}}.tier.D{{color:var(--muted)}}
.count{{color:var(--muted);font-size:.82rem;margin-left:8px}}
</style></head><body>
<header><div class="wrap">
<div class="eyebrow">Killed-pages audit · the June 3 prune · 931 pages</div>
<h1>Everything we cut — scored against real Google demand.</h1>
<p class="lead">All 931 firehose pages removed on June 3, recovered from git and joined to 18 months of Search Console data. Sorted so the pages worth resurrecting float to the top. These were NOT thin — most are 1,300-2,700 words ranking on page 1-2. They were cut for zero affiliate clicks + being part of a 948-page mass.</p>
<div class="cards">
<div class="c"><div class="n">931</div><div class="l">pages killed (98.4% cut)</div></div>
<div class="c amber"><div class="n">{withimp}</div><div class="l">had Google impressions</div></div>
<div class="c amber"><div class="n">{tot_imp:,}</div><div class="l">total impressions thrown away</div></div>
<div class="c green"><div class="n">{len(tiers['A'])}</div><div class="l">Tier A — resurrect first</div></div>
<div class="c green"><div class="n">{tierimp('A'):,}</div><div class="l">impressions in Tier A alone</div></div>
</div></div></header>

<section><div class="wrap">
<h2>The big surprise</h2>
<div class="insight green"><b>The site's real organic demand is AI &amp; Agent Studio — and we killed all of it.</b> The top killed pages by impressions are "AI agents in GoHighLevel," "Agent Studio," and "automate workflows" (1,862 · 1,162 · 721 impressions, ranking position 9-10). That's a THIRD hub we never considered — bigger than agency or service. The two hubs I built (agency, service) are real, but AI/Automation is where Google already sends this domain traffic.</div>
<div class="insight red"><b>Service-business was barely covered.</b> Only 11 of 931 killed pages were service-business topics. So when you asked "should this be a service-business site" — the old site never actually tried that angle. Building the service hub + spokes is genuinely new ground, not a rebuild.</div>
<div class="insight"><b>Agency was the deepest silo</b> (199 pages): sub-accounts, white-label, snapshots, API/branding, agency dashboards — many ranking page 1. Strong raw material to mine for the agency hub's spokes.</div>
</div></section>

<section><div class="wrap">
<h2>Where the 931 pages went (by silo)</h2>
{SILO_ROWS}
<h2 style="margin-top:26px">Resurrect tiers</h2>
<div class="tierrow">
<div class="tc A"><div class="tg">Tier A</div><div class="tn">{len(tiers['A'])}</div><div class="td">English · fits a hub · ≥50 imp · ≥800 words. {tierimp('A'):,} impressions.</div></div>
<div class="tc B"><div class="tg">Tier B</div><div class="tn">{len(tiers['B'])}</div><div class="td">English hub fit · ≥10 imp, or any ≥80 imp. {tierimp('B'):,} impressions.</div></div>
<div class="tc C"><div class="tg">Tier C</div><div class="tn">{len(tiers['C'])}</div><div class="td">Spanish / India own-silo · ≥20 imp. {tierimp('C'):,} impressions.</div></div>
<div class="tc D"><div class="tg">Tier D</div><div class="tn">{len(tiers['D'])}</div><div class="td">Near-zero demand or off-topic. Leave dead. {tierimp('D'):,} impressions.</div></div>
</div></div></section>

<section><div class="wrap">
<h2>Every killed page <span class="count" id="cnt"></span></h2>
<div class="controls">
<input id="q" placeholder="search title / slug…" oninput="render()">
<button class="fbtn on" data-f="tier" data-v="all" onclick="setf(this)">All tiers</button>
<button class="fbtn" data-f="tier" data-v="A" onclick="setf(this)">Tier A</button>
<button class="fbtn" data-f="tier" data-v="B" onclick="setf(this)">B</button>
<button class="fbtn" data-f="tier" data-v="C" onclick="setf(this)">C</button>
<span style="width:14px"></span>
<button class="fbtn on" data-f="silo" data-v="all" onclick="setf(this)">All silos</button>
<button class="fbtn" data-f="silo" data-v="AGENCY" onclick="setf(this)">Agency</button>
<button class="fbtn" data-f="silo" data-v="SERVICE" onclick="setf(this)">Service</button>
<button class="fbtn" data-f="silo" data-v="AI/AUTO" onclick="setf(this)">AI/Auto</button>
<button class="fbtn" data-f="silo" data-v="SPANISH" onclick="setf(this)">Spanish</button>
<button class="fbtn" data-f="silo" data-v="INDIA" onclick="setf(this)">India</button>
</div>
<table><thead><tr>
<th onclick="sortby('imp')">Impressions ▼</th><th onclick="sortby('pos')">Pos</th><th onclick="sortby('clk')">Clk</th>
<th onclick="sortby('silo')">Silo</th><th onclick="sortby('tier')">Tier</th><th onclick="sortby('words')">Words</th><th onclick="sortby('title')">Page</th>
</tr></thead><tbody id="tb"></tbody></table>
</div></section>
<script>
const DATA={jsdata};
let f={{tier:'all',silo:'all'}}, sort='imp', dir=-1;
function setf(b){{f[b.dataset.f]=b.dataset.v; document.querySelectorAll('[data-f="'+b.dataset.f+'"]').forEach(x=>x.classList.remove('on')); b.classList.add('on'); render();}}
function sortby(k){{ if(sort===k) dir=-dir; else {{sort=k; dir=(k==='title'||k==='silo')?1:-1;}} render(); }}
function render(){{
 const q=document.getElementById('q').value.toLowerCase();
 let rows=DATA.filter(r=>(f.tier==='all'||r.tier===f.tier)&&(f.silo==='all'||r.silo===f.silo)&&(!q||(r.title+r.slug).toLowerCase().includes(q)));
 rows.sort((a,b)=>{{let x=a[sort],y=b[sort]; if(typeof x==='string')return dir*x.localeCompare(y); return dir*(x-y);}});
 document.getElementById('cnt').textContent=rows.length+' shown · '+rows.reduce((s,r)=>s+r.imp,0).toLocaleString()+' impressions';
 document.getElementById('tb').innerHTML=rows.map(r=>`<tr>
  <td style="font-weight:700;color:${{r.imp>=50?'var(--text)':'var(--muted)'}}">${{r.imp.toLocaleString()}}</td>
  <td>${{r.pos||'—'}}</td><td>${{r.clk||''}}</td>
  <td><span class="pill s-${{r.silo}}">${{r.silo}}</span></td>
  <td class="tier ${{r.tier}}">${{r.tier}}</td><td>${{r.words}}</td>
  <td><div class="tt">${{r.title}}</div><div class="sl">/blog/${{r.slug}}/ · ${{r.lang}} · ${{r.pub}}</div></td>
 </tr>`).join('');
}}
render();
</script></body></html>'''
open('/Users/kerapassante/Documents/ghl-killed-audit.html','w').write(html)
print("wrote ghl-killed-audit.html")
