import json,glob,re,os
audit=json.load(open('/tmp/ghl_audit.json'))   # 931 killed, has imp/clk/pos/silo/lang
GSC="/Users/kerapassante/.claude/projects/-Users-kerapassante/35499a86-8a1d-4dfa-8b4c-1cea08ea7054/tool-results/mcp-gsc-search_analytics-1782315899407.txt"
gsc={}
for r in json.load(open(GSC))['rows']:
    m=re.search(r'/blog/([^/]+)/?$',r['keys'][0])
    if m: gsc[m.group(1)]={'imp':r['impressions'],'clk':r['clicks'],'pos':round(r['position'],1)}
# add kept (live) pages
kept=[]
for f in glob.glob('/Users/kerapassante/Projects/Claude-notebookLM-GHL-Podcast/globalhighlevel-site/posts/*.json'):
    d=json.load(open(f)); slug=d.get('slug') or os.path.basename(f)[:-5]
    g=gsc.get(slug,{})
    kept.append(dict(slug=slug,title=d.get('title',''),lang=d.get('language','en'),
        imp=g.get('imp',0),clk=g.get('clk',0),pos=g.get('pos',0),live=True))
for a in audit: a['live']=False
pages=audit+kept

# fine-grained PILLAR classifier (ordered; first match wins)
def lang_of(p): 
    l=(p.get('lang') or 'en'); return l
def pillar(p):
    l=lang_of(p)
    if l.startswith('es'): return ('LANG: Spanish / LATAM','lang')
    if l=='ar': return ('LANG: Arabic','lang')
    s=(p['slug']+' '+(p.get('title') or '')).lower()
    if re.search(r'india|razorpay|upi|lakh|mena|hindi|\bindian\b',s): return ('GEO: India','geo')
    rules=[
      (r'voice-ai|voice ai','Voice AI','topic'),
      (r'conversation-ai|convo-ai|chat-widget|chatbot|flow-builder|conversation ai','Conversation AI & Chatbots','topic'),
      (r'agent-studio|ai-agent|ai agents|ask-ai|ai-employee|ai studio|build-ai','AI Agents & Agent Studio','topic'),
      (r'saas|white.?label|whitelabel|reseller|sub-account|sub account|snapshot|app-installer|resell|agency-dashboard|agency dashboard|prospect','Agency, White-Label & SaaS','persona'),
      (r'workflow|automat|trigger|cross-object|bulk-add|premium-features','Workflows & Automation','topic'),
      (r'webhook|\bapi\b|apis|mcp-server|integration|sdk|app-store','APIs, Webhooks & Integrations','topic'),
      (r'payment|stripe|mercadopago|invoice|checkout|shipping|coupon|order','Payments & Checkout','topic'),
      (r'calendar|booking|appointment|schedul','Calendars & Booking','topic'),
      (r'custom-object|custom object|custom-dispositions|associate-companies|company-based','Custom Objects & Data','topic'),
      (r'contact|smart-list|advanced-filter|\bcrm\b|pipeline|\blead','Contacts & CRM','topic'),
      (r'form|survey','Forms & Surveys','topic'),
      (r'website|funnel|\bpage|template|global-section|\bdomain|launch','Websites, Funnels & Pages','topic'),
      (r'email|\bsms\b|a2p|whatsapp|messaging|mobile-dnd|unsolicited|inbound','Email, SMS & Messaging','topic'),
      (r'review|reputation|listing|uberall|gbp|local-seo|seo-tool|seo-in','Reviews, Listings & Local SEO','topic'),
      (r'spam-call|\bivr\b|\bcall|number-intelligence|disposition|audio-response','Calls & Phone','topic'),
      (r'pricing|promo|discount|\bcost','Pricing','topic'),
      (r'service-business|contractor|hvac|plumb|salon|rental|service-appointment|service-booking|service','Service Businesses','persona'),
      (r'free-trial|30-day|free trial','Free Trial','money'),
    ]
    for pat,name,typ in rules:
        if re.search(pat,s): return (name,typ)
    return ('Other / Misc','topic')

from collections import defaultdict
P=defaultdict(lambda:{'pages':[],'type':'topic'})
for p in pages:
    name,typ=pillar(p)
    P[name]['type']=typ
    P[name]['pages'].append(p)

pillars=[]
for name,d in P.items():
    pg=sorted(d['pages'],key=lambda x:-x.get('imp',0))
    pillars.append(dict(name=name,type=d['type'],n=len(pg),
        imp=sum(x.get('imp',0) for x in pg),clk=sum(x.get('clk',0) for x in pg),
        live=sum(1 for x in pg if x.get('live')),pages=pg))
pillars.sort(key=lambda x:-x['imp'])
json.dump(pillars,open('/tmp/ghl_pillars.json','w'))
print(f"{len(pillars)} pillars from {len(pages)} pages")
print(f"{'PILLAR':38} {'type':8} {'pages':>5} {'imp':>7} {'live':>4}")
for p in pillars:
    print(f"{p['name'][:37]:38} {p['type']:8} {p['n']:5} {p['imp']:7} {p['live']:4}")
