# AI Booking Bots — expand the Flow Builder page

**Status: implementing 2026-09-24.** No new URL. Host title and H1 stay `GoHighLevel Conversation AI Flow Builder, No Code`.

| | |
|---|---|
| URL | `https://globalhighlevel.com/blog/master-conversation-ai-flow-builder-gohighlevel-complete-setup/` |
| File | `globalhighlevel-site/posts/master-conversation-ai-flow-builder-gohighlevel-complete-setup.json` |
| Episode | Transistor `968aa4ab` (share `/s/`, embed `/e/`) and YouTube `y_eFDPg1wrE` (unlisted, `youtube-nocookie` embed) |
| Help | Workflow action `155000003467`, modified 23 September 2026. Canvas Book Appointment stays cited to Flow Builder `155000006515`, modified 1 June 2026. |

## Decision

**Expand the existing Conversation AI Flow Builder page.** Do not publish a new HTML post.

### 1. Inventory

No live post targets the Appointment Booking Conversation AI workflow action. A body search for `booking bot` hits only `how-to-set-conversation-ai-response-styles-in-gohighlevel`, and that page uses the phrase as a response-style example ("for appointment bots, be concise"), not as setup steps.

The Flow Builder page (`articleId` `155000006515`) already has an H2, "Mastering AI Actions: Qualify, Book, and Customize," and a Book Action subsection. That subsection claimed the bot shows 3 suggested times and that you connect Google Calendar or Outlook. Those sentences are not in the Flow Builder article fetched 24 September 2026. They are replaced with the canvas facts that article does publish: the action loops until it books or the contact gives a clear exit such as "I don't want to book," you enter a prompt and select a calendar, and the branches are Appointment Booked and Appointment not booked.

The workflow action is a second surface. Flow Builder help says to use the canvas when the bot should follow a structured path inside Conversation AI, and to use the Conversation AI workflow action when a workflow should ask, wait, branch, and continue from the Workflow Builder. The episode's source article is that workflow action.

Nearby pages that are not the host:

| Page | Why it is not the host |
|---|---|
| Agent Studio build guide | Builds an agent. Title and H1 locked. Bing already concentrates AI impressions here. |
| Guided Form setup | Questionnaire that creates a Conversation AI bot. Same silo, linked, not rewritten. |
| Service Booking Triggers | Fires after a service booking exists. Same silo. The only GSC appointment URL in this pull. |
| Multi-calendar booking | Topic is CRM & Communication. A followed link from this AI page is unwrapped at render. |
| India / Arabic / Spanish Flow Builder twins | Left alone. This PR does not clone the English fold. |
| AI agents pillar (`gohighlevel-ai-agents-automation-complete-guide`, `isPillar`) | Hub copy. One same-silo sentence points at `#booking-bot`. The `/blog/` copy of a pillar strips internal links; the category hub keeps them. |

### 2. Cannibalization

A new URL would split a page that already has the Book action, and it would sit next to the Agent Studio guide that holds almost all of this cluster's Bing impressions. Bing query `gohighlevel ai automation agents platform` is 363 impressions, 0 clicks, position 4.0 (pull `2026-09-24-ghl-bing-28d`, fetched 2026-09-24T17:05:39Z). That is a CTR problem on the page Bing already shows, not a missing-URL problem.

### 3. Intent

The episode is a workflow-action how-to. The closest existing surface is the Flow Builder page's Book action, with a labeled section that keeps the canvas action and the workflow action distinct.

### 4. Demand (do not invent; absence from a capped list is not zero)

Bing Webmaster, property `ghl`, site `https://globalhighlevel.com/`, source `live`, fetched 2026-09-24T17:05:39.243965Z. Totals: 92 clicks, 7,194 impressions, ctr 0.012788434806783431, position 4.7. `top_pages` has 170 rows (the endpoint caps at 250).

