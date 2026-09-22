# Fact ledger — Spanish workflow rebuild (2026-09-22)

Nine existing Spanish posts. No new slugs. Titles unchanged.
`copiar-templates-temporizadores-gohighlevel` is not in this rebuild: it shipped in v0.3.9.0 from `plans/es-timer-rebuild-2026-07-31/fact-ledger.md`.

The research vault `WilliamCourterWelch/globalhighlevel-research-vault` is not visible to this token. Claims below were read from the HighLevel help articles on 22 September 2026. gbrain is not installed in this environment, so there is no timeline write.

## Mercado Pago — help `155000007562`, modified 10 Sep 2026

| Claim | Tag |
|---|---|
| Connect path: Payments > Integrations > Mercado Pago > Connect | verbatim (translated) |
| Production credentials (Public Key, Access Token), not test credentials, from Your integrations | verbatim (translated) |
| Webhook URL `https://backend.leadconnectorhq.com/payments/mercado-pago/webhook`, matching secret, Payment event | verbatim, with the article's own host-casing note |
| Countries live: Colombia, Argentina, Chile, Mexico, Uruguay, Peru, Brazil. Ecuador and El Salvador "to come soon" | verbatim (translated) |
| No dynamic currency conversion; price in the account currency | verbatim (translated) |
| One checkout element per page | verbatim (translated) |
| CVV-less required; without it, subscriptions, off-session, and SaaS-related billing flows may fail | verbatim (translated) |
| Card min/max in the FAQ are the Argentina Mercado Pago help figures, not a LATAM-wide dollar floor | summary |
| July 28 capture still shows the webhook secret field as optional. The 10 Sep article still requires the webhook for payment sync | capture vs article |

Flujo A stays Stripe, NMI, Authorize.net, Square. Mercado Pago on these pages is the end-customer charge. That is the v0.3.19.0 dual-statement, not a new product claim.

## WhatsApp setup — help `155000001980`, modified 16 Sep 2026

Three paths: existing app (coexistence; not Nigeria or South Africa; one number; templates only from the CRM), new number, migrate from a BSP.

## WhatsApp workflow action — help `155000003531`, modified 8 Apr 2025

Free-form inside the 24-hour window. Approved template outside it. Free Entry Point up to 72 hours at no additional cost after the customer responds. DND exists. The appointment-reminder template in the article is the documented example, not a client.

The five action names (WhatsApp, media, interactive messages, send flows, customer service window check) are what the 28 Jul 2026 capture shows. They are not a second help article.

## Payment Received — help `155000003534`, modified 15 Apr 2026

Trigger path Automation > Workflows > Start from Scratch > Payments > Payment Received. Source filters listed in the article. Payment Status = Success and = Failed. Custom values include `{{Payment Amount}}` and `{{Transaction ID}}`. Gateway-agnostic wording covers any connected gateway. The article does not name Mercado Pago inside that table. Order Submitted is V2-only. Subscription is lifecycle, not each charge.

## Error 131042 — help `155000007938`, modified 30 Jun 2026

Meta conversation billing is separate from the CRM plan. 1,000 free service conversations per month, then a payment method on the WhatsApp Business Account is required.

WhatsApp integration at $10/month is the figure in this site's English pricing guide, re-checked against HighLevel docs in August 2026 (`gohighlevel-pricing-plans-2026-complete-guide`). It is not re-fetched from a new help article in this session. The resale-price sentence that used to sit on the setup post is removed: it was not in the articles read today.

## Conversation AI Flow Builder — help `155000006515`, modified 1 Jun 2026

Path AI Agents > Conversation AI > Create Bot > Flow Based Builder. Auto Pilot, channel list, Chat Initiated only, [END] does not end the chat, action list, up to 3 custom triggers. The article does not mention Mercado Pago.

## Workflow AI Builder — help `155000006100`, modified 3 Aug 2026

Three entry points. Average generation under 30 seconds, down from about 60. Clarifying Agent asks up to three questions. Point and Edit, Chat Mode, post-generation to-do list. Beta: AI does not test the workflow. The article does not publish a 3x multiplier. The page title still says 3x; the body says the guide does not.

## Facebook and Instagram — help `155000005068` (18 Aug 2026), `155000006069` (20 Aug 2025), `155000003298` (4 Sep 2024), recipe `155000004659` (8 Apr 2025)

Settings > Integrations connect path, test from a different account, dedup behavior, Instagram DM 24-hour window, and the note that the pre-31 Aug 2024 comment-to-DM bug is closed. The Facebook comments recipe is the documented five-step example, not a client.

## Kanban and pipelines — help `155000007528` (2 Apr 2026), `155000003910`, `155000005062`, `155000001982`

Collapse, resize, double-click reset, sort fields, layout stored in the browser for that user. Pipeline create, form-submitted to Create/Update Opportunity, stage-delete moves existing opportunities. The 2 Apr Kanban article does not mention Labs. The pipelines article says the HighRise pipelines page is enabled in Sub-account > Labs. Modified dates for 155000003910, 155000005062, and 155000001982 were not in the fetch extract; the posts say "consultado", not "modificado", for those three.

## Template library — help `155000005613`, modified 13 Aug 2025

Automation > Workflows > Create Workflow > Select from Template. "In minutes" is the article's phrase. Creating your own library templates is not available. Loading one does not change existing workflows.

## Not used

No Caso Real with a name and a result. Ideas-thread vote line stays "más de 300", linked, with no new quotation. PagBank is not stated as a native provider. Conekta and PayU are named only to say the Mercado Pago article does not list them as native connectors.
