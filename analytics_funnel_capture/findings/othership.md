# Othership: analytics teardown

Captured 2026-11-24 with `scripts/capture_funnel.py`: one fresh, logged-out, headless
Chromium visitor (macOS, 1440x900, en-US). Raw JSONL is in `data/` (gitignored).

## Stack seen

| Vendor | Evidence | Purpose |
|---|---|---|
| GA4 `G-WGV281F0R9` | `analytics.google.com/g/collect` | Core analytics + custom events |
| Google Ads `AW-10844902924` | `/pagead/viewthroughconversion`, `/rmkt/collect`, `/1p-user-list` | Conversion + remarketing audiences |
| LinkedIn Insight `pid=7450202` | `px.ads.linkedin.com/collect` | B2B retargeting / conversions |
| TikTok pixel | `analytics.tiktok.com` | Ad attribution |
| Microsoft Clarity | `r.clarity.ms/collect` | Session replay + heatmaps |
| Hotjar | `hotjar` requests | Session replay / heatmaps |
| Mariana Tek | `othership.marianaiframes.com` | Booking + buy widgets (iframes) |
| Heybrio | `api.heybrio.ai` | AI chat widget |
| Xplor forms | `api.prd.xplorcs.com` | Lead/contact forms |
| Perkville | localStorage `perkville.*` | Loyalty / rewards |
| EmbedReach | `api.embedreach.com` cookie `svid` | Marketing automation (inferred) |
| Shopify | `_shopify_y/_s` cookies | Online store |
| Cloudflare Turnstile | `challenges.cloudflare.com` | Bot protection on forms |

GTM cross-domain linker covers `othership.us`, `marianaiframes.com`,
`forms.prd.xplorcs.com`, `othership.brandbot-checkout.com`, so ad clicks are attributed
across marketing site -> booking widget -> checkout.

## Custom GA4 events

| Event | Fires on | Properties |
|---|---|---|
| `region_selector_viewed` | `/schedule` load | screenCategory, screenStep, platform |
| `schedule_page_viewed` | `/schedule` load | screenCategory, screenStep, platform |
| `region_selector_done_clicked` | choose a studio | locationId, locationName, regionId |
| `first_timers_page_view` | `/first-timers` | page_url |
| `buy_page_viewed` | `/memberships` (embedded buy widget) | screenCategory=Buy, locationId |
| `location_page_view` | `/flatiron` etc. | location_name, page_url |
| `scroll_depth` | `/events` | scroll_depth=75 (custom, alongside built-in 90% `scroll`) |

`screenCategory` / `screenStep` / `platform="Web Integrations"` is Mariana Tek's naming,
not Othership's own.

## Growth mechanics visible in the booking widget

- Live capacity per class ("16/20 Open").
- Five saunas on staggered 15-minute starts, so a class is always about to start.
- Started classes stay listed but lose the reserve button.
- Promo layers for a fresh visitor: top banner, "Pack Friday" modal, "GET 22% OFF" side tab.

## Observations

- `page_view` fires twice per page (same `tid` and `gtm`): double-fired tag or a
  history-change trigger.
- Google Ads fires about 2x (21 vs 11 requests) on `/buy-a-pass`.
- GA4, Ads, LinkedIn, TikTok and Hotjar all fired on first load before any cookie choice.
  Declining optional cookies in Mariana's banner did not stop GA4 afterwards. That banner may
  only govern the widget's own cookies.
- Mariana's consent modal overlays the studio buttons and blocks clicks until a choice is made.

## Not captured

- Anything past `RESERVE` (login/signup, `begin_checkout`, `purchase`): the click did nothing
  in headless mode. Try `--headed`.
- `shop.othership.us` (separate domain).
- Experiment variants and returning-visitor behaviour (single fresh visit).
- TikTok / Hotjar event names (requests logged, payloads not parsed).
- Identity linkage to logged-in Google / LinkedIn / TikTok accounts (headless profile has none).
