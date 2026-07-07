Reading additional input from stdin...
OpenAI Codex v0.142.5
--------
workdir: /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: none
reasoning summaries: none
session id: 019f38bb-e1d3-7dd3-ae12-e9dcd82aa807
--------
user
You are a skeptical GoHighLevel expert fact-checking a draft SEO pillar. Read the draft post at posts/gohighlevel-white-label-saas-agency-guide.json (the 'html_content' field) and the verified fact sheet at ../research-vault/data/agency-plans.md. Adversarially verify every factual claim about GoHighLevel: plan prices (Starter $97 / Unlimited $297 / Agency Pro $497), sub-account caps (3/unlimited/unlimited), SaaS Mode gated to Agency Pro, rebilling-with-markup=Pro vs without-markup=Unlimited, white-label domain across plans, white-label MOBILE app tier (the draft hedges it — is that accurate?), SSO/OIDC tier, snapshots availability, and terminology (sub-accounts=locations, SaaS Configurator, custom objects via snapshots). Flag: factual errors, overstated modal verbs (certainty vs 'may'), any invented testimonial/revenue/user-count claim, and conflated product terms. Output TERSE markdown with three sections: '## BLOCKING' (must fix before publish, with the exact wrong text + the correction), '## SHOULD-FIX', and '## VERDICT' (one line: PUBLISH-SAFE or NEEDS-FIXES). Be honest — confirm what is correct, don't manufacture problems.
codex
I’ll verify against the local draft and fact sheet only, since those are the sources you specified. I’m going to read both files and then inspect the GHL claims in the HTML content.
exec
/bin/zsh -lc "sed -n '1,240p' ../research-vault/data/agency-plans.md" in /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
 succeeded in 0ms:
---
type: data
topic: agency-white-label-saas
status: populated
source: gohighlevel.com/pricing (vendor-controlled) + owner account corroboration
pull_date: 2026-07-06
---

# GoHighLevel agency plan tiers + feature gating

Vendor-controlled pricing page → tagged `[vendor-claimed]`. Owner (Bill) is on Agency Pro $497 and his account exposes SaaS Configurator + Reselling + Whitelabel (corroborates SaaS Mode = Pro tier). Publish pricing with attribution ("As of 2026, GoHighLevel lists…"), never as timeless fact, and hedge exact numbers ("at the time of writing").

| Plan | Price | Sub-accounts | Reselling / rebilling | SaaS Mode | Notes |
|---|---|---|---|---|---|
| **Starter** | $97/mo ($970/yr) | 3 | basic only | ❌ | unlimited contacts/users, core features `[vendor-claimed — ghl pricing 2026-07-06]` |
| **Unlimited** | $297/mo ($2,970/yr) | unlimited | rebill phone & email **without markup**, basic API | ❌ | `[vendor-claimed — ghl pricing 2026-07-06]` |
| **Agency Pro** | $497/mo ($4,970/yr) | unlimited | rebill **with markup**, automated sub-account creation, user/agent reporting, advanced API | ✅ | "Transforms HighLevel into your own sellable software product" `[vendor-claimed — ghl pricing 2026-07-06]`. Owner is on this tier `[verbatim — owner account 2026-07-06]` |
| **Enterprise** | custom | unlimited | full | ✅ | white-label mobile app, HIPAA, dedicated success, custom dev `[vendor-claimed — ghl pricing 2026-07-06]` |

## Feature gating (verify each in draft; codex fact-check target)
- **SaaS Mode** → Agency Pro ($497)+ `[vendor-claimed]` — corroborated by owner account.
- **Rebilling with markup** → Agency Pro; **without markup** → Unlimited `[vendor-claimed]`.
- **White-label custom domain** (app.yourbrand.com) → available across plans ("connect custom domains") `[vendor-claimed]` — corroborated: owner's Whitelabel tab shows app./link.reiamplifi.com.
- **White-label MOBILE app** → Enterprise (or paid add-on) — ⚠️ AMBIGUOUS in source (said "$497/month add-on" AND "Enterprise"). DO NOT state definitively; hedge or verify against help.gohighlevel.com before publishing. `[interpreted]`
- **SSO (OIDC)** → Enterprise-tier per owned post `how-to-set-up-sso` `[summary — owned prior post]` — verify.
- **Snapshots** → all plans `[interpreted]` — verify.

## Anti-cannibalization note
Existing ranking page `/blog/gohighlevel-pricing-plans-2026-complete-guide/` owns the "pricing" query cluster. This pillar covers pricing only as a section and LINKS to that page for full pricing — does NOT target the pricing keyword (per data/agency-gsc-cluster.md).

exec
/bin/zsh -lc 'rg --files' in /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
 succeeded in 0ms:
