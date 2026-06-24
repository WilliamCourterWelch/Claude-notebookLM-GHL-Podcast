import json,re,html
pillars=json.load(open('/tmp/ghl_pillars.json'))
uni=json.load(open('/Users/kerapassante/Projects/seo-ops-agent/runs/keyword-universe/ghl-pillars-universe.json'))['rows']
kdov=json.load(open('/Users/kerapassante/Projects/seo-ops-agent/runs/keywords/ghl-pillar-heads-kd.json'))
def findrows(d):
    if isinstance(d,dict):
        for k,v in d.items():
            if isinstance(v,list) and v and isinstance(v[0],dict) and 'keyword' in v[0]: return v
        for v in d.values():
            r=findrows(v); 
            if r: return r
    return None
ov=findrows(kdov)
kd={r['keyword']:{'kd':r.get('difficulty'),'vol':r.get('volume_clickstream') or r.get('volume_ads') or 0} for r in ov}
# classify a keyword to a pillar (same rules as clustering)
def kw_pillar(s):
    s=s.lower()
    rules=[(r'voice ai','Voice AI'),(r'conversation ai|chatbot|chat widget','Conversation AI & Chatbots'),
      (r'agent studio|ai agent|ai agents|ask ai|ai studio','AI Agents & Agent Studio'),
      (r'saas|white label|whitelabel|reseller|sub-account|sub account|snapshot|agenc','Agency, White-Label & SaaS'),
      (r'report|analytic|dashboard','Reporting & Analytics'),(r'social|content|qr','Social, Content & QR'),
      (r'mobile app|app store|marketplace','Mobile App & Marketplace'),(r'workflow|automat|trigger','Workflows & Automation'),
      (r'webhook|\bapi|integration|sdk','APIs, Webhooks & Integrations'),(r'payment|stripe|invoice|checkout','Payments & Checkout'),
      (r'calendar|booking|appointment','Calendars & Booking'),(r'custom object','Custom Objects & Data'),
      (r'crm|contact|smart list|pipeline|lead','Contacts & CRM'),(r'form|survey','Forms & Surveys'),
      (r'website|funnel|page|template|domain','Websites, Funnels & Pages'),(r'email|sms|a2p|whatsapp|messag','Email, SMS & Messaging'),
      (r'review|reputation|listing','Reviews, Listings & Local SEO'),(r'call|ivr|phone|number','Calls & Phone'),
      (r'pricing|price|cost|promo','Pricing'),(r'service business|small business','Service Businesses')]
    for pat,name in rules:
        if re.search(pat,s): return name
    return None
# attach universe keywords to pillars
ukw={}
for r in uni:
    p=kw_pillar(r['keyword'])
    if p: ukw.setdefault(p,[]).append(r)
# head term + KD per pillar (best matching overview keyword)
HEAD={'AI Agents & Agent Studio':'gohighlevel ai agents','Workflows & Automation':'gohighlevel workflows',
 'Reporting & Analytics':'gohighlevel reporting','Agency, White-Label & SaaS':'gohighlevel agency','Pricing':'gohighlevel pricing',
 'Contacts & CRM':'gohighlevel crm','Email, SMS & Messaging':'gohighlevel sms','Payments & Checkout':'gohighlevel payments',
 'APIs, Webhooks & Integrations':'gohighlevel api','Calendars & Booking':'gohighlevel calendar','Calls & Phone':'gohighlevel voice ai',
 'Websites, Funnels & Pages':'gohighlevel funnels','Conversation AI & Chatbots':'gohighlevel conversation ai','Voice AI':'gohighlevel voice ai',
 'Forms & Surveys':'gohighlevel forms','Custom Objects & Data':'gohighlevel custom objects','Reviews, Listings & Local SEO':'gohighlevel reviews',
 'Service Businesses':'gohighlevel for service business','Mobile App & Marketplace':'gohighlevel mobile app','Social, Content & QR':'gohighlevel social media'}
TC={'topic':'#7c9cff','persona':'#34d399','lang':'#fb7185','geo':'#a88bfa','money':'#f59e0b'}
def kdbadge(v):
    if v is None: return '<span class="kd" style="background:var(--surface2);color:var(--muted)">KD ?</span>'
    c='#34d399' if v<=10 else ('#f59e0b' if v<=25 else '#fb7185')
    return f'<span class="kd" style="background:{c}22;color:{c}">KD {v}</span>'
def card(p):
    if p['type'] in('lang','geo'): return ''
    clr=TC.get(p['type'],'#7c9cff')
    head=HEAD.get(p['name'])
    hk=kd.get(head,{}) if head else {}
    kw=sorted(ukw.get(p['name'],[]),key=lambda x:-(x.get('volume') or 0))[:6]
    existing_slugs=set(x['slug'] for x in p['pages'])
    kwli=''.join(f'<li><span class="vol">{r.get("volume",0):,}</span><span class="kw">{html.escape(r["keyword"])}</span></li>' for r in kw) or '<li class="none">no new keyword data</li>'
    sp=p['pages'][:5]
    spli=''.join(f'<li><span class="imp">{s.get("imp",0)}</span><span class="sl">{html.escape((s.get("slug") or "")[:40])}</span>{" ●" if s.get("live") else ""}</li>' for s in sp)
    return f'''<div class="pillar" style="border-top:3px solid {clr}">
      <div class="ph">{kdbadge(hk.get('kd'))}<span class="pages">{p['n']} pages · {p['imp']:,} imp{" · "+str(p['live'])+" live" if p['live'] else ""}</span></div>
      <h3>{html.escape(p['name'])}</h3>
      <div class="head">head: <b>{html.escape(head or '')}</b></div>
      <div class="cols">
        <div><div class="clbl">Recovered spokes (GSC imp)</div><ul class="rec">{spli}</ul></div>
        <div><div class="clbl">Keyword gaps (DataForSEO vol)</div><ul class="gap">{kwli}</ul></div>
      </div>
    </div>'''
