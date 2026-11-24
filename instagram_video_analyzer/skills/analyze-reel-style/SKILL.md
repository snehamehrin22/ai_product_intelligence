---
name: analyze-reel-style
description: Reverse-engineer a reference reel/video (cuts, pacing, typography, colors, transitions, audio) into a reusable style spec and recipe. Use when the user gives a video file and asks to analyze its edit, typography, or style so it can be recreated on other footage.
---

# Analyze Reel Style

Runs the `instagram_video_analyzer` project against a reference video.

## Run
```bash
cd /Users/snehamehrin/Desktop/ai_product_intelligence/instagram_video_analyzer
source .venv/bin/activate
infisical run --silent -- python scripts/analyze_video.py "<video path>" 2>&1 | sed -E 's/sk-[A-Za-z0-9_-]+/sk-<hidden>/g'
```
Secrets come from Infisical (`OPENAI_API_KEY`); never read or print them. Needs `ffmpeg`, `tesseract`.
4K HEVC sources are slow (~8 min for a 90s clip): run in the background and wait for the notification.

## Outputs (`data/<video_name>/`)
- `style_spec.json`: per-shot timing, palette, OCR, text overlays (font, hex, position, size, animation), transitions, transcript, pacing.
- `style_recipe.md`: LLM-written recipe. Generic; treat `style_spec.json` as the source of truth.

## Known limits
- Fonts are described, not named: map to the editor's font catalog by hand.
- Overall `palette` is sampled from one frame; prefer per-shot palettes.
- Animation type is inferred from 3-5 frames per shot, so timing is approximate.
- Shots are cached per index (`shot_NN.json`); delete them to re-analyze.