data/published.json
robots.txt
verify.py
scripts/test_audit_links.py
scripts/audit_links.py
scripts/ghl_capture.py
scripts/ghl_capture_lib.py
scripts/ghl_optimize_wire.py
scripts/agency-capture-plan.json
scripts/test_ghl_capture.py
scripts/test_build_links.py
lang_check.py
_redirects
images/logo.png
images/blog/gohighlevel-white-label-saas-agency-guide/reselling.png
images/blog/gohighlevel-white-label-saas-agency-guide/whitelabel.png
images/blog/gohighlevel-white-label-saas-agency-guide/snapshots.png
images/blog/gohighlevel-white-label-saas-agency-guide/saas-configurator.png
images/blog/gohighlevel-white-label-saas-agency-guide/sub-accounts.png
images/og-default.png
images/es-mx/gohighlevel-latam-pagos-agencias-1.png
images/es-mx/ghl-mercadopago-card-es.png
images/es-mx/ghl-mercadopago-config-es.png
assemble_spoke.py
posts/gohighlevel-precios-planes-2026-guia-completa.json
posts/automate-google-contacts-gohighlevel-sync.json
posts/unsolicited-sms-gohighlevel-compliance-risk.json
posts/how-to-set-up-uberall-listings-in-gohighlevel-local-seo.json
posts/how-to-launch-a-website-in-gohighlevel-pro-templates.json
posts/gohighlevel-free-trial-30-days-extended.json
posts/gohighlevel-ai-agents-automation-complete-guide.json
posts/gohighlevel-payments-complete-guide.json
posts/como-configurar-primera-automatizacion-gohighlevel-paso-a-paso.json
posts/gohighlevel-latam-pagos-agencias.json
posts/master-payment-providers-gohighlevel-complete-setup-guide.json
posts/que-es-gohighlevel-mejor-alternativa-herramientas-locales-latinoamerica.json
posts/gohighlevel-whatsapp-business-api-setup-india.json
posts/gohighlevel-opiniones-es-confiable-vale-la-pena.json
posts/how-to-reduce-spam-calls-gohighlevel-ivr-number-intelligence.json
posts/gohighlevel-mercadopago-mexico.json
posts/how-to-accept-razorpay-upi-payments-in-gohighlevel-india.json
posts/leverage-ai-pricing-updates-gohighlevel-save-more.json
posts/gohighlevel-pricing-plans-2026-complete-guide.json
posts/gohighlevel-white-label-saas-agency-guide.json
build.py
categories.json

codex
The fact sheet is readable and has the key tier notes. The JSON extraction via heredoc hit the read-only temp-file limitation, so I’m switching to direct `jq`/read-only commands.
exec
/bin/zsh -lc "jq -r '.html_content' posts/gohighlevel-white-label-saas-agency-guide.json | sed -n '1,260p'" in /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
 succeeded in 0ms:
<p>Most people meet GoHighLevel as a CRM. Agencies meet it as a business model. The difference is a set of features — white-label, sub-accounts, snapshots, SaaS Mode and rebilling — that let you stop selling your time and start selling software with your name on it.</p>

<p>I run a real agency on GoHighLevel's Agency Pro plan, with dozens of client sub-accounts under one roof. This guide is the walkthrough I wish I'd had: what each of these features actually does, which plan unlocks it, and where the setup trips people up. Every screenshot below is from my own live account (client names and private details blacked out).</p>

<p style="font-size:.9rem;color:var(--text2)"><em>Heads up: this page has affiliate links. If you start a trial through one, we may earn a commission at no extra cost to you. I only write about features I actually use.</em></p>

<h2 id="what-it-means">What "agency", "white-label" and "SaaS Mode" actually mean</h2>
<p>These three words get thrown around together, so let's separate them:</p>
<ul>
<li><strong>Agency account</strong> — the top-level GoHighLevel account you log into. It holds all your clients as <em>sub-accounts</em> and gives you agency-wide settings, billing and branding.</li>
<li><strong>White-label</strong> — replacing GoHighLevel's branding with your own: your logo, your login domain (like <code>app.youragency.com</code>), your emails. Your clients never see the words "GoHighLevel."</li>
<li><strong>SaaS Mode</strong> — the piece that turns the platform into a product you sell. You package plans, set your own prices, and GoHighLevel bills your clients on your behalf and handles account provisioning. In GoHighLevel's own words, it "transforms HighLevel into your own sellable software product."</li>
</ul>
<p>Put together: white-label makes the tool look like yours, sub-accounts keep clients separate, snapshots let you deploy fast, and SaaS Mode collects the recurring revenue. Reselling is where you take a margin on the services underneath. The rest of this guide is those pieces, one at a time.</p>

