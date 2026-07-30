#!/usr/bin/env python3
"""
assemble_spoke.py — assemble a multi-section markdown draft (research vault) into
a publishable posts/{slug}.json for build.py.

Extracts the prose under each section's "## Draft" heading, drops editorial
commentary + frontmatter + image/figure refs, converts the (simple) markdown to
HTML, special-cases the affiliate CTA blockquote, appends a truthful EEAT bio
box (byline: William Welch — no fabricated numbers), and writes the post JSON.

Usage: python3 assemble_spoke.py <manifest.json>
Manifest: {slug,title,description,category,language,tags,publishedAt,topic,
           sections:[paths in order], hub_slug (optional),
           hub_title (optional hub anchor text; required with hub_slug for non-es),
           affiliate}
NO images are emitted (per decision 2026-06-22: ship text-only, add images later).
"""
import json, os, re, sys, html as _html
from urllib.parse import urlparse

AFFILIATE_DEFAULT = "https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog"

# headings that mark the START of trailing editorial commentary (cut content here)
COMMENTARY_H = re.compile(r'^##\s+(Verified claims|Mismatch|Dropped|Register correction|'
                          r'Codex|Provenance|Word count|Cost|Notes?|User arbitration|'
                          r'Third.voice|Claim ledger|v1\s*[→>-]|v2 changes|BLOCKING|WARN|'
                          r'NIT\b|Other v2|Status\b|changes \(codex|Register correction)', re.I)
# standalone editorial lines to drop anywhere in the draft body
EDITORIAL_LINE = re.compile(r'^\s*(\*\*(Ready for|Codex|Word count|Cost summary|Draft for|v2 changes)'
                            r'|>\s*\*\*v\d|<!--|TODO|PLACEHOLDER)', re.I)
IMG_LINE = re.compile(r'(!\[|<figure|</figure|<img|\*\(imagen|\*\(captura|\[IMAGEN|\[CAPTURA)', re.I)

DROPPED_LINKS = []  # unknown-scheme links stripped by inline(); reported in main()


def inline(t):
    t = _html.escape(t, quote=False)
    # links [text](url) -> anchor; external gohighlevel/affiliate get target+rel
    def _a(m):
        txt, url = m.group(1), m.group(2)
        url = _html.unescape(url)  # t was already escaped; avoid &amp;amp;-class doubles
        if not re.match(r'^(https?://|mailto:|/(?!/)|#)', url, re.I):
            DROPPED_LINKS.append(url)
            return txt  # unknown scheme (javascript:, //protocol-relative) — keep text
        host = (urlparse(url).hostname or '').lower()
        internal = (not host) or host == 'globalhighlevel.com' or host.endswith('.globalhighlevel.com')
        rel = '' if internal else ' target="_blank" rel="nofollow noopener"'
        return f'<a href="{_html.escape(url, quote=True)}"{rel}>{txt}</a>'
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _a, t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    return t

def section_body(path):
    raw = open(path, encoding='utf-8').read()
    # strip YAML frontmatter
    raw = re.sub(r'^---\n.*?\n---\n', '', raw, flags=re.S)
    lines = raw.split('\n')
    # find the "## Draft" content start
    start = None
    for i, ln in enumerate(lines):
        if re.match(r'^##\s+Draft', ln, re.I):
            start = i + 1
            break
    if start is None:
        return ''
    body = []
    for ln in lines[start:]:
        if COMMENTARY_H.match(ln):
            break
        if ln.strip() == '---':            # editorial separators
            continue
        if EDITORIAL_LINE.match(ln):
            continue
        if IMG_LINE.search(ln):            # drop image/figure refs (no images yet)
            continue
        body.append(ln)
    return '\n'.join(body).strip()

