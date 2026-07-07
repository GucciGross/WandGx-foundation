# Paint Quote PWA install prompt moved into Settings (2026-07-02)

## Trigger
Use this reference when Paint Quote / PainterQuote has a janky or aggressive browser/PWA install prompt, or when the user asks for install UX to be discoverable instead of interruptive.

## Durable lesson
For Paint Quote, do **not** show global PWA install banners/toasts that cover workspace content. Users should find install from Settings when they want it.

## Proven implementation pattern
- Keep the root `PWAInstallPrompt` mounted only to capture `beforeinstallprompt` and `appinstalled` browser events.
- Prevent the browser's automatic prompt via `event.preventDefault()` and store the deferred prompt in module state.
- Render no global banner/popup from the root component.
- Expose a Settings option such as `Settings -> Install App` that calls a shared `requestPwaInstall()` function.
- Add a General-settings shortcut if useful: `Settings -> General -> Open Install App`.
- Use `useSyncExternalStore` (or equivalent stable store snapshot) for install availability so the Settings panel can react without creating render loops.
- Avoid old localStorage-based nag/dismiss cycles such as `pwa-install-dismissed`; the goal is no nag at all.

## Verification pattern
Run focused tests for:
- PWA prompt capture does not render an automatic banner.
- `requestPwaInstall()` invokes the browser prompt only when Settings calls it.
- Settings deep link `/settings?section=install` renders install controls.
- Settings tab counts/selectors are updated when adding a new Settings section.

Recommended commands from the Paint Quote repo:

```bash
npm run test -- src/test/components/PWAInstallPrompt.test.tsx src/test/pages/Settings.test.tsx src/test/integration/settings.test.tsx --run
npm run test -- src/test/server/integrationSync.test.ts src/test/server/apiV1RateLimit.test.ts src/test/server/authProvider.test.ts --run
npm run typecheck
npm run build
```

If the broader suite previously had unrelated flakes/failures, rerun the targeted server tests after fixes, then run the full suite before final deploy when time allows.

## Production proof cues
After deploying to LXC123 (`192.168.1.183`, `/opt/apps/paint-quote`, `painterquote-web`), verify:
- `https://painter.wandgx.com/health?format=json` returns `status=healthy`, `authProvider=company-identity`, `billingEnabled=true`.
- The live JS bundle contains the Settings install copy (e.g. `will not pop up over the workspace`).
- The live bundle no longer contains `pwa-install-dismissed`.
- Browser visual/console check on `https://painter.wandgx.com/login` shows no install prompt/banner/popup and no console errors.