<h2 id="white-label">White-label: put your brand on GoHighLevel</h2>
<p>White-labeling starts in <strong>Settings &rarr; Company &rarr; Whitelabel</strong>. Two things matter most here: your logo and your domain.</p>
<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/whitelabel.png" alt="GoHighLevel Whitelabel settings showing the logo upload and custom domain fields" loading="lazy"><figcaption>The Whitelabel tab in my agency's Company Settings. You set the brand logo and the custom login domain here (mine are blacked out). This is what makes the platform read as your software, not GoHighLevel's.</figcaption></figure>
<p>The <strong>domain</strong> step is the one that trips people up. Out of the box, clients log in at a GoHighLevel URL. To rebrand it, you point a subdomain you own — something like <code>app.youragency.com</code> — at GoHighLevel with a CNAME record, then set it as your Whitelabel Domain. Until that DNS record resolves, the field will reject the domain, so set the CNAME first and give it time to propagate.</p>
<p>Beyond the login screen, white-labeling extends to:</p>
<ul>
<li><strong>Emails</strong> — system notifications and shared email templates can carry your branding instead of GoHighLevel's, so client-facing messages stay on-brand.</li>
<li><strong>In-app banners</strong> — GoHighLevel pushes feature announcements into every sub-account. From Agency Settings you can review and disable banners so your clients' dashboards stay clean and don't advertise the platform underneath.</li>
<li><strong>The mobile app</strong> — a fully branded iOS/Android app (your name in the App Store) is a higher-tier feature. GoHighLevel offers it as a paid add-on / on the Enterprise plan rather than on the standard Agency Pro plan, so check current pricing before you promise a client an app store listing.</li>
</ul>
<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">See the white-label features on a 30-day trial &rarr;</a></p>

<h2 id="sub-accounts">Sub-accounts: one account per client</h2>
<p>A <strong>sub-account</strong> (GoHighLevel also calls these "locations") is a self-contained workspace for a single client — their contacts, funnels, calendars and conversations, walled off from every other client. You manage them all from <strong>Sub-Accounts</strong> in the agency menu.</p>
<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/sub-accounts.png" alt="GoHighLevel Sub-Accounts screen with the Create Sub-Account button" loading="lazy"><figcaption>The Sub-Accounts screen — every client gets their own isolated workspace. The list is filtered empty here so no client names show; the Create Sub-Account button (top right) is where each new client starts.</figcaption></figure>
<p>How many sub-accounts you get depends on your plan: the <strong>Starter</strong> plan caps you at 3, while <strong>Unlimited</strong> and <strong>Agency Pro</strong> are unlimited. If you're planning to grow past a few clients, you'll be on Unlimited or Pro quickly.</p>
<p>One habit worth building early: <strong>a naming convention</strong>. When you're managing dozens of accounts, "Client Business Name — City" beats whatever default a new sub-account inherits. On SaaS plans you can even standardize sub-account naming at creation so you're not renaming every account after onboarding. It sounds trivial until you're scrolling a long list looking for one client.</p>

<h2 id="snapshots">Snapshots: build once, clone forever</h2>
<p>If sub-accounts are the biggest reason to run an agency on GoHighLevel, <strong>snapshots</strong> are the reason it scales. A snapshot is a saved template of an entire account setup — funnels, workflows, pipelines, custom fields, calendars — that you can load into a brand-new sub-account in one step.</p>
<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/snapshots.png" alt="GoHighLevel Account Snapshots screen listing saved snapshots with versions and dates" loading="lazy"><figcaption>My Account Snapshots library (client names blacked out). Each row is a reusable account template. Instead of rebuilding a client from scratch, you load a snapshot and the whole setup clones over.</figcaption></figure>
<p>The workflow that saves the most time:</p>
<ol>
<li>Build one account exactly how a certain type of client should be set up.</li>
<li>Save it as a snapshot (from Account Snapshots &rarr; Create new snapshot).</li>
<li>Load that snapshot into every new sub-account of that type.</li>
</ol>
<p>A few things worth knowing before you lean on them:</p>
<ul>
<li><strong>Custom objects</strong> and their field schemas can be carried across accounts via snapshots, so a complex data model doesn't have to be rebuilt per client.</li>
<li>Snapshots have <strong>version history</strong> — you can track what was added, removed or synced between versions, which matters when a team is editing the master template and you need to know who changed what.</li>
<li>A snapshot is a copy taken at a moment in time. Updating the master snapshot doesn't automatically rewrite accounts you already deployed unless you push the update — plan your changes deliberately.</li>
</ul>

<h2 id="saas-mode">SaaS Mode: turn GoHighLevel into your own software</h2>
<p><strong>SaaS Mode</strong> is where an agency becomes a software company. Instead of billing clients for your time, you package the platform into plans, set your prices, and GoHighLevel handles provisioning and billing under your brand. You configure all of it in the <strong>SaaS Configurator</strong>.</p>
<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/saas-configurator.png" alt="GoHighLevel SaaS Configurator Plans and pricing tab showing a monthly and annual plan" loading="lazy"><figcaption>The SaaS Configurator on my account — this is where you build the plans you sell. That's a real plan of mine: a monthly and annual price your clients check out against. GoHighLevel provisions the sub-account automatically when they pay.</figcaption></figure>
<p>The important detail: <strong>SaaS Mode is an Agency Pro ($497/mo) feature</strong>. It isn't on Starter or Unlimited. That's the plan I'm on, and it's the tier you need if selling GoHighLevel as your own product is the goal. Once it's on, you can:</p>
<ul>
<li>Build plans with your own monthly/annual pricing and a free-trial period.</li>
<li>Have new sub-accounts <strong>created automatically</strong> when a customer subscribes — no manual provisioning.</li>
<li><strong>Bulk-activate SaaS</strong> across many existing sub-accounts at once instead of switching each one over by hand.</li>
</ul>
<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">SaaS Mode lives on Agency Pro — start a trial &rarr;</a></p>

