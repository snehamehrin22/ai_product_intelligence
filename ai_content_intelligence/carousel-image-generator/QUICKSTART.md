# Quick Start Guide

## Generate Your First Carousel

### Step 1: Navigate to the generator directory
```bash
cd carousel-image-generator
```

### Step 2: Generate PPTX (works now)
```bash
npm test
```

This will:
- Load `Superhuman_pillar_01_growth_loops_are_changing.json`
- Generate PPTX with 10 slides
- Save to `../data/carousel_images/Superhuman_pillar_01_growth_loops_are_changing.pptx`

### Step 3: Open PPTX to verify
```bash
open ../data/carousel_images/Superhuman_pillar_01_growth_loops_are_changing.pptx
```

---

## Generate Images (requires system tools)

### Install conversion tools first:
```bash
# macOS
brew install --cask libreoffice
brew install poppler

# Linux
sudo apt-get install libreoffice poppler-utils
```

### Run full pipeline:
```bash
npm run test-full
```

This will:
- Generate PPTX
- Convert to PDF
- Extract images (300 DPI JPGs)
- Clean up intermediate files

---

## Generate for Other Carousels

### Any JSON file:
```bash
npm run generate-images <path-to-json>

# Examples:
npm run generate-images ../data/carousel_outputs/Superhuman_pillar_02_measurement_gap.json
npm run generate-images ../data/carousel_outputs/AnotherApp_pillar_01_growth_loops_are_changing.json
```

---

## Troubleshooting

### "File not found"
- Make sure you're in the `carousel-image-generator` directory
- Check that the JSON file exists at the specified path

### "LibreOffice not installed"
- Install with: `brew install --cask libreoffice` (macOS)
- Or skip image generation and just generate PPTX

### "pdftoppm not installed"
- Install with: `brew install poppler` (macOS)
- Or convert PPTX to images manually in PowerPoint

---

## What You Get

### PPTX Format:
- 10" x 12.5" slides (Instagram portrait)
- Burgundy gradient background
- Gold and cream accents
- Glass-morphism cards
- SNEHA branding

### JPG Images:
- 1080x1350px (Instagram perfect)
- 300 DPI quality
- One image per slide
- Named: `carousel-name-1.jpg`, `carousel-name-2.jpg`, etc.

---

## Next Steps

1. **Verify the design** - Open PPTX and check if you like the style
2. **Iterate if needed** - Edit `src/design-system.js` to change colors/fonts
3. **Generate for all carousels** - Run on all JSON files in `data/carousel_outputs/`
4. **Upload to Instagram** - Use the generated images in your posts
