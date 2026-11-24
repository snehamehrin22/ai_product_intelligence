"""Generate a realistic photo with OpenAI gpt-image-2 for a cutaway card.

Usage:
    infisical run --silent -- python scripts/generate_photo.py "<subject>" out/photo.png
"""
import base64
import sys
from pathlib import Path

from openai import OpenAI

# Realism guardrails: candid phone/35mm look, and no text/logos so we never fabricate a brand's signage.
STYLE = ("candid documentary photograph, natural light, shot on a 35mm lens, shallow depth of field, "
         "real skin and fabric texture, slightly imperfect framing, no text, no logos, no watermark")


def main() -> None:
    """Generate one portrait photo and write it to the given path."""
    subject, out = sys.argv[1], Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    resp = OpenAI().images.generate(model="gpt-image-2", prompt=f"{subject}. {STYLE}", size="1024x1536",
                                    quality="medium")
    out.write_bytes(base64.b64decode(resp.data[0].b64_json))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