<h2 id="reselling">Reselling &amp; rebilling: where your margin comes from</h2>
<p>SaaS Mode sells the platform. <strong>Rebilling</strong> is how you take a margin on the usage underneath it — the phone, email, AI and app costs your clients run up.</p>
<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/reselling.png" alt="GoHighLevel Reselling screen showing markup pricing tiers for services" loading="lazy"><figcaption>The Reselling screen. You set a markup on GoHighLevel's wholesale rates (the example shows a client price above the HighLevel price, with the difference as your profit). Multiply that across every sub-account and it becomes real recurring revenue.</figcaption></figure>
<p>The mechanics come down to markup:</p>
<ul>
<li><strong>Rebilling with markup</strong> — reselling phone, email and AI usage above cost — is an <strong>Agency Pro</strong> feature. The <strong>Unlimited</strong> plan lets you rebill phone and email but <em>without</em> a markup, so you break even rather than profit on usage.</li>
<li>You can also <strong>resell usage-based marketplace apps</strong>, adding your margin on third-party tools your clients install.</li>
<li>Giving clients <strong>in-app cancellation</strong> of their reselling subscriptions removes you as the manual middleman on every downgrade — worth turning on once you're past a handful of accounts.</li>
</ul>

<h2 id="pricing">What it costs: the agency plans</h2>
<p>As of 2026, GoHighLevel lists four tiers. Prices and exact feature gating change, so treat this as a map and confirm the current details on GoHighLevel's pricing page:</p>
<ul>
<li><strong>Starter — $97/mo.</strong> Up to 3 sub-accounts, unlimited contacts and users, core features. Basic reselling only. Good for testing the waters or running one or two clients.</li>
<li><strong>Unlimited — $297/mo.</strong> Unlimited sub-accounts, rebill phone &amp; email (no markup), basic API. The step you take when client count grows.</li>
<li><strong>Agency Pro — $497/mo.</strong> Everything in Unlimited plus <strong>SaaS Mode</strong>, automated sub-account creation, rebilling <em>with</em> markup, and user/agent reporting. This is the plan if you want to sell GoHighLevel as your own SaaS. It's the one I run.</li>
<li><strong>Enterprise — custom.</strong> Adds the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support.</li>
</ul>
<p>For a full plan-by-plan breakdown, see our <a href="/blog/gohighlevel-pricing-plans-2026-complete-guide/">complete GoHighLevel pricing guide</a>. The tier that pays for itself is whichever one matches how many clients you'll actually run and whether you're selling plans or just managing accounts.</p>

<h2 id="running-it">Running the agency: onboarding, access and revenue</h2>
<p>A few operational features round out the picture once you're past setup:</p>
<ul>
<li><strong>Agency LaunchPad</strong> — a guided, video-based onboarding flow that walks you through account configuration, client structure and automations. It's the fastest way to get a new agency productive instead of poking at settings blindly.</li>
<li><strong>SSO (Single Sign-On)</strong> — for teams, GoHighLevel supports OIDC-based single sign-on so staff log in through one identity provider instead of juggling separate passwords. It's an upper-tier / Enterprise capability, so check eligibility before you plan around it.</li>
<li><strong>Revenue tracking</strong> — the Agency Dashboard and payments widgets pull client payments, subscription fees and product sales into one view, so you can actually see where your money comes from instead of stitching it together from exports.</li>
</ul>

<h2 id="is-it-worth-it">Is GoHighLevel legit — and worth it for an agency?</h2>
<p>Short answer: yes, it's legitimate, and for the right agency it's one of the better bets in the market. It genuinely replaces a stack of separate tools (CRM, email, funnels, scheduling, phone) and, on Agency Pro, lets you resell all of it under your own brand. I run my agency on it, which is the most honest endorsement I can give.</p>
<p>Where it's <em>not</em> the right fit, so you go in clear-eyed:</p>
<ul>
<li>If you only need a simple CRM for your own business, the Starter plan's agency machinery is overkill.</li>
<li>The platform is broad, which means a learning curve. Snapshots and LaunchPad blunt it, but budget real setup time.</li>
<li>SaaS Mode only pays off if you're actually going to sell plans. Paying $497/mo for features you won't use isn't a deal.</li>
</ul>
<p>If your plan is to build recurring revenue by selling software rather than hours, that's exactly what the agency and SaaS features are built for.</p>
<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">Try it free for 30 days and see if it fits &rarr;</a></p>

