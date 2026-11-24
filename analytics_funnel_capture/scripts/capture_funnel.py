"""Drive a site's funnel in Playwright and log every analytics request.

Examples:
    python scripts/capture_funnel.py https://www.othership.us \
        --step "scroll" --step "click:Book a Class" --step "wait:5"

Step grammar: goto:<url> | click:<visible text> | scroll | dismiss | decline_cookies | wait:<seconds>.
Clicks refuse payment-like text so the run never completes a purchase, and
nothing here fills forms.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.recorder import Recorder  # noqa: E402

# Never click anything that looks like it completes a payment
PAYMENT_GUARD = re.compile(r"pay|purchase|place order|complete|confirm|subscribe", re.I)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def click_by_text(page: Page, text: str) -> None:
    """Click the first visible element matching text, searching every frame."""
    if PAYMENT_GUARD.search(text):
        raise SystemExit(f"Refusing to click payment-like text: {text!r}")
    # Second pass after scrolling to top: sticky navs often hide once scrolled down
    for attempt in range(2):
        if attempt == 1:
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
        for frame in page.frames:
            # Sites often render hidden duplicates (mobile menus), so skip to the visible match
            loc = frame.get_by_text(text, exact=False).filter(visible=True).first
            try:
                loc.wait_for(state="visible", timeout=2000)
                loc.click(timeout=5000)
                return
            except Exception:
                continue
    print(f"  ! could not find clickable text {text!r}", file=sys.stderr)


def audit_storage(context: BrowserContext, page: Page, path: Path) -> None:
    """Save which cookies/localStorage keys the site set (names only, never values).

    Answers "what do they store about the visitor" without writing identifiers to disk.
    """
    now = time.time()
    cookies = [
        {
            "name": c["name"],
            "domain": c["domain"],
            "days": round((c["expires"] - now) / 86400) if c["expires"] > 0 else "session",
        }
        for c in context.cookies()
    ]
    local_keys = {}
    for frame in page.frames:
        try:
            keys = frame.evaluate("Object.keys(localStorage)")
        except Exception:  # about:blank / sandboxed frames
            continue
        if keys:
            local_keys[frame.url.split("?")[0]] = keys
    path.write_text(json.dumps({"cookies": cookies, "local_storage_keys": local_keys}, indent=2))


def decline_cookies(page: Page) -> None:
    """Open a cookie banner's Manage Settings, untick optional cookies, save.

    Never clicks "Accept all". Consent modals (e.g. Mariana Tek's) sit on top of
    the booking widget and block clicks until a choice is made, so the funnel
    can't progress without one.
    """
    for frame in page.frames:
        manage = frame.get_by_role("button", name=re.compile("manage settings", re.I)).first
        try:
            manage.wait_for(state="visible", timeout=2000)
        except Exception:
            continue
        manage.click()
        page.wait_for_timeout(800)
        for box in frame.locator("input[type=checkbox]:checked").all():
            try:
                box.uncheck(force=True, timeout=2000)
            except Exception:
                pass
        frame.get_by_role("button", name=re.compile("save settings", re.I)).first.click(timeout=3000)
        page.wait_for_timeout(1000)
        return
    print("  ! no cookie banner found", file=sys.stderr)


def run_step(page: Page, step: str) -> None:
    """Execute one step string against the page."""
    kind, _, arg = step.partition(":")
    if kind == "goto":
        page.goto(arg, wait_until="domcontentloaded", timeout=60000)
    elif kind == "click":
        click_by_text(page, arg)
    elif kind == "scroll":
        for _ in range(6):
            page.mouse.wheel(0, 900)
            page.wait_for_timeout(400)
    elif kind == "dismiss":
        # Close promo modals (they intercept clicks); Escape first, then a close button
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        close = page.locator("dialog[open] [aria-label*='lose' i], dialog[open] button:has-text('×')")
        if close.count():
            close.first.click(timeout=3000)
    elif kind == "decline_cookies":
        decline_cookies(page)
    elif kind == "wait":
        page.wait_for_timeout(int(float(arg) * 1000))
    else:
        raise SystemExit(f"Unknown step: {step!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--step", action="append", default=[], help="repeatable")
    parser.add_argument("--headed", action="store_true", help="show the browser")
    parser.add_argument("--out", type=Path, help="JSONL output path")
    args = parser.parse_args()

    host = re.sub(r"\W+", "_", args.url.split("//")[-1].split("/")[0])
    out = args.out or DATA_DIR / f"{host}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        rec = Recorder(context, out)
        page = context.new_page()

        rec.step = "load"
        # domcontentloaded, not load: heavy third-party tags can keep "load" from firing
        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)  # let tag managers fire
        for step in args.step:
            rec.step = step
            print(f"-> {step}")
            run_step(page, step)
            page.wait_for_timeout(3000)

        rec.save()
        audit_storage(context, page, out.with_suffix(".storage.json"))
        browser.close()

    print(rec.summary())
    print(f"\n{len(rec.records)} analytics requests -> {out}")


if __name__ == "__main__":
    main()
