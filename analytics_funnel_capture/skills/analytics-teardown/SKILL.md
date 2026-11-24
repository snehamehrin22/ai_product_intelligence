---
name: analytics-teardown
description: Reverse-engineer which analytics, ad pixels and custom events a website (or iOS app) fires at each funnel step, and what it stores about the visitor. Use when the user gives a URL or app name and asks what events/tracking it fires, how its funnel is instrumented, what growth tactics or experiments it runs, or "tear down X's analytics". Drives a headless browser, never fills forms or pays.
---

# Analytics Teardown

Given a website, walk its public funnel in headless Chromium, log every analytics
request per step, and write a findings doc. You are the **navigator** (read pages, choose
clicks); the scripts are the deterministic capture layer.

Project: `/Users/snehamehrin/Desktop/ai_product_intelligence/analytics_funnel_capture`
Always `cd` there and `source .venv/bin/activate` first.

## Pre-flight (do first)
1. `ls .venv` exists; if not: `/usr/local/bin/python3.13 -m venv .venv && pip install -r requirements.txt && playwright install chromium`.
2. Test the browser, not just curl: `python scripts/inspect_page.py <url>`. If curl works but
   the page fails with `ERR_SOCKET_NOT_CONNECTED` / `ERR_QUIC_PROTOCOL_ERROR`, **ask the user
   to turn off their VPN**. Don't retry blindly.

## Workflow
1. **Recon**: `python scripts/inspect_page.py <url> --step dismiss`. Read the printed links,
   overlays and the screenshot (`data/inspect.png`). Identify the funnel: pricing/plans,
   signup, booking/schedule, checkout, app download, location/product pages.
2. **Capture**: `python scripts/capture_funnel.py <url> --step ... ` with steps
   `dismiss | decline_cookies | click:<text> | goto:<url> | scroll | wait:<s>`.
   Capture the home page, then 3-6 funnel pages. One run = one visitor session.
3. **Iterate on failures** (use `inspect_page.py --step ...` to look at the state):
   - Click does nothing: an overlay is intercepting. Look at `OVERLAYS`; use `dismiss` or
     `decline_cookies`. Print the real exception before guessing.
   - Text not found: it is probably a hidden duplicate (mobile menu) or a nav that hides on
     scroll; the script already handles both. Check iframes (booking widgets live there).
   - Same failure 3 times: stop, say what you tried, ask the user (e.g. try `--headed`).
4. **Read results**: `python scripts/show_events.py data/<file>.jsonl` for named events and
   properties; `data/<file>.storage.json` for cookie/localStorage names and lifetimes.
5. **Write** `findings/<site>.md` using the template below and show the user a short summary.
6. **Commit only if asked**, staging only `analytics_funnel_capture/` (never `data/`).

## Guardrails (non-negotiable)
- Never click "Accept all" on cookie banners; use `decline_cookies`. Never fill forms, create
  accounts, enter emails/cards, or click anything payment-like (the script refuses these).
  Stop at login/checkout walls and report them as "not captured".
- `data/` holds raw IDs and is gitignored. Findings docs contain parameter *names* and
  non-identifying values only, never client IDs, cookies' values or emails.
- Report **facts vs inference** separately. An event name shows what they measure, not that
  it works. Mark guesses ("probably", "inferred"). One fresh visitor = one experiment variant.

## Findings template (`findings/<site>.md`)
1. Header: date, tool, visitor profile (logged out, headless, OS/viewport).
2. **Stack**: vendor | evidence (host/ID) | purpose. Include cookies/localStorage vendors.
3. **Custom events**: event | fires on | properties. Note who owns the naming (vendor widget
   such as Mariana Tek vs the company).
4. **Growth mechanics visible**: promos/modals, scarcity, staggered inventory, referral,
   paywall placement. Evidence only.
5. **Instrumentation critique**: duplicate events, tracking before consent, missing events a
   funnel should have, vendor-defined names, ad-pixel weight per page.
6. **What they know about the visitor**: device/browser params, behavior, persistent IDs
   with lifetimes, session replay vendors, cross-site matching, hashed-email params (names only).
7. **Not captured**: everything past walls, other domains, variants, logged-in identity
   linkage, unparsed vendors.

## iOS apps
Same report, different capture: see `guides/ios-setup.md`. Start the proxy with
`scripts/ios_proxy.sh <app>`; the user taps through the app and you label steps with
`scripts/ios_mark.sh "<step>"` when told. Remind them to remove the proxy and the mitm
certificate profile afterwards. Pinned apps will fail; skip them.

## Known limits
- Chrome-extension network capture misses iframe traffic and resets on SPA navigation; use
  these scripts instead.
- Server-side tracking (Conversions API, server GTM) is invisible to a browser proxy.
- Event payloads that are protobuf/encrypted (e.g. Firebase) are logged by vendor only.