<h2 id="faq">Frequently asked questions</h2>
<h3>What is SaaS Mode in GoHighLevel?</h3>
<p>SaaS Mode lets you package GoHighLevel into plans you sell under your own brand. You set the pricing, GoHighLevel bills your clients and provisions their sub-accounts automatically. It's available on the Agency Pro plan.</p>
<h3>Is GoHighLevel a SaaS?</h3>
<p>GoHighLevel is itself a SaaS product, and through SaaS Mode it lets <em>you</em> resell it as your own SaaS — you become the software vendor to your clients while GoHighLevel runs the infrastructure.</p>
<h3>How do you set up SaaS Mode in GHL?</h3>
<p>On the Agency Pro plan, open the SaaS Configurator, build your plans (monthly/annual pricing and any trial), connect your payment processor, then activate SaaS on the sub-accounts you want to sell. New subscribers get a sub-account created automatically.</p>
<h3>What is a GoHighLevel agency account?</h3>
<p>It's the top-level account that holds all your clients as sub-accounts and gives you agency-wide branding, billing and settings. It's how one login manages many client workspaces.</p>
<h3>What does it mean to resell GoHighLevel?</h3>
<p>Reselling means selling GoHighLevel to clients under your own brand and taking a margin — either by charging for plans (SaaS Mode) or by marking up the phone, email, AI and app usage they consume (rebilling). Rebilling with a markup is an Agency Pro feature.</p>
<h3>How much does a GoHighLevel agency plan cost?</h3>
<p>As of 2026, GoHighLevel lists Starter at $97/mo (3 sub-accounts), Unlimited at $297/mo (unlimited sub-accounts), and Agency Pro at $497/mo (SaaS Mode plus rebilling with markup), with a custom Enterprise tier above that. Confirm current pricing on GoHighLevel's site.</p>
<h3>Is GoHighLevel legit?</h3>
<p>Yes. It's an established platform used by thousands of agencies to run and resell marketing services. Whether it's right for you depends on whether you'll use the agency and SaaS features — for a solo CRM need it's more than you require.</p>

exec
/bin/zsh -lc "jq -r '.html_content' posts/gohighlevel-white-label-saas-agency-guide.json | rg -n \"\\"'$97|'"\\"'$297|'"\\"'$497|Starter|Unlimited|Agency Pro|Enterprise|SaaS|rebill|markup|white.label|mobile app|SSO|OIDC|snapshot|sub.account|location|custom object|Configurator|testimonial|revenue|client|user|million|thousand|'"\\bmay\\b|\\bcan\\b|\\bwill\\b|\\bmust\\b\"" in /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
 succeeded in 0ms:
