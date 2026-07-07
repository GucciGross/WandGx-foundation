# WandGx and SET landing-page clarity teardown

Use this when the user asks why `wandgx.com`, `trainwithset.com`, or related GTM pages feel weak, confusing, or "bad". This is a marketing/positioning diagnostic pattern, not a code-change recipe.

## Live pages inspected in the 2026-07-06 session

- `https://wandgx.com`
  - H1: `Build software from one request. Ship with proof.`
  - Follow-on sections emphasized `Galaxy Map`, `Missions`, `Build Receipt`, `The galaxy is the system, not a backdrop`, and receipt/proof metaphors.
- `https://trainwithset.com`
  - H1: `The training layer for a world that changes every week.`
  - Positioning emphasized AI Training Operating System, changing documents/SOPs/workflows, living paths, source-backed tutor, practice, and readiness.

Both pages loaded quickly and had no obvious console errors in that pass. The diagnosis was not technical breakage; it was product-message and conversion clarity.

## Durable diagnosis

The pages feel weak when they present internal operating-system mythology before customer comprehension.

A new visitor needs to know within seconds:

1. What is this?
2. Who is it for?
3. What painful problem does it solve today?
4. What do I get if I click?
5. Can I trust it?
6. How much commitment/cost is involved?
7. Can I see the actual product or result?

If the page answers those indirectly through ecosystem terms, branded metaphors, or internal architecture, it will feel sophisticated but low-converting.

## WandGx specific pattern

Strong seed:

- `Build software from one request. Ship with proof.` is usable.

Problems to watch for:

- Too much metaphor too early: `galaxy`, `mission`, `receipt`, `surface`, `system`.
- Ecosystem introduced before the buyer understands the base offer: SET, Chat, Oracle, PainterQuote, integrations.
- Proof is asserted more than demonstrated: receipts need to look/feel like real audit trails, deployed previews, QA checks, before/after, cost/timeline, and deliverable evidence.
- Buyer target is too broad or implicit: local businesses, founders, agencies, internal teams, and enterprises should not all be left to infer fit.
- CTA uncertainty: `Start a build` needs immediate context for what happens next — form, chat, payment, quote, human review, preview, etc.

Preferred first-screen direction:

```text
Need software for your business?
Describe it once. WandGx builds the app, shows the work, and gives you proof before launch.
```

Then show concrete examples before ecosystem architecture:

```text
Booking app
Quote + deposit tool
Internal training portal
```

Each example should answer:

```text
What the customer asked for
What WandGx built
How long it took
What proof was included
What the next action is
```

Move galaxy/system architecture lower, after the visitor understands the offer.

## SET specific pattern

Problem seed:

- `The training layer for a world that changes every week` is elegant but abstract.
- `AI Training Operating System` can sound heavy/enterprise-complex before the pain is clear.

Problems to watch for:

- Category ambiguity: LMS, AI tutor, document knowledge base, enablement platform, compliance system, internal academy?
- Too many concepts in one subheadline: documents, SOPs, launches, app workflows, living paths, tutor support, practice, readiness.
- Proprietary terms before explanation: `living paths`, `source-backed tutor`, `readiness`.
- `Book a pilot` is high friction if the page has not built enough confidence.
- Use cases are too broad unless one dominant pain is highlighted first.

Preferred first-screen direction:

```text
When work changes, training breaks.
SET turns updated SOPs, docs, and workflows into training paths, AI practice, and readiness proof.
```

Then show the simplest visual flow:

```text
1. Add changed document
2. SET creates training
3. Team practices with tutor
4. Manager sees who is ready
```

Use `Book a pilot` only after proof or pair it with a lower-friction action such as `View demo workspace`, `Upload a sample SOP`, or `See what SET creates`.

## How to report this to the user

Be direct and non-defensive. The useful framing:

- The products are not doomed.
- The ideas are good.
- The sites are currently written for insiders, not buyers.
- They prove sophistication before usefulness.
- Homepage should be primitive and obvious; app surfaces can carry the richer OS feel.

Blunt summary:

```text
WandGx feels like a cool internal command center for an ecosystem.
It needs to feel like the fastest way for a business owner to get a working app without hiring a dev team.

SET feels like a strategic AI enablement platform deck.
It needs to feel like the easiest way to turn changed documents into training the team actually completes.
```

## Pitfalls

- Do not start coding when the user asks to discuss why pages are bad. First inspect live pages and give the diagnosis.
- Do not over-index on load time or console cleanliness; a technically healthy page can still fail conversion.
- Do not lead with internal product names, model names, agents, tools, or architecture. Lead with customer pain and outcome.
- Do not make the homepage explain the whole ecosystem. Use one sharp promise, one clear buyer, one believable proof path.
