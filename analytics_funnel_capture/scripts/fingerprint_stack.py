"""Fingerprint a site's tech stack from what its pages load (hosts, generator, globals).

    python scripts/fingerprint_stack.py https://www.example.com --path /pricing --path /schedule

Prints vendors by category, unknown third-party hosts (research these), and third-party
scripts that may read form fields (read them, e.g. with curl). Saves data/<host>.stack.json.
Browser-side only: backend and server-side tooling are invisible.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.stack import is_first_party, label_host, may_read_form_fields  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_SCRIPT_CHARS = 200_000

PAGE_INFO_JS = """() => ({
  generator: (document.querySelector('meta[name=generator]') || {}).content || null,
  webflow: !!document.documentElement.getAttribute('data-wf-site'),
  shopify: !!window.Shopify,
  wordpress: !!document.querySelector('link[href*=wp-content]'),
  next: !!window.__NEXT_DATA__,
  globals: Object.keys(window).filter(k => /^(Webflow|jQuery|Shopify|Stripe|Intercom|drift|HubSpot|_hsq|klaviyo|Klaviyo|MT[A-Z]|Mindbody|rudder|Sentry|posthog|amplitude|mixpanel|analytics|fbq|ttq|gtag|dataLayer)/.test(k)).slice(0, 25)
})"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--path", action="append", default=[], help="extra paths to load, repeatable")
    args = parser.parse_args()
    site = urlparse(args.url).hostname or ""

    hosts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    scripts: dict[str, str] = {}
    info: dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        ctx.on("request", lambda r: hosts[urlparse(r.url).hostname or "?"].update([r.resource_type])
               if r.url.startswith("http") else None)

        def on_response(r):
            host = urlparse(r.url).hostname or ""
            if r.request.resource_type == "script" and not is_first_party(host, site):
                try:
                    scripts[r.url] = r.text()[:MAX_SCRIPT_CHARS]
                except Exception:  # body unavailable (redirects, aborted)
                    pass

        ctx.on("response", on_response)
        for target in [args.url] + [args.url.rstrip("/") + p for p in args.path]:
            page.goto(target, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(8000)
            info = {**info, **{k: v for k, v in page.evaluate(PAGE_INFO_JS).items() if v}}
        browser.close()

    by_cat: dict[str, dict[str, set]] = collections.defaultdict(lambda: collections.defaultdict(set))
    unknown: list[str] = []
    for host in hosts:
        if "chrome-extension" in host or is_first_party(host, site):
            continue
        label = label_host(host)
        if label:
            by_cat[label[1]][label[0]].add(host)
        else:
            unknown.append(host)

    print(f"Site: {site}   generator/platform: { {k: v for k, v in info.items() if k != 'globals'} }")
    print(f"window globals: {info.get('globals', [])}\n")
    for cat in sorted(by_cat):
        for vendor, hs in sorted(by_cat[cat].items()):
            print(f"  [{cat}] {vendor}: {', '.join(sorted(hs))}")
    print("\nUNKNOWN third-party hosts (research these):")
    for h in sorted(unknown):
        print(f"  {h}  {dict(hosts[h])}")
    suspects = [u for u, t in scripts.items() if may_read_form_fields(t)]
    print("\nThird-party scripts that may read form fields (read to confirm):")
    for u in suspects or ["(none flagged)"]:
        print(f"  {u}")

    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / f"{re.sub(r'\\W+', '_', site)}.stack.json"
    out.write_text(json.dumps({
        "site": site, "info": info,
        "vendors": {c: {v: sorted(h) for v, h in vs.items()} for c, vs in by_cat.items()},
        "unknown_hosts": sorted(unknown), "form_reading_suspects": suspects,
    }, indent=2))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
