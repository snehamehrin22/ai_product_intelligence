# analytics_funnel_capture

Drive a website's funnel in headless Chromium and log every analytics request
(GA4, Google Ads, Meta, TikTok, LinkedIn, Clarity, Hotjar, Segment, PostHog...)
with the funnel step that triggered it. Used to reverse-engineer growth tactics
from the events a product fires.

## Usage

```bash
source .venv/bin/activate
python scripts/capture_funnel.py https://www.othership.us \
    --step dismiss --step scroll --step "click:Book a Class" --step "wait:10"
```

Steps: `goto:<url>` | `click:<visible text>` | `scroll` | `dismiss` | `wait:<s>`.
Output: `data/<host>_<timestamp>.jsonl` (gitignored) plus a per-step summary.
Clicks refuse payment-like text; the script never fills forms.

## Layout

- `src/funnel_capture/vendors.py` - classify requests, parse event names/props
- `src/funnel_capture/recorder.py` - context-level listener (captures iframes)
- `scripts/capture_funnel.py` - CLI
- `scripts/show_events.py` - print named events + properties from a capture
- `findings/` - written teardowns per site (`othership.md`)
- `tests/` - `pytest tests`

Steps also include `decline_cookies` (opens Manage Settings, unticks optional
cookies, saves; never accepts all).

## Bugs Found & Lessons Learned

- **VPN breaks Playwright browsers.** Every page failed with
  `ERR_SOCKET_NOT_CONNECTED` (bundled Chromium) / `ERR_QUIC_PROTOCOL_ERROR`
  (system Chrome) while `curl` worked. Cause: VPN on. Fix: turn it off. Lesson:
  if curl works but the browser doesn't, check VPN/proxy first.
- **Wait for `domcontentloaded`, not `load`.** Third-party tags can stall `load`.
- **`get_by_text(...).first` can pick a hidden duplicate** (mobile menu). Use
  `.filter(visible=True)`; sticky navs also hide after scrolling down.
- **Promo modals intercept clicks** on fresh sessions (e.g. Pack Friday sale
  `<dialog>`). Use the `dismiss` step before clicking. Don't swallow click
  exceptions while debugging; print them.
- **Chrome extension network capture misses iframe traffic and loses state on
  SPA navigation**; Playwright's context-level listener doesn't.
