"""mitmproxy addon: log analytics requests from an iOS/Android device as JSONL.

Uses the same classifier/parsers and CapturedRequest schema as the Playwright
capture, so web and mobile runs produce one report format. The active funnel
step comes from a marker file (see scripts/ios_mark.sh) because a phone has no
script driving it: you tap through the app and mark each step as you go.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional

from mitmproxy import http

from .schemas import CapturedRequest
from .vendors import classify, parse

MAX_BODY_CHARS = 2000


class AnalyticsLogger:
    """Appends one JSONL line per analytics request, tagged with the current step."""

    def __init__(self, out_path: Path, step_file: Path) -> None:
        self.out_path = out_path
        self.step_file = step_file
        out_path.parent.mkdir(parents=True, exist_ok=True)

    def _current_step(self) -> str:
        try:
            return self.step_file.read_text().strip() or "unmarked"
        except FileNotFoundError:
            return "unmarked"

    def response(self, flow: http.HTTPFlow) -> None:
        """Called by mitmproxy when a response completes (so status is known)."""
        url = flow.request.pretty_url
        vendor = classify(url)
        if vendor is None:
            return
        body: Optional[str] = flow.request.get_text(strict=False) or None
        names, params = parse(vendor, url, body)
        rec = CapturedRequest(
            ts=time.time(),
            step=self._current_step(),
            vendor=vendor,
            method=flow.request.method,
            url=url,
            frame_url="ios-app",
            status=flow.response.status_code if flow.response else None,
            event_names=names,
            params=params,
            # Raw body only where nothing was parsed (e.g. protobuf, unknown JSON)
            raw_body=(body[:MAX_BODY_CHARS] if body and not names else None),
        )
        with self.out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec.model_dump()) + "\n")


def build_from_env() -> AnalyticsLogger:
    """Create the logger from FUNNEL_OUT / FUNNEL_STEP_FILE (set by ios_proxy.sh)."""
    return AnalyticsLogger(
        Path(os.environ["FUNNEL_OUT"]),
        Path(os.environ.get("FUNNEL_STEP_FILE", "data/ios_step.txt")),
    )
