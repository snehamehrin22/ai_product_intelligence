"""Show what's clickable on a page (every frame), so a navigator can pick next steps.

Runs optional capture_funnel-style steps first, then prints visible links/buttons per
frame, blocking overlays, and form field names (never filled). Saves a screenshot.

    python scripts/inspect_page.py https://example.com --step dismiss --step "click:Pricing"
"""
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_funnel import run_step  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

LIST_JS = """() => {
  const vis = e => e.offsetParent !== null || getComputedStyle(e).position === 'fixed';
  const clean = s => (s || '').trim().replace(/\\s+/g, ' ').slice(0, 50);
  const clicks = [...document.querySelectorAll('a[href],button,[role=button]')]
    .filter(vis).map(e => [clean(e.innerText || e.getAttribute('aria-label')), e.getAttribute('href')])
    .filter(x => x[0]);
  const forms = [...document.querySelectorAll('input,select,textarea')]
    .filter(vis).map(e => (e.type || e.tagName) + ':' + (e.name || e.id || e.placeholder || ''));
  const overlays = [...document.querySelectorAll('dialog[open],[role=dialog],[class*=modal i],[class*=cookie i],[class*=consent i]')]
    .filter(vis).map(e => clean(e.getAttribute('aria-label') || e.className || e.tagName));
  return {clicks: clicks.slice(0, 60), forms: forms.slice(0, 20), overlays: overlays.slice(0, 6)};
}"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--step", action="append", default=[])
    parser.add_argument("--shot", type=Path, default=DATA_DIR / "inspect.png")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)
        for step in args.step:
            print(f"-> {step}")
            run_step(page, step)
            page.wait_for_timeout(3000)
        print(f"\nURL: {page.url}")
        for frame in page.frames:
            if not frame.url.startswith("http"):
                continue
            try:
                info = frame.evaluate(LIST_JS)
            except Exception:
                continue
            if not (info["clicks"] or info["forms"] or info["overlays"]):
                continue
            print(f"\n[frame] {frame.url[:100]}")
            if info["overlays"]:
                print("  OVERLAYS (may block clicks):", info["overlays"])
            for text, href in info["clicks"]:
                print(f"  click: {text}" + (f"  -> {href[:70]}" if href else ""))
            if info["forms"]:
                print("  form fields (not filled):", info["forms"])
        args.shot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(args.shot))
        print(f"\nscreenshot: {args.shot}")
        browser.close()


if __name__ == "__main__":
    main()