def md_to_html(md, affiliate, lang='es'):
    out = []
    lines = md.split('\n')
    para, bq, ul, ol, tbl = [], [], [], [], []
    def flush_p():
        if para:
            out.append('<p>' + inline(' '.join(para).strip()) + '</p>'); para.clear()
    def flush_ul():
        if ul:
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in ul) + '</ul>'); ul.clear()
    def flush_ol():
        if ol:
            items = []
            for text, subs in ol:
                sub = ('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in subs) + '</ul>') if subs else ''
                items.append(f'<li>{inline(text)}{sub}</li>')
            out.append('<ol>' + ''.join(items) + '</ol>'); ol.clear()
    def flush_tbl():
        if not tbl: return
        rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in tbl]
        # drop only the canonical GFM separator (row 2); later all-dash rows are data
        def _sep(r): return all(re.fullmatch(r'[\s:-]*', c) for c in r)
        if len(rows) > 1 and _sep(rows[1]):
            rows.pop(1)
        while rows and _sep(rows[0]):   # a separator can't be a header
            rows.pop(0)
        if rows:
            head = '<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr>'
            body = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
                           for r in rows[1:])
            out.append(f'<div style="overflow-x:auto"><table><thead>{head}</thead>'
                       f'<tbody>{body}</tbody></table></div>')
        tbl.clear()
    def flush_bq():
        if not bq: return
        joined = '\n'.join(bq)
        if 'fp_ref=' in joined:            # the affiliate CTA blockquote -> CTA box
            m = re.search(r'\[([^\]]+)\]\((https?://[^)]*fp_ref=[^)]+)\)', joined)
            label = m.group(1) if m else CTA_FALLBACK.get(lang, CTA_FALLBACK['en'])
            url = m.group(2) if m else affiliate
            heading = ''
            hm = re.search(r'##\s*\*\*([^*]+)\*\*', joined)
            if hm: heading = f'<p class="cta-h">{inline(hm.group(1))}</p>'
            tail = re.sub(r'>\s*#{0,3}\s*\*\*[^*]+\*\*', '', joined)
            tail = re.sub(r'\[[^\]]+\]\([^)]+\)', '', tail)
            tail = re.sub(r'^[>\s]+', '', tail, flags=re.M).strip()
            tailp = f'<p>{inline(tail)}</p>' if tail else ''
            out.append(f'<div class="cta-box">{heading}<p><a class="cta-btn" href="{_html.escape(url, quote=True)}" '
                       f'target="_blank" rel="nofollow noopener">{inline(label)} →</a></p>{tailp}</div>')
        else:
            txt = ' '.join(re.sub(r'^[>\s]+', '', b) for b in bq if b.strip())
            out.append(f'<blockquote><p>{inline(txt)}</p></blockquote>')
        bq.clear()
    for ln in lines:
        s = ln.strip()
        if s.startswith('>'):
            flush_p(); flush_ul(); flush_ol(); flush_tbl(); bq.append(ln); continue
        else:
            flush_bq()
        if s.startswith('|'):
            flush_p(); flush_ul(); flush_ol(); tbl.append(s); continue
        else:
            flush_tbl()
        if not s:
            flush_p(); flush_ul(); flush_ol(); continue
        if s.startswith('#### '):
            flush_p(); flush_ul(); flush_ol(); out.append(f'<h3>{inline(s[5:])}</h3>'); continue
        if s.startswith('### '):
            flush_p(); flush_ul(); flush_ol(); out.append(f'<h2>{inline(s[4:])}</h2>'); continue
        if s.startswith('## '):
            flush_p(); flush_ul(); flush_ol(); out.append(f'<h2>{inline(s[3:])}</h2>'); continue
        if re.match(r'^\d+\.\s+', s):
            flush_p(); flush_ul(); ol.append([re.sub(r'^\d+\.\s+', '', s), []]); continue
        if re.match(r'^[-*]\s+', s):
            flush_p()
            item = re.sub(r'^[-*]\s+', '', s)
            # nested only when the source line was indented under an open ol;
            # an unindented bullet after a numbered list is a new top-level ul
            if ol and re.match(r'^\s+[-*]', ln):
                ol[-1][1].append(item)
            else:
                flush_ol()
                ul.append(item)
            continue
        if not para and (ul or ol):    # text after a list closes it (keep order)
            flush_ul(); flush_ol()
        para.append(s)
    flush_p(); flush_ul(); flush_ol(); flush_bq(); flush_tbl()
    return '\n'.join(out)

