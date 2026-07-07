# WandGx GTM media packet workflow — 2026-07-03

Use this when the user asks whether the WandGx ecosystem is GTM-approved and then wants a media packet for socials, website, email, text, images, and video.

## Scope control

- If the user excludes a product, keep it out of the product/media lanes completely.
- Still report excluded-product leakage if it appears on an in-scope public landing page because campaign traffic would see it.
- For this session: Paint Quote / PainterQuote / paint.wandgx.com was excluded. It was not audited or used in copy/assets, but current `wandgx.com` homepage leakage was reported as a GTM blocker.

## Order of operations

1. Load `wandgx-ecosystem` and media-relevant skills before acting.
2. Run read-only GTM checks first:
   - public route health,
   - visible auth/register entry points,
   - public copy hygiene,
   - excluded-product leakage,
   - pilot/waitlist/request-access language,
   - unsafe claims such as self-serve billing or unproven integrations.
3. Launch background lanes when possible:
   - WandGx vNext public builder,
   - Oracle/Chat/shared platform,
   - SET,
   - media packet planning.
4. Decide `GTM approved`, `GTM blocked`, or `GTM conditional/hold` before generating final-post copy.
5. If not clean-approved, still produce a **draft-ready safe-claim packet** only when claims avoid the blockers, and label it as hold until cleanup.
6. Generate assets only after claim safety is known.
7. Verify artifacts: image QA, video render probe, checksums/manifest, and searchable blocker report.

## GTM blockers found in the session

Initial audit findings:

- `/register`, `/signup`, and `/sign-up` on WandGx loaded the build shell but did not open Create Account mode; Register toggles in the build shell also did not switch reliably. Treat this as a conversion blocker for campaigns using raw account routes.
- `wandgx.com` homepage exposed excluded-product copy/links even though that product was excluded from the campaign. Treat excluded-product leakage as a campaign-path blocker.
- SET public CTAs used `Book a pilot`. For GA/release-now positioning, replace pilot-only CTA language with `Start workspace`, `See demo`, `Talk to us`, or another launch-safe CTA.
- `api.trainwithset.com/` returned 404 while docs/OpenAPI/bridge health were alive. Do not use API root as SET proof unless a health/root route exists.

Follow-up clearance pattern from the same session:

- A campaign can move from `blocked` to **controlled GTM approved** when a verified campaign path works even if generic deep links still need polish. In this session, the safe campaign paths were `https://wandgx.com/` and `https://wandgx.com/app?intent=signup#account-auth-tab-signup`; the latter opened a visible Create account modal with Name, Email, Password, and Create account button.
- Keep **raw route/header auth issues** as a remaining blocker: `/register`, `/signup`, `/sign-up`, and top-nav Register should open the same visible auth surface before using those exact URLs in paid/social/email CTAs.
- Do not create real accounts without owner approval. Label disposable signup/sign-in/build proof as still pending if no approved test mailbox was provided.
- If SET CTA/copy is patched and redeployed, verify both container health and public pages. In this session `set-frontend-1` was healthy and public SET pages showed launch-safe `Talk to us`/workspace language with no `Book a pilot` CTA.

## Safe media-packet claim set

Use:

- WandGx is available now.
- Build the app your work keeps asking for.
- Start with one workflow.
- Move from prompt to app path with preview and proof steps.
- WandGx Chat helps clarify next actions.
- SET turns changing documents, SOPs, and workflows into training paths, practice, checks, and readiness insight.
- The ecosystem connects apps, chat, training, account, access, and operations.

Avoid unless proven and in scope:

- excluded-product specifics,
- self-serve Stripe/card top-up,
- instant/guaranteed production apps,
- every build auto-hosted,
- live third-party sync,
- automatic Oracle-to-SET packet creation without durable IDs/material URLs,
- internal tools, providers, models, workers, or agent names.

## Asset production pattern

- Generate raw visual concepts with the requested image model/provider when available.
- Avoid relying on generated images for exact marketing text. Use deterministic overlays for final spelled text.
- QA generated/final cards for: spelling, readable contrast, no gradients if banned, no purple/indigo, no chat bubbles, no internal names, no excluded-product leakage.
- For Hyperframes video, `npm run check` must be clean for lint, validate, and inspect/layout before final delivery. If inspect reports overlap warnings, adjust HTML/CSS, re-run check, re-render the MP4, regenerate email GIF/preview frames, then regenerate manifest/checksums/zip.
- Hyperframes render output may land in `video/hyperframes/renders/`; copy the latest rendered MP4 back to the packet’s stable delivery path before checksumming/zipping.
- For email, convert MP4 to a small GIF preview and note that real campaign sends require hosted absolute URLs and unsubscribe/sender details.
- Bundle the packet with `MEDIA_PACKET.md`, blocker report, social/website/email/SMS copy, assets, video, source, `asset-manifest.json`, and checksums.

## Recommended final labels

Use one of these status shapes, matching the evidence:

- `GTM status: blocked` — account conversion, public route, or claim-safety failure prevents campaign traffic.
- `Controlled GTM status: approved` — a verified campaign path is usable and materials are safe, but generic/deep-link/self-serve proof gaps remain.
- `Full clean self-serve GTM status: conditional` — visible forms exist but disposable account creation/sign-in/build proof was not run.
- `Packet status: launch-usable for a controlled campaign path` — when copy/assets avoid unproven claims and the CTA path is verified.
- `Packet status: draft-ready / Final-post hold` — when cleanup is still required before any public traffic.
- `No email/text/social post was sent` unless the user explicitly authorizes sending/posting.

When marking controlled GTM approved, include the exact allowed links and exact forbidden links. Example: allow `wandgx.com/` and `wandgx.com/app?intent=signup#account-auth-tab-signup`; forbid raw `/register`, `/signup`, `/sign-up` until they auto-open the same auth surface.