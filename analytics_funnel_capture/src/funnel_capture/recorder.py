"""Record analytics requests from every frame of a Playwright browser context."""
import json
import time
from pathlib import Path
from typing import List

from playwright.sync_api import BrowserContext, Request, Response

from .schemas import CapturedRequest
from .vendors import classify, parse

MAX_BODY_CHARS = 2000


class Recorder:
    """Attaches to a context so iframe traffic (booking/checkout widgets) is captured too.

    Context-level listeners are used instead of page-level ones because the
    interesting funnel steps often live in cross-origin iframes.
    """

    def __init__(self, context: BrowserContext, out_path: Path) -> None:
        self.step = "init"
        self.records: List[CapturedRequest] = []
        self._by_request: dict[int, CapturedRequest] = {}
        self._out_path = out_path
        context.on("request", self._on_request)
        context.on("response", self._on_response)

    def _on_request(self, request: Request) -> None:
        vendor = classify(request.url)
        if vendor is None:
            return
        try:
            body = request.post_data
        except Exception:  # binary bodies raise on decode
            body = None
        names, params = parse(vendor, request.url, body)
        try:
            frame_url = request.frame.url
        except Exception:  # service-worker requests have no frame
            frame_url = ""
        rec = CapturedRequest(
            ts=time.time(),
            step=self.step,
            vendor=vendor,
            method=request.method,
            url=request.url,
            frame_url=frame_url,
            event_names=names,
            params=params,
            # Keep raw body only where we couldn't extract event names
            raw_body=(body[:MAX_BODY_CHARS] if body and not names else None),
        )
        self.records.append(rec)
        self._by_request[id(request)] = rec

    def _on_response(self, response: Response) -> None:
        rec = self._by_request.get(id(response.request))
        if rec is not None:
            rec.status = response.status

    def save(self) -> None:
        """Write all records as JSONL (one request per line)."""
        self._out_path.parent.mkdir(parents=True, exist_ok=True)
        with self._out_path.open("w", encoding="utf-8") as f:
            for rec in self.records:
                f.write(json.dumps(rec.model_dump()) + "\n")

    def summary(self) -> str:
        """Human-readable table: per step, vendor -> event names and counts."""
        by_step: dict[str, dict[str, list[str]]] = {}
        for r in self.records:
            by_step.setdefault(r.step, {}).setdefault(r.vendor, []).extend(
                r.event_names or ["(request)"]
            )
        lines = []
        for step, vendors in by_step.items():
            lines.append(f"\n== {step} ==")
            for vendor, names in sorted(vendors.items()):
                counts: dict[str, int] = {}
                for n in names:
                    counts[n] = counts.get(n, 0) + 1
                pretty = ", ".join(f"{n} x{c}" if c > 1 else n for n, c in counts.items())
                lines.append(f"  {vendor:<13} {pretty}")
        return "\n".join(lines)