1:<p>Most people meet GoHighLevel as a CRM. Agencies meet it as a business model. The difference is a set of features — white-label, sub-accounts, snapshots, SaaS Mode and rebilling — that let you stop selling your time and start selling software with your name on it.</p>
3:<p>I run a real agency on GoHighLevel's Agency Pro plan, with dozens of client sub-accounts under one roof. This guide is the walkthrough I wish I'd had: what each of these features actually does, which plan unlocks it, and where the setup trips people up. Every screenshot below is from my own live account (client names and private details blacked out).</p>
5:<p style="font-size:.9rem;color:var(--text2)"><em>Heads up: this page has affiliate links. If you start a trial through one, we may earn a commission at no extra cost to you. I only write about features I actually use.</em></p>
7:<h2 id="what-it-means">What "agency", "white-label" and "SaaS Mode" actually mean</h2>
10:<li><strong>Agency account</strong> — the top-level GoHighLevel account you log into. It holds all your clients as <em>sub-accounts</em> and gives you agency-wide settings, billing and branding.</li>
11:<li><strong>White-label</strong> — replacing GoHighLevel's branding with your own: your logo, your login domain (like <code>app.youragency.com</code>), your emails. Your clients never see the words "GoHighLevel."</li>
12:<li><strong>SaaS Mode</strong> — the piece that turns the platform into a product you sell. You package plans, set your own prices, and GoHighLevel bills your clients on your behalf and handles account provisioning. In GoHighLevel's own words, it "transforms HighLevel into your own sellable software product."</li>
14:<p>Put together: white-label makes the tool look like yours, sub-accounts keep clients separate, snapshots let you deploy fast, and SaaS Mode collects the recurring revenue. Reselling is where you take a margin on the services underneath. The rest of this guide is those pieces, one at a time.</p>
16:<h2 id="white-label">White-label: put your brand on GoHighLevel</h2>
18:<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/whitelabel.png" alt="GoHighLevel Whitelabel settings showing the logo upload and custom domain fields" loading="lazy"><figcaption>The Whitelabel tab in my agency's Company Settings. You set the brand logo and the custom login domain here (mine are blacked out). This is what makes the platform read as your software, not GoHighLevel's.</figcaption></figure>
19:<p>The <strong>domain</strong> step is the one that trips people up. Out of the box, clients log in at a GoHighLevel URL. To rebrand it, you point a subdomain you own — something like <code>app.youragency.com</code> — at GoHighLevel with a CNAME record, then set it as your Whitelabel Domain. Until that DNS record resolves, the field will reject the domain, so set the CNAME first and give it time to propagate.</p>
20:<p>Beyond the login screen, white-labeling extends to:</p>
22:<li><strong>Emails</strong> — system notifications and shared email templates can carry your branding instead of GoHighLevel's, so client-facing messages stay on-brand.</li>
23:<li><strong>In-app banners</strong> — GoHighLevel pushes feature announcements into every sub-account. From Agency Settings you can review and disable banners so your clients' dashboards stay clean and don't advertise the platform underneath.</li>
24:<li><strong>The mobile app</strong> — a fully branded iOS/Android app (your name in the App Store) is a higher-tier feature. GoHighLevel offers it as a paid add-on / on the Enterprise plan rather than on the standard Agency Pro plan, so check current pricing before you promise a client an app store listing.</li>
26:<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">See the white-label features on a 30-day trial &rarr;</a></p>
28:<h2 id="sub-accounts">Sub-accounts: one account per client</h2>
29:<p>A <strong>sub-account</strong> (GoHighLevel also calls these "locations") is a self-contained workspace for a single client — their contacts, funnels, calendars and conversations, walled off from every other client. You manage them all from <strong>Sub-Accounts</strong> in the agency menu.</p>
30:<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/sub-accounts.png" alt="GoHighLevel Sub-Accounts screen with the Create Sub-Account button" loading="lazy"><figcaption>The Sub-Accounts screen — every client gets their own isolated workspace. The list is filtered empty here so no client names show; the Create Sub-Account button (top right) is where each new client starts.</figcaption></figure>
31:<p>How many sub-accounts you get depends on your plan: the <strong>Starter</strong> plan caps you at 3, while <strong>Unlimited</strong> and <strong>Agency Pro</strong> are unlimited. If you're planning to grow past a few clients, you'll be on Unlimited or Pro quickly.</p>
32:<p>One habit worth building early: <strong>a naming convention</strong>. When you're managing dozens of accounts, "Client Business Name — City" beats whatever default a new sub-account inherits. On SaaS plans you can even standardize sub-account naming at creation so you're not renaming every account after onboarding. It sounds trivial until you're scrolling a long list looking for one client.</p>
34:<h2 id="snapshots">Snapshots: build once, clone forever</h2>
35:<p>If sub-accounts are the biggest reason to run an agency on GoHighLevel, <strong>snapshots</strong> are the reason it scales. A snapshot is a saved template of an entire account setup — funnels, workflows, pipelines, custom fields, calendars — that you can load into a brand-new sub-account in one step.</p>
36:<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/snapshots.png" alt="GoHighLevel Account Snapshots screen listing saved snapshots with versions and dates" loading="lazy"><figcaption>My Account Snapshots library (client names blacked out). Each row is a reusable account template. Instead of rebuilding a client from scratch, you load a snapshot and the whole setup clones over.</figcaption></figure>
39:<li>Build one account exactly how a certain type of client should be set up.</li>
40:<li>Save it as a snapshot (from Account Snapshots &rarr; Create new snapshot).</li>
41:<li>Load that snapshot into every new sub-account of that type.</li>
45:<li><strong>Custom objects</strong> and their field schemas can be carried across accounts via snapshots, so a complex data model doesn't have to be rebuilt per client.</li>
46:<li>Snapshots have <strong>version history</strong> — you can track what was added, removed or synced between versions, which matters when a team is editing the master template and you need to know who changed what.</li>
47:<li>A snapshot is a copy taken at a moment in time. Updating the master snapshot doesn't automatically rewrite accounts you already deployed unless you push the update — plan your changes deliberately.</li>
50:<h2 id="saas-mode">SaaS Mode: turn GoHighLevel into your own software</h2>
51:<p><strong>SaaS Mode</strong> is where an agency becomes a software company. Instead of billing clients for your time, you package the platform into plans, set your prices, and GoHighLevel handles provisioning and billing under your brand. You configure all of it in the <strong>SaaS Configurator</strong>.</p>
52:<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/saas-configurator.png" alt="GoHighLevel SaaS Configurator Plans and pricing tab showing a monthly and annual plan" loading="lazy"><figcaption>The SaaS Configurator on my account — this is where you build the plans you sell. That's a real plan of mine: a monthly and annual price your clients check out against. GoHighLevel provisions the sub-account automatically when they pay.</figcaption></figure>
53:<p>The important detail: <strong>SaaS Mode is an Agency Pro ($497/mo) feature</strong>. It isn't on Starter or Unlimited. That's the plan I'm on, and it's the tier you need if selling GoHighLevel as your own product is the goal. Once it's on, you can:</p>
56:<li>Have new sub-accounts <strong>created automatically</strong> when a customer subscribes — no manual provisioning.</li>
57:<li><strong>Bulk-activate SaaS</strong> across many existing sub-accounts at once instead of switching each one over by hand.</li>
59:<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">SaaS Mode lives on Agency Pro — start a trial &rarr;</a></p>
61:<h2 id="reselling">Reselling &amp; rebilling: where your margin comes from</h2>
62:<p>SaaS Mode sells the platform. <strong>Rebilling</strong> is how you take a margin on the usage underneath it — the phone, email, AI and app costs your clients run up.</p>
63:<figure class="post-figure"><img src="/images/blog/gohighlevel-white-label-saas-agency-guide/reselling.png" alt="GoHighLevel Reselling screen showing markup pricing tiers for services" loading="lazy"><figcaption>The Reselling screen. You set a markup on GoHighLevel's wholesale rates (the example shows a client price above the HighLevel price, with the difference as your profit). Multiply that across every sub-account and it becomes real recurring revenue.</figcaption></figure>
64:<p>The mechanics come down to markup:</p>
66:<li><strong>Rebilling with markup</strong> — reselling phone, email and AI usage above cost — is an <strong>Agency Pro</strong> feature. The <strong>Unlimited</strong> plan lets you rebill phone and email but <em>without</em> a markup, so you break even rather than profit on usage.</li>
67:<li>You can also <strong>resell usage-based marketplace apps</strong>, adding your margin on third-party tools your clients install.</li>
68:<li>Giving clients <strong>in-app cancellation</strong> of their reselling subscriptions removes you as the manual middleman on every downgrade — worth turning on once you're past a handful of accounts.</li>
74:<li><strong>Starter — $97/mo.</strong> Up to 3 sub-accounts, unlimited contacts and users, core features. Basic reselling only. Good for testing the waters or running one or two clients.</li>
75:<li><strong>Unlimited — $297/mo.</strong> Unlimited sub-accounts, rebill phone &amp; email (no markup), basic API. The step you take when client count grows.</li>
76:<li><strong>Agency Pro — $497/mo.</strong> Everything in Unlimited plus <strong>SaaS Mode</strong>, automated sub-account creation, rebilling <em>with</em> markup, and user/agent reporting. This is the plan if you want to sell GoHighLevel as your own SaaS. It's the one I run.</li>
77:<li><strong>Enterprise — custom.</strong> Adds the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support.</li>
79:<p>For a full plan-by-plan breakdown, see our <a href="/blog/gohighlevel-pricing-plans-2026-complete-guide/">complete GoHighLevel pricing guide</a>. The tier that pays for itself is whichever one matches how many clients you'll actually run and whether you're selling plans or just managing accounts.</p>
81:<h2 id="running-it">Running the agency: onboarding, access and revenue</h2>
84:<li><strong>Agency LaunchPad</strong> — a guided, video-based onboarding flow that walks you through account configuration, client structure and automations. It's the fastest way to get a new agency productive instead of poking at settings blindly.</li>
85:<li><strong>SSO (Single Sign-On)</strong> — for teams, GoHighLevel supports OIDC-based single sign-on so staff log in through one identity provider instead of juggling separate passwords. It's an upper-tier / Enterprise capability, so check eligibility before you plan around it.</li>
86:<li><strong>Revenue tracking</strong> — the Agency Dashboard and payments widgets pull client payments, subscription fees and product sales into one view, so you can actually see where your money comes from instead of stitching it together from exports.</li>
90:<p>Short answer: yes, it's legitimate, and for the right agency it's one of the better bets in the market. It genuinely replaces a stack of separate tools (CRM, email, funnels, scheduling, phone) and, on Agency Pro, lets you resell all of it under your own brand. I run my agency on it, which is the most honest endorsement I can give.</p>
93:<li>If you only need a simple CRM for your own business, the Starter plan's agency machinery is overkill.</li>
95:<li>SaaS Mode only pays off if you're actually going to sell plans. Paying $497/mo for features you won't use isn't a deal.</li>
97:<p>If your plan is to build recurring revenue by selling software rather than hours, that's exactly what the agency and SaaS features are built for.</p>
98:<p class="cta-byline"><a href="https://www.gohighlevel.com/highlevel-bootcamp?fp_ref=amplifi-technologies12&utm_source=globalhighlevel&utm_medium=blog&utm_campaign=agency-white-label-pillar" target="_blank" rel="nofollow noopener">Try it free for 30 days and see if it fits &rarr;</a></p>
101:<h3>What is SaaS Mode in GoHighLevel?</h3>
102:<p>SaaS Mode lets you package GoHighLevel into plans you sell under your own brand. You set the pricing, GoHighLevel bills your clients and provisions their sub-accounts automatically. It's available on the Agency Pro plan.</p>
103:<h3>Is GoHighLevel a SaaS?</h3>
104:<p>GoHighLevel is itself a SaaS product, and through SaaS Mode it lets <em>you</em> resell it as your own SaaS — you become the software vendor to your clients while GoHighLevel runs the infrastructure.</p>
105:<h3>How do you set up SaaS Mode in GHL?</h3>
106:<p>On the Agency Pro plan, open the SaaS Configurator, build your plans (monthly/annual pricing and any trial), connect your payment processor, then activate SaaS on the sub-accounts you want to sell. New subscribers get a sub-account created automatically.</p>
108:<p>It's the top-level account that holds all your clients as sub-accounts and gives you agency-wide branding, billing and settings. It's how one login manages many client workspaces.</p>
110:<p>Reselling means selling GoHighLevel to clients under your own brand and taking a margin — either by charging for plans (SaaS Mode) or by marking up the phone, email, AI and app usage they consume (rebilling). Rebilling with a markup is an Agency Pro feature.</p>
112:<p>As of 2026, GoHighLevel lists Starter at $97/mo (3 sub-accounts), Unlimited at $297/mo (unlimited sub-accounts), and Agency Pro at $497/mo (SaaS Mode plus rebilling with markup), with a custom Enterprise tier above that. Confirm current pricing on GoHighLevel's site.</p>
114:<p>Yes. It's an established platform used by thousands of agencies to run and resell marketing services. Whether it's right for you depends on whether you'll use the agency and SaaS features — for a solo CRM need it's more than you require.</p>

