# Fact ledger — Conversation AI booking bot fold

Fetched 2026-09-24. Do not add a product claim to the new section unless it is in this table.

| Claim in the new copy | Source | Fetched |
|---|---|---|
| Use Flow Builder for a structured path inside Conversation AI. Use the Conversation AI workflow action when a workflow should ask, wait, branch, and continue from the Workflow Builder. | [Conversation AI Flow Builder](https://help.gohighlevel.com/support/solutions/articles/155000006515-conversation-ai-flow-builder), modified Mon, 1 Jun 2026, 10:58 AM | 2026-09-24 |
| Canvas path: AI Agents > Conversation AI > Create Bot > Create New Bot (Flow Based Builder). | Same article | 2026-09-24 |
| Bot settings: select or deselect channels such as SMS, Facebook, Instagram, WhatsApp, and Live Chat. | Same article, "Name the bot / Set Bot Status to Auto Pilot" | 2026-09-24 |
| Book Appointment loops until it books or a clear exit such as "I don't want to book." Enter a booking prompt. Select a calendar. Branches: Appointment Booked, Appointment not booked. | Same article, section "AI Action - Book Appointment" | 2026-09-24 |
| The workflow action uses an AI conversation so the contact picks an open time on the selected calendar. Outcomes: Timeout, Appointment Was Booked, Appointment Was Not Booked. | [Workflow Action - Appointment Booking Conversation AI Booking Bot](https://help.gohighlevel.com/support/solutions/articles/155000003467-workflow-action-appointment-booking-conversation-ai-booking-bot), modified Wed, 23 Sep 2026, 7:14 AM | 2026-09-24 |
| Example trigger is Customer Replied with an SMS reply-channel filter. The article says that trigger is an example, not a requirement. | Same workflow-action article, Step 2 | 2026-09-24 |
| Action name to add: Appointment Booking Conversation AI Bot. | Same article, Step 3 | 2026-09-24 |
| Recurring calendars are not supported and do not appear in the calendar field. | Same article, Step 4 and the FAQ | 2026-09-24 |
| Personality, Additional Instructions, Maximum Messages Limit, timeout, and channel are settings on the action. Channels listed: Facebook, Instagram, SMS, WhatsApp. | Same article, Step 4 | 2026-09-24 |
| Maximum Messages Limit minimum 5, maximum 25. | Same article, Step 4 and the FAQ | 2026-09-24 |
| Timeout is no reply inside the timeout window. Appointment Was Not Booked is the message limit reached without a booking. They are different. | Same article, Step 4 and the FAQ | 2026-09-24 |
| By default the bot sends the booking confirmation. "Don't let the bot send confirmation message" leaves confirmation to the Appointment Was Booked branch. | Same article, Step 10 | 2026-09-24 |
| Wait time before responding, in seconds, lets the bot collect back-to-back messages. The article's example is "Hi" followed by "I want to book a consultation." | Same article, Step 11 | 2026-09-24 |
| Save Action adds the three branches. They are not custom branch conditions you build by hand. Then test, save, and publish. | Same article, Steps 12 and 13 | 2026-09-24 |

The published workflow-action article numbers Step 4, then Step 10, Step 11, Step 12, and Step 13. There are no Step 5 through Step 9 headings on the page fetched 2026-09-24. The on-site list collapses the published controls into five steps and does not invent the missing numbers.

Not used, on purpose:

- "3 suggested times," Google Calendar, Outlook, buffer time, and timezone conversion. Those were in the old Book Action paragraphs and are not in the 1 June 2026 Flow Builder article. Removed.
- Per-minute Voice AI rates, Agent Studio token rates, and plan prices. They stay on the pricing pages.
- Any claim about what the unlisted YouTube video shows beyond the title supplied with the episode. The page embeds it and names the workflow action. It does not narrate frames.

Help links are citations. They do not get `fp_ref`.
