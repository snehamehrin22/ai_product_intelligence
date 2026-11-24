---
name: edit-reel-in-style
description: Edit a raw video into a reel in the style of a previously analyzed reference (cuts, captions, fonts, stickers), driving the Edits app (metapilot-native MCP). Use when the user hands over a raw file and asks to edit it like the reference/Little Ghosts reel. Requires a style_spec.json from analyze-reel-style.
---

# Edit Reel In Style

## Inputs
- Raw video path from the user.
- `style_spec.json` from `analyze-reel-style` (default: `instagram_video_analyzer/data/little_ghosts_draft/`). If missing, run that skill first.

## Gotcha: tools depend on the app screen
`metapilot-native` only exposes home tools (projects, import) until a project is open. Call `newProject` first, then `ToolSearch` for `addText`, `splitAt`, etc. Load all needed tools in ONE ToolSearch call.

## Steps
1. **Plan from the spec** (no editing yet). Read `pacing` and per-shot `text_overlays`. Target the reference rhythm: hook shot ~11s, then 1-3s shots (median 2.45s), hard cuts only (23/26 shots).
2. **Import**: `newProject` -> `addMedia` (path, audioKind). Get ids via `clips` / `elements`.
3. **Transcribe**: `transcribeClip` (word timestamps). Use `findPauses` to find dead air. Build the cut list from sentence boundaries, not fixed intervals.
4. **Cut**: `splitAt` (one call, many times), then remove dead-air pieces with `delete`; tighten with `trim`. Use hard cuts: do not add `addTransition`.
5. **Captions as text overlays** (the reference uses `addText`, not auto-captions): per phrase `addText` -> `setTextFont` -> `setTextStyle` (size, color, bold) -> `setTextPosition` (normalized x,y) -> `setEmphasis` (shadow) -> `setTextAnimation` (reference: 58 static, 23 pop, 7 fade, 3 typewriter).
   Reference style: white `#FFFFFF`, bold rounded sans, medium size, center/lower-third, shadow, lowercase/title case. Accents: red display `#8B0000` for the key scary word; sky-blue `#87CEEB` pixel/mono for the name/tag line. Pick real fonts via `listCatalog({kind:"font"})`; the spec only describes fonts, it does not name them.
6. **Stickers** (optional, sparse; reference used them in the opening shot only):
   `infisical run --silent -- python scripts/generate_sticker.py "<subject>" <out.png>` in `instagram_video_analyzer/` (OpenAI gpt-image-1, transparent PNG), then `addSticker` (sticker, path, duration, atSeconds).
7. **Verify before exporting**: `previewVideo` + `previewVideoStatus` + `previewVideoFrames`; check text legibility, safe margins, overlaps. Fix and re-preview.
8. **Export**: `export` (path). Report the path; do not claim it matches the reference without comparing frames.

## Verified on On_Cloud.mp4 (first real run)
- **Sandbox**: the app cannot read `~/Downloads`. Copy the raw file to `~/Movies/reel_edits/` first, import and export there. Use `importMedia` (path only) for video; `addMedia` is audio-only (`audioKind`: music|soundEffect|voiceover).
- **Canvas**: `setCanvas aspect=9:16 frameRate=30`. Export came out 1548x2752, not 1080x1920; check before posting.
- **Cuts**: `transcribeClip` (poll `jobStatus`) gives word times; cut at the midpoint of the gap between sentences, e.g. `(end_of_last_word + start_of_next_word)/2`. One `splitAt` call returns all piece ids.
- **Single-shot talking head (no b-roll)**: `detectShots` finds nothing. Build rhythm with jump cuts + alternating punch-in: `setTransform id scale=1.15 allowBeyondCanvas=true keyframes=clear` on every other clip (`keyframes` must be reject|offsetAll|clear).
- **Captions: use `generateCaptions source=video language=en curseWords=false` then `setCaptionStyle style="Short Pop"`** (applies to all). Hand-built `addText` per phrase is ~5 calls each; avoid. Output is one-word-at-a-time pop in InstagramBubble-Black, white with dark outline, lower third. Valid sources: video|voiceover|importedAudio|all.
- **Manual text sizing** (if `addText` is needed): on the 9:16 canvas `setTextStyle size=44` fits ~16 chars/line; size 90 wraps mid-word and covers the face. Place at y~0.8. `setEmphasis` has no shadow; options: none, outline, invertedOutline, backgroundPill, invertedBackgroundPill.
- **Verify**: `previewVideo` returns frames inline; it caught the size-90 bug. Exports run async: poll `exportStatus` until `complete` (file has no moov atom until then).
- Do not call `captions` (returns every token, huge output); use `generateCaptions` counts and previews instead.
- **Verified since**: `addSticker` with a Pillow PNG, `addShape`. **Still unverified**: `generate_sticker.py` (OpenAI returned 429, no credits, at the time), `applyLUT`, `addTransition`.

