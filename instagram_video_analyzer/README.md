# instagram_video_analyzer

Analyzes a reference reel (cuts, typography, palette, audio, pacing) into `style_spec.json` + `style_recipe.md`, then drives the Edits app (MCP `metapilot-native`) to edit raw footage in that style.

**Status: closed.** The v3 edit of `On_Cloud.mp4` was judged not good enough. Known gaps: the analyzer misses flat backgrounds and cutaway cards, and the card blue renders lighter than the reference.

## Run
```
python3.13 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
infisical run --silent -- python scripts/analyze_video.py "<video>"
infisical run --silent -- python scripts/generate_photo.py "<subject>" out.png   # gpt-image-2
```
Secrets come from Infisical (`OPENAI_API_KEY`). `data/` is gitignored.

## Layout
- `src/instagram_video_analyzer/` schemas, media (ffmpeg), vision (OpenAI)
- `prompts/` LLM prompts, `scripts/` entry points
- `skills/` copies of the `analyze-reel-style` and `edit-reel-in-style` Claude skills (live copies are in `~/.claude/skills/`)
