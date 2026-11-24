"""Generate a transparent-background sticker PNG with OpenAI gpt-image-2.

Usage:
    infisical run --silent -- python scripts/generate_sticker.py "cute ghost with a book" out/ghost.png
"""
import base64
import sys
from pathlib import Path

from openai import OpenAI

# Fixed style suffix: gpt-image-2 drifts between calls, so every sticker shares one look.
STYLE = ("flat vector sticker, thick white outline, soft shadow, playful hand-drawn feel, "
         "centered single subject, no text, transparent background")


def main() -> None:
    """Generate one sticker and write it to the given path."""
    prompt, out = sys.argv[1], Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    resp = OpenAI().images.generate(model="gpt-image-2", prompt=f"{prompt}, {STYLE}", size="1024x1024",
                                    background="transparent", output_format="png")
    out.write_bytes(base64.b64decode(resp.data[0].b64_json))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
