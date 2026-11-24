# iOS capture setup

Log the analytics an iPhone app fires, using mitmproxy on your Mac. Same JSONL format as
the web capture, so `scripts/show_events.py` works on both.

## One-time (Mac)
```bash
cd analytics_funnel_capture && source .venv/bin/activate && pip install -r requirements.txt
```
Mac and iPhone must be on the same Wi-Fi.

## Each session
1. Mac: `scripts/ios_proxy.sh <app-name>` prints the proxy IP and port (default 8080).
2. iPhone: Settings > Wi-Fi > (i) > Configure Proxy > **Manual**; enter that Server and Port.
3. iPhone Safari: open `http://mitm.it`, install the iOS profile, then
   Settings > General > About > Certificate Trust Settings > **enable full trust**
   (skipping this is the usual reason nothing decrypts).
4. Delete and reinstall the target app for a clean first-run, then use it.
5. Label steps as you go (new terminal tab): `scripts/ios_mark.sh "onboarding 1"`,
   `"paywall"`, `"after purchase screen"`, etc. Unlabelled traffic is tagged `unmarked`.
6. Read: `python scripts/show_events.py data/ios_<app>_<time>.jsonl`.

## Cleanup (do this every time)
- iPhone: Wi-Fi > Configure Proxy > **Off**; Settings > General > VPN & Device Management >
  **delete the mitmproxy profile**. A trusted mitm CA can decrypt your HTTPS traffic.
- Mac: Ctrl-C the proxy.

## Safety
- While proxied, **all** phone traffic passes through your Mac. Don't open banking or
  password-manager apps; a spare device is better.
- `data/` is gitignored because it holds device identifiers. Don't commit it.

## What works and what doesn't
- Works: apps that trust the user-installed CA (most indie and growth-stage apps), plus
  the app's web views.
- **Certificate pinning** (many large apps) shows connection errors and no payloads. Skip
  those apps; defeating pinning (Frida/objection) may breach the app's ToS.
- Firebase (`app-measurement.com`) sends protobuf: logged by vendor/host only.
- Server-side events never touch the phone and can't be seen.
- Amplitude, Segment, Mixpanel, PostHog, Braze and RevenueCat JSON payloads are parsed into
  event names; AppsFlyer/Adjust/Branch are logged as requests.
- Android 7+ ignores user-installed CAs for most apps; use an emulator with a rooted image.
