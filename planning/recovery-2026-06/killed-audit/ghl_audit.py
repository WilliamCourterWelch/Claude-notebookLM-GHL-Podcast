import json,glob,re,os
GSC="/Users/kerapassante/.claude/projects/-Users-kerapassante/35499a86-8a1d-4dfa-8b4c-1cea08ea7054/tool-results/mcp-gsc-search_analytics-1782315899407.txt"
gsc={}
for r in json.load(open(GSC))['rows']:
    u=r['keys'][0]
    m=re.search(r'/blog/([^/]+)/?$',u)
    if m: gsc[m.group(1)]={'imp':r['impressions'],'clk':r['clicks'],'pos':round(r['position'],1)}
# kept slugs (don't re-audit those)
kept=set()
for f in glob.glob('/Users/kerapassante/Projects/Claude-notebookLM-GHL-Podcast/globalhighlevel-site/posts/*.json'):
    kept.add(os.path.basename(f)[:-5])

def silo(slug,topic,lang,title):
    s=(slug+' '+topic+' '+title).lower()
    if lang and lang.startswith('es'): return 'SPANISH'
    if lang in('ar',): return 'ARABIC'
    if re.search(r'india|razorpay|upi|lakh|mena|hindi|indian',s): return 'INDIA'
    if re.search(r'agenc|saas|white.?label|sub-account|reseller|snapshot|mrr|scale',s): return 'AGENCY'
    if re.search(r'service|contractor|hvac|plumb|salon|gym|clinic|dentist|real.?estate|missed.?call|receptionist|booking|review|local-seo|gbp|listing',s): return 'SERVICE'
    if re.search(r'voice-ai|ai-agent|agent-studio|ai agents|automat|workflow',s): return 'AI/AUTO'
    if re.search(r'payment|stripe|mercadopago|invoice|checkout',s): return 'PAYMENTS'
    return 'FEATURE/OTHER'

rows=[]
for f in glob.glob('/tmp/ghl-killed/globalhighlevel-site/posts/*.json'):
    d=json.load(open(f)); slug=d.get('slug') or os.path.basename(f)[:-5]
    if slug in kept: continue
    b=d.get('html_content','') or ''
    words=len(re.sub(r'<[^>]+>',' ',b).split())
    h2=len(re.findall(r'<h2',b))
    lang=d.get('language','en'); topic=d.get('topic','') or d.get('category','')
    g=gsc.get(slug,{}); imp=g.get('imp',0); clk=g.get('clk',0); pos=g.get('pos',0)
    sl=silo(slug,topic,lang,d.get('title',''))
    eng = lang in ('en','en-US','') or lang.startswith('en')
    # resurrect tiering
    hubfit = sl in ('AGENCY','SERVICE','AI/AUTO')
    if eng and hubfit and imp>=50 and words>=800: tier='A'
    elif eng and hubfit and imp>=10: tier='B'
    elif sl in('SPANISH','INDIA') and imp>=20: tier='C'
    elif imp>=80: tier='B'
    else: tier='D'
    rows.append(dict(slug=slug,title=d.get('title',''),words=words,h2=h2,lang=lang,
        topic=topic,silo=sl,imp=imp,clk=clk,pos=pos,tier=tier,pub=(d.get('publishedAt') or '')[:10]))
json.dump(rows,open('/tmp/ghl_audit.json','w'))
# summary
from collections import Counter
print("TOTAL killed audited:",len(rows))
print("\nBy silo:")
for k,v in Counter(r['silo'] for r in rows).most_common(): print(f"  {k:14} {v}")
print("\nBy resurrect tier:")
for k in 'ABCD':
    t=[r for r in rows if r['tier']==k]
    ti=sum(r['imp'] for r in t)
    print(f"  Tier {k}: {len(t):4} pages | {ti} total impressions")
print("\nWith ANY Google impressions:",sum(1 for r in rows if r['imp']>0),"/",len(rows))
print("Total impressions across all killed:",sum(r['imp'] for r in rows))
print("\n=== TIER A (resurrect first) ===")
for r in sorted([r for r in rows if r['tier']=='A'],key=lambda x:-x['imp']):
    print(f"  {r['imp']:5} imp  pos{r['pos']:>4}  {r['silo']:9} {r['words']:4}w  {r['slug'][:60]}")