## Little Ghosts "cutaway card" device (missed by the first analysis; added after user feedback)
The reference alternates talking head with **cards**: a flat solid background (`#ACDDFB` sky blue, sampled from every corner of shots 1,2,6,9,11,25; NO lime green found) with a photo/collage or a **maroon script title** (`#6B0F1A`, Romanesco closest), a hand-drawn star doodle beside titles, and the one-word white captions kept on top. Cards run ~1.3-3s, the voiceover continues underneath. Numbered section titles ("1. Book clubs and events") sit over the face in the same maroon script.
Build a card: `addShape` (x .5 y .5 w 1 h 1, color, opacity 1, startSeconds, duration) -> `moveToLayer toLayer=1` (new shapes land on the TOP layer and hide captions/text) -> `addText` + `setTextFont Romanesco-Regular` + `setTextStyle color #6B0F1A size 64-70` + `setTextPosition y .4` + `setEmphasis none`. Star: Pillow-drawn PNG in `~/Movies/reel_edits/stickers/`, `addSticker sticker=<name> path=<png>`, then `setTransform scale .75 rotation -12`.
- Rendered shape color comes out lighter than the hex given (asked #ACDDFB, previews ~#C7E1FA); compensate or verify against a frame.
- If the raw footage has no b-roll, cards are typographic only; ask the user for real photos (reference used real photos, not illustrations).
- Text widths: ~16 chars/line at size 44; maroon titles size 64-70 wrap into 2-3 lines (fine).
- Only one `previewVideo` can render at a time; run previews sequentially.
- Export needs a full preset: `setExportSettings aspectRatio=nineBySixteen resolution=1080x1920 frameRate=30 resolutionType=HD quality=high dynamicRange=sdr` (else "incomplete preset row"). 9:16 and 1080p are rejected as values.
- Waiting on export: `run_in_background` a `until ffprobe ...; do sleep 3; done` loop, not a foreground sleep.
- Known analyzer gap: `analyze-reel-style` palettes miss flat backgrounds and the card device; check a contact sheet of all shots by eye.

## Photoreal cards (user said: generate realistic images, not cartoon stickers)
- Image model on this account: **`gpt-image-2`** (`gpt-image-1` -> 400 "does not exist"; list with `OpenAI().models.list()` and filter "image"). Scripts: `instagram_video_analyzer/scripts/generate_photo.py "<subject>" <out.png>` (1024x1536 portrait, medium quality, candid-photo style suffix, "no text, no logos"). Run several in parallel with `&` + `wait`.
- Keep subjects generic: no brand names, logos or storefronts (they'd be fabricated brand imagery); put names in the card title. Warn the user generated people/events may need an AI label on Instagram.
- Review every image by contact sheet before use; the first batch had no warped hands or garbled text.
- Photo on card: `addSticker sticker=<name> path=<png>` (same duration as the card) -> `setTransform x .5 y .58 scale 2.2` (scale 1 ~ 30% of canvas width for a 1024px image; 2.2 ~ 66%) -> title at y .14, size 48-70 (keep to 2 lines).
- Layer order trap: new shapes/stickers land on the TOP layer and hide captions. `moveToLayer 1` hides a photo UNDER the card. What worked: leave shapes/photos/titles on top, then `deleteCaptions`, `generateCaptions source=video`, `setCaptionStyle "Short Pop"` LAST so captions get the top track. Re-run this after any further overlay edits.