exec
/bin/zsh -lc "jq -r 'keys' posts/gohighlevel-white-label-saas-agency-guide.json" in /Users/kerapassante/Projects/ghl-agency-pillar/globalhighlevel-site
 succeeded in 0ms:
[
  "author",
  "category",
  "description",
  "html_content",
  "isPillar",
  "language",
  "publishedAt",
  "slug",
  "title",
  "topic",
  "updatedAt"
]

codex
I have the relevant claim surface now. The big verified items mostly line up; the likely problems are unsupported proof/social-proof phrasing and a couple of tier claims that need softer wording because the fact sheet itself marks them ambiguous or “verify.”
codex
## BLOCKING

- Wrong/unsupported text: “It’s an established platform used by thousands of agencies to run and resell marketing services.”
  Correction: Remove the user-count claim unless separately sourced. Use: “It’s an established platform for agencies to run and resell marketing services.”

- Too definitive given fact sheet ambiguity: “Enterprise — custom. Adds the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support.”
  Correction: “Enterprise — custom. May include the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support; verify current eligibility/pricing before promising those features.”

## SHOULD-FIX

- Unsupported/possibly invented proof claim: “with dozens of client sub-accounts under one roof.”
  Correction: Fact sheet corroborates owner is on Agency Pro, not “dozens.” Use “with client sub-accounts under one roof” unless independently verified.