BIO_ES = ('<section class="author-bio"><h2>Sobre el autor</h2>'
          '<p><strong>William Welch</strong> es consultor de GoHighLevel y fundador de Amplifi '
          'Technologies, una agencia digital enfocada en automatización de marketing con GoHighLevel '
          '. No opero agencias dentro de LATAM y soy afiliado de HighLevel.</p>'
          '<p>Esta guía se basa en investigación documentada: 38 fuentes verificadas, 8 revisiones '
          'independientes con Codex/GPT-5 y capturas reales de la interfaz en español de mayo de 2026. '
          'Si detectas algún dato que necesite actualización, escríbeme a '
          '<a href="mailto:bill@reiamplifi.com">bill@reiamplifi.com</a>.</p></section>')

BIO_EN = ('<section class="author-bio"><h2>About the author</h2>'
          '<p><strong>William Welch</strong> is a GoHighLevel consultant and the founder of Amplifi '
          'Technologies, a digital agency focused on marketing automation on GoHighLevel.</p>'
          '<p>Every price and limit in this guide was re-verified against GoHighLevel\'s official '
          'help documentation and public ideas board on the date shown in the article. '
          'If you spot a figure that needs updating, email me at '
          '<a href="mailto:bill@reiamplifi.com">bill@reiamplifi.com</a>.</p>'
          '<p><strong>Disclosure:</strong> GoHighLevel links on this page are affiliate links. '
          'If you sign up through them, I earn a recurring commission — about 40% of '
          'GoHighLevel\'s monthly plan fee, for as long as you stay subscribed. That commission '
          'is based on the plan you choose, not how much you use it, so I don\'t earn more when '
          'your usage or bill goes up. The costs, the limits, and the "who should not buy this" '
          'guidance are kept honest anyway.</p></section>')

BIOS = {'es': BIO_ES, 'en': BIO_EN}

CTA_FALLBACK = {'es': 'Empieza tu prueba gratis de 30 días',
                'en': 'Start your 30-day free trial'}

HUB_LABEL = {'es': 'Parte de la guía', 'en': 'Part of the guide'}

def main():
    DROPPED_LINKS.clear()
    man = json.load(open(sys.argv[1], encoding='utf-8'))
    aff = man.get('affiliate', AFFILIATE_DEFAULT)
    lang = man['language'][:2]
    parts = []
    for sec in man['sections']:
        body = section_body(sec)
        if body:
            parts.append(md_to_html(body, aff, lang))
    bio = BIOS.get(lang, BIO_EN)
    htmlc = '\n'.join(parts) + '\n' + bio
    # hub interlink (hub-and-spoke): link up to the hub if provided
    if man.get('hub_slug'):
        label = HUB_LABEL.get(lang, HUB_LABEL['en'])
        title = man.get('hub_title')
        if not title:
            if lang != 'es':
                raise SystemExit("hub_slug requires hub_title for non-es manifests")
            title = 'GoHighLevel en Latinoamérica'   # legacy es-spoke default
        htmlc = (f'<p class="hub-link">{label}: '
                 f'<a href="/blog/{_html.escape(man["hub_slug"], quote=True)}/">'
                 f'{_html.escape(title, quote=False)}</a></p>\n' + htmlc)
    post = {
        "title": man["title"], "slug": man["slug"], "description": man["description"],
        "html_content": htmlc, "category": man["category"], "tags": man["tags"],
        "language": man["language"], "publishedAt": man["publishedAt"],
        "author": "William Welch", "translations": man.get("translations", {}),
        "topic": man.get("topic", ""),
    }
    outp = man["out"]
    if os.path.exists(outp):
        print(f"  WARNING: overwriting existing {outp}")
    json.dump(post, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    words = len(re.sub(r'<[^>]+>', ' ', htmlc).split())
    todos = len(re.findall(r'TODO|PLACEHOLDER|\[ungrounded', htmlc, re.I))
    imgs = len(re.findall(r'<img|<figure', htmlc))
    print(f"wrote {outp}")
    print(f"  words={words}  TODOs={todos}  images={imgs}  "
          f"affiliate_links={htmlc.count('fp_ref=')}  ctas={htmlc.count('cta-btn')}  "
          f"faqs={htmlc.count('<h3>')}  dropped_links={len(DROPPED_LINKS)}")
    for u in DROPPED_LINKS:
        print(f"  DROPPED LINK: {u}")

if __name__ == '__main__':
    main()
