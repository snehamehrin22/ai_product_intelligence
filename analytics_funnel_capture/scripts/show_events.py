"""Print named events (with properties) from a capture JSONL, grouped by step.

Usage: python scripts/show_events.py data/<file>.jsonl [--all]
By default hides GA4 page_view/scroll noise only when --all is not given.
"""
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--all", action="store_true", help="include request-only rows")
    args = parser.parse_args()

    seen: set[tuple] = set()
    for line in args.path.read_text().splitlines():
        r = json.loads(line)
        if not r["event_names"] and not args.all:
            continue
        key = (r["step"], r["vendor"], tuple(r["event_names"]), r["frame_url"].split("?")[0])
        if key in seen:
            continue
        seen.add(key)
        print(f"[{r['step']}] {r['vendor']}: {', '.join(r['event_names']) or '(request)'}")
        print(f"    page: {r['params'].get('dl', r['frame_url'])[:90]}")
        for k, v in r["params"].items():
            if k not in ("tid", "dl", "dt"):
                print(f"    {k} = {str(v)[:80]}")


if __name__ == "__main__":
    main()