- Over-absolute white-label claim: “Your clients never see the words ‘GoHighLevel.’”
  Correction: “Supported client-facing surfaces can be branded with your logo/domain instead of GoHighLevel’s.”

- Potentially unsupported service scope: “the phone, email, AI and app costs your clients run up” and “reselling phone, email and AI usage above cost”
  Correction: Fact sheet explicitly verifies Unlimited rebills phone/email without markup and Pro rebills with markup. If AI/app markup is not separately verified, say “usage costs such as phone and email” or “eligible usage costs.”

- Slight terminology confusion: “On SaaS plans you can even standardize sub-account naming…”
  Correction: “When SaaS Mode is enabled…” to avoid implying multiple GHL SaaS plan tiers.

- Correct as written: Starter $97, Unlimited $297, Agency Pro $497; sub-account caps 3/unlimited/unlimited; SaaS Mode on Agency Pro; markup rebilling on Pro vs no-markup phone/email rebilling on Unlimited; mobile app hedge in the white-label section; SSO hedge in operations section; sub-accounts = locations; SaaS Configurator; custom objects via snapshots.

## VERDICT

NEEDS-FIXES
tokens used
17,281
## BLOCKING

- Wrong/unsupported text: “It’s an established platform used by thousands of agencies to run and resell marketing services.”
  Correction: Remove the user-count claim unless separately sourced. Use: “It’s an established platform for agencies to run and resell marketing services.”

- Too definitive given fact sheet ambiguity: “Enterprise — custom. Adds the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support.”
  Correction: “Enterprise — custom. May include the fully white-labeled mobile app, HIPAA compliance, SSO and dedicated support; verify current eligibility/pricing before promising those features.”

## SHOULD-FIX

- Unsupported/possibly invented proof claim: “with dozens of client sub-accounts under one roof.”
  Correction: Fact sheet corroborates owner is on Agency Pro, not “dozens.” Use “with client sub-accounts under one roof” unless independently verified.

- Over-absolute white-label claim: “Your clients never see the words ‘GoHighLevel.’”
  Correction: “Supported client-facing surfaces can be branded with your logo/domain instead of GoHighLevel’s.”

- Potentially unsupported service scope: “the phone, email, AI and app costs your clients run up” and “reselling phone, email and AI usage above cost”
  Correction: Fact sheet explicitly verifies Unlimited rebills phone/email without markup and Pro rebills with markup. If AI/app markup is not separately verified, say “usage costs such as phone and email” or “eligible usage costs.”

- Slight terminology confusion: “On SaaS plans you can even standardize sub-account naming…”
  Correction: “When SaaS Mode is enabled…” to avoid implying multiple GHL SaaS plan tiers.

- Correct as written: Starter $97, Unlimited $297, Agency Pro $497; sub-account caps 3/unlimited/unlimited; SaaS Mode on Agency Pro; markup rebilling on Pro vs no-markup phone/email rebilling on Unlimited; mobile app hedge in the white-label section; SSO hedge in operations section; sub-accounts = locations; SaaS Configurator; custom objects via snapshots.

## VERDICT

NEEDS-FIXES
