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
           sections:[abs paths in order], hub_slug (optional), affiliate}
NO images are emitted (per decision 2026-06-22: ship text-only, add images later).
"""
import json, re, sys, html as _html

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

def inline(t):
    t = _html.escape(t, quote=False)
    # links [text](url) -> anchor; external gohighlevel/affiliate get target+rel
    def _a(m):
        txt, url = m.group(1), m.group(2)
        rel = ' target="_blank" rel="nofollow noopener"' if ('http' in url and 'globalhighlevel.com' not in url) else ''
        return f'<a href="{url}"{rel}>{txt}</a>'
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

def md_to_html(md, affiliate):
    out, i = [], 0
    lines = md.split('\n')
    para, bq, ul = [], [], []
    def flush_p():
        if para:
            out.append('<p>' + inline(' '.join(para).strip()) + '</p>'); para.clear()
    def flush_ul():
        if ul:
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in ul) + '</ul>'); ul.clear()
    def flush_bq():
        if not bq: return
        joined = '\n'.join(bq)
        if 'fp_ref=' in joined:            # the affiliate CTA blockquote -> CTA box
            m = re.search(r'\[([^\]]+)\]\((https?://[^)]*fp_ref=[^)]+)\)', joined)
            label = m.group(1) if m else 'Empieza tu prueba gratis de 30 días'
            url = m.group(2) if m else affiliate
            heading = ''
            hm = re.search(r'##\s*\*\*([^*]+)\*\*', joined)
            if hm: heading = f'<p class="cta-h">{inline(hm.group(1))}</p>'
            tail = re.sub(r'>\s*#{0,3}\s*\*\*[^*]+\*\*', '', joined)
            tail = re.sub(r'\[[^\]]+\]\([^)]+\)', '', tail)
            tail = re.sub(r'^[>\s]+', '', tail, flags=re.M).strip()
            tailp = f'<p>{inline(tail)}</p>' if tail else ''
            out.append(f'<div class="cta-box">{heading}<p><a class="cta-btn" href="{url}" '
                       f'target="_blank" rel="nofollow noopener">{inline(label)} →</a></p>{tailp}</div>')
        else:
            txt = ' '.join(re.sub(r'^[>\s]+', '', b) for b in bq if b.strip())
            out.append(f'<blockquote><p>{inline(txt)}</p></blockquote>')
        bq.clear()
    for ln in lines:
        s = ln.strip()
        if s.startswith('>'):
            flush_p(); flush_ul(); bq.append(ln); continue
        else:
            flush_bq()
        if not s:
            flush_p(); flush_ul(); continue
        if s.startswith('#### '):
            flush_p(); flush_ul(); out.append(f'<h3>{inline(s[5:])}</h3>'); continue
        if s.startswith('### '):
            flush_p(); flush_ul(); out.append(f'<h2>{inline(s[4:])}</h2>'); continue
        if s.startswith('## '):
            flush_p(); flush_ul(); out.append(f'<h2>{inline(s[3:])}</h2>'); continue
        if re.match(r'^[-*]\s+', s):
            flush_p(); ul.append(re.sub(r'^[-*]\s+', '', s)); continue
        para.append(s)
    flush_p(); flush_ul(); flush_bq()
    return '\n'.join(out)

BIO = ('<section class="author-bio"><h2>Sobre el autor</h2>'
       '<p><strong>William Welch</strong> es consultor de GoHighLevel y fundador de Amplifi '
       'Technologies, una agencia digital enfocada en automatización de marketing con GoHighLevel '
       'para clientes en Latinoamérica.</p>'
       '<p>Esta guía se basa en investigación documentada: 38 fuentes verificadas, 8 revisiones '
       'independientes con Codex/GPT-5 y capturas reales de la interfaz en español de mayo de 2026. '
       'Si detectas algún dato que necesite actualización, escríbeme a '
       '<a href="mailto:bill@reiamplifi.com">bill@reiamplifi.com</a>.</p></section>')

def main():
    man = json.load(open(sys.argv[1], encoding='utf-8'))
    aff = man.get('affiliate', AFFILIATE_DEFAULT)
    parts = []
    for sec in man['sections']:
        body = section_body(sec)
        if body:
            parts.append(md_to_html(body, aff))
    htmlc = '\n'.join(parts) + '\n' + BIO
    # hub interlink (hub-and-spoke): link up to the hub if provided
    if man.get('hub_slug'):
        htmlc = (f'<p class="hub-link">Parte de la guía: '
                 f'<a href="/blog/{man["hub_slug"]}/">GoHighLevel en Latinoamérica</a></p>\n' + htmlc)
    post = {
        "title": man["title"], "slug": man["slug"], "description": man["description"],
        "html_content": htmlc, "category": man["category"], "tags": man["tags"],
        "language": man["language"], "publishedAt": man["publishedAt"],
        "author": "William Welch", "translations": man.get("translations", {}),
        "topic": man.get("topic", ""),
    }
    outp = man["out"]
    json.dump(post, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    words = len(re.sub(r'<[^>]+>', ' ', htmlc).split())
    todos = len(re.findall(r'TODO|PLACEHOLDER|\[ungrounded', htmlc, re.I))
    imgs = len(re.findall(r'<img|<figure', htmlc))
    print(f"wrote {outp}")
    print(f"  words={words}  TODOs={todos}  images={imgs}  "
          f"affiliate_links={htmlc.count('fp_ref=')}  ctas={htmlc.count('cta-btn')}  faqs={htmlc.count('<h3>')}")

if __name__ == '__main__':
    main()
