"""mitmdump entrypoint: `mitmdump -s scripts/mitm_addon.py` (see scripts/ios_proxy.sh)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from funnel_capture.mitm_logger import build_from_env  # noqa: E402

addons = [build_from_env()]