eng=[p for p in pillars if p['type'] in('topic','persona','money')]
cards=''.join(card(p) for p in eng)
total_vol=sum(r.get('volume',0) for r in uni)
out=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GoHighLevel — Master Topical Map (data-complete)</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#07080a;--surface:#111520;--surface2:#171c2a;--line:#222a3d;--amber:#f59e0b;--text:#eef2ff;--text2:#9aa6c4;--muted:#5b688a;--green:#34d399;--blue:#7c9cff}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--text2);font-family:"DM Sans",system-ui,sans-serif;font-size:13.5px;line-height:1.45;padding-bottom:80px}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
.eyebrow{{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--amber);font-weight:700}}
h1{{color:var(--text);font-weight:800;font-size:2.1rem;letter-spacing:-1px;margin:10px 0;line-height:1.1}}
.lead{{font-size:1.04rem;color:var(--text);max-width:900px}}
header{{padding:42px 0 22px;border-bottom:1px solid var(--line);background:radial-gradient(800px 320px at 82% -20%,rgba(245,158,11,.10),transparent 60%)}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}
.c{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}}.c .n{{font-size:1.4rem;font-weight:800;color:var(--text)}}.c .l{{font-size:.74rem;color:var(--muted)}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;font-size:.8rem}}.legend span{{display:inline-flex;gap:6px;align-items:center}}
.dot{{width:11px;height:11px;border-radius:3px}}
.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:13px;margin-top:18px}}
.pillar{{background:#0c0f16;border:1px solid var(--line);border-radius:12px;padding:15px}}
.ph{{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}}
.kd{{font-size:11px;font-weight:800;padding:2px 9px;border-radius:20px}}
.pages{{font-size:.76rem;color:var(--muted)}}
.pillar h3{{color:var(--text);font-size:1.12rem;font-weight:800}}
.head{{font-size:.8rem;color:var(--muted);margin:2px 0 10px}}.head b{{color:var(--amber);font-family:ui-monospace,monospace;font-size:.8rem}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.clbl{{font-size:9.5px;text-transform:uppercase;letter-spacing:.6px;font-weight:700;color:var(--muted);margin-bottom:5px}}
ul{{list-style:none;display:flex;flex-direction:column;gap:3px}}
li{{display:flex;gap:7px;align-items:baseline;font-size:.78rem}}
.imp{{color:var(--green);font-weight:700;min-width:30px;text-align:right;font-variant-numeric:tabular-nums}}
.vol{{color:var(--amber);font-weight:700;min-width:38px;text-align:right;font-variant-numeric:tabular-nums}}
.sl{{font-family:ui-monospace,monospace;font-size:.68rem;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.kw{{color:var(--text2)}}.none{{color:var(--muted);font-style:italic}}
.note{{background:var(--surface);border-left:3px solid var(--amber);border-radius:0 10px 10px 0;padding:14px 18px;margin-top:18px;font-size:.95rem}}.note b{{color:var(--text)}}
@media(max-width:880px){{.grid{{grid-template-columns:1fr}}.cards{{grid-template-columns:1fr 1fr}}}}
</style></head><body>
<header><div class="wrap">
<div class="eyebrow">Master topical map · pages + GSC + DataForSEO · the boil-the-lake blueprint</div>
<h1>Every pillar, with real demand AND difficulty.</h1>
<p class="lead">The complete Caleb structure, data-backed on three axes: the pages you already have, the Google impressions they pull (GSC), and the search volume + difficulty for the gaps (DataForSEO, $0.28 live pull). Green KD = easy win, amber = moderate, red = hard.</p>
<div class="cards">
<div class="c"><div class="n">{len(eng)}</div><div class="l">English pillars</div></div>
<div class="c"><div class="n">167</div><div class="l">keywords w/ volume (DataForSEO)</div></div>
<div class="c"><div class="n">{total_vol:,}</div><div class="l">monthly searches mapped</div></div>
<div class="c"><div class="n">KD 0-17</div><div class="l">most pillars — winnable</div></div>
</div>
<div class="legend"><span><span class="dot" style="background:#34d399"></span>KD ≤10 easy</span><span><span class="dot" style="background:#f59e0b"></span>KD 11-25 moderate</span><span><span class="dot" style="background:#fb7185"></span>KD 26+ hard</span><span><span class="dot" style="background:#34d399"></span>● = live page</span></div>
</div></header>
<section style="padding:24px 0"><div class="wrap">
<div class="grid">{cards}</div>
<div class="note"><b>Read it like this:</b> each pillar shows its head-term difficulty (KD badge), how many pages + impressions you already have, the recovered spokes (left, GSC impressions), and the keyword gaps worth adding (right, DataForSEO volume). <b>Build order = high impressions × low KD first.</b> AI Agents (KD 6), Workflows (KD 2), Reporting (KD 0), Pricing (KD 5) are loud-demand + easy. Agency (KD 36) is the one hard pillar — but it's your highest-value money term, so it's worth the fight (your "don't dodge hard keywords" call, proven).</div>
</div></section>
</body></html>'''
open('/Users/kerapassante/Documents/ghl-master-map.html','w').write(out)
print("wrote ghl-master-map.html ·",len(eng),"English pillars rendered")