| URL | impr | clicks | position |
|---|---:|---:|---:|
| `/blog/how-to-build-ai-agents-in-gohighlevel-agent-studio-guide/` | 423 | 3 | 4.0 |
| `/blog/gohighlevel-ai-studio-pricing/` | 12 | 3 | 4.3 |
| `/blog/gohighlevel-ai-employee-pricing/` | 12 | 0 | 3.5 |
| `/blog/gohighlevel-ai-agent-pricing/` | 3 | 0 | 5.7 |
| `/blog/gohighlevel-voice-ai-pricing/` | 3 | 0 | 2.0 |
| `/blog/master-multi-calendar-appointment-booking-gohighlevel/` | 3 | 0 | 3.7 |
| `/blog/master-conversation-ai-flow-builder-gohighlevel-complete-setup/` | 3 | 0 | 5.0 |
| `/blog/automate-client-support-ask-ai-agent-studio-gohighlevel/` | 2 | 0 | 6.0 |
| `/blog/how-to-use-service-booking-triggers-gohighlevel-automate-appointments/` | 1 | 0 | 4.0 |
| `/blog/gohighlevel-ai-employee-ai-receptionist-review/` | 1 | 0 | 2.0 |

Not in those 170 rows: Guided Form setup, the India Flow Builder twin, the AI Studio pages how-to, `book-across-multiple-calendars-gohighlevel-voice-ai`. That is "not in the returned set," not a measured zero.

Google Search Console, `sc-domain:globalhighlevel.com`, 28 days, window 2026-08-25 through 2026-09-21. Three files (`ghl-gsc-top` fetched 2026-09-24T17:06:36Z, `ghl-gsc-ai-broad` fetched 2026-09-24T17:06:51Z, `ghl-ai-booking-gsc` fetched 2026-09-24T17:06:34Z) agree on site totals: 0 clicks, 236 impressions, position 69.25, 16 queries, 9 pages. The broad and booking files' cluster filters return one row: query `high level appointment setting`, page `/blog/how-to-use-service-booking-triggers-gohighlevel-automate-appointments/`, 0 clicks, 1 impression, position 63. That page's own row is 0 clicks, 8 impressions, position 70.75. No GSC row in these files names Conversation AI, Agent Studio, or a booking bot.

### 5. What shipped on the host

- Text-only 5-step list (`#extractable-steps`) after the intro, before the first H2. Plain markup, because `sanitize_content` strips the `#f0f4ff` boxes.
- `#booking-bot` separates the canvas Book Appointment action from the workflow action and cites both help articles.
- Transistor embed `https://share.transistor.fm/e/968aa4ab`, share link `/s/968aa4ab`, YouTube nocookie embed `y_eFDPg1wrE`, and the watch URL. The page-level player stays `transistorEpisodeId` `1480182e` (the older Flow Builder episode).
- Two Bootcamp CTAs, both `fp_ref=amplifi-technologies12`, campaign `conversation-ai-booking-bot`, slots `utm_content=ai-booking-bots` and `utm_content=ai-booking-episode`.
- Same-silo links to Agent Studio, Guided Form, and Service Booking Triggers. Each of those pages, plus the AI pillar, links back to `#booking-bot` with its own anchor text.
- Meta description rewritten to 151 characters so the snippet names both Flow Builder and the booking-bot action. Title and H1 are unchanged. The opening section's canvas path now matches the 1 June 2026 help article (AI Agents, Conversation AI, Create Bot, Flow Based Builder). The YouTube iframe is `width="100%"` so it fits the column.
- No Meta Pixel. No homepage edit. Frozen free-trial and agency titles untouched. Agent Studio title and H1 untouched.

## Review

gstack `/review` (Dual-Cursor skill is not in this repo). No SQL, shell, or new enum. The diff is post JSON plus a render test.

Fixed in this change before commit:

- The opening section said Automations → Conversation AI, and channels "SMS, WhatsApp, email, or web chat." The 1 June 2026 Flow Builder article says AI Agents → Conversation AI → Create Bot → Flow Based Builder, and channels SMS, Facebook, Instagram, WhatsApp, and Live Chat.
- The cluster intro explained the silo rule to readers. It now says what each guide is for.
- The YouTube iframe is `width="100%"` so a 560px frame does not force horizontal scroll.
- The meta description names Flow Builder and the booking-bot action (151 characters).

Left as known legacy, not rewritten: the rest of the pre-existing Flow Builder body (canvas layout, "most agencies choose SMS and WhatsApp"). Those sentences are not in the ledger. The two legacy "no credit card" sentences stay in JSON and are rewritten at render; the built page has zero occurrences.

No shared helper. The five-step list is page copy, same shape as the Agent Studio TLDR, not a builder function.

## Not in this PR

Voice AI Outbound (`https://share.transistor.fm/s/bb4012cd`) and the earlier Appointment Booking video (`https://www.youtube.com/watch?v=n5daF3BI4F4`) are named in `PATTERN.md` for the next folds. They are not embedded here.
