# Carousel Image Generator

Generate Instagram-ready carousel images from JSON carousel data using PPTX.

## Features

- **Dynamic Content**: Accepts any carousel JSON as input
- **Beautiful Design**: Burgundy gradient backgrounds, glass-morphism cards, gold accents
- **Brand Consistent**: SNEHA branding, consistent typography and spacing
- **Flexible Layouts**: Auto-adjusts font sizes, line breaks, and spacing based on content

## Setup

```bash
cd carousel-image-generator
npm install
```

## Usage

### Generate PPTX from JSON

```bash
npm run generate ../data/carousel_outputs/Superhuman_pillar_01_growth_loops_are_changing.json
```

Or directly:

```bash
node src/index.js <path-to-carousel-json>
```

### Convert PPTX to Images

**Step 1: PPTX → PDF**
```bash
soffice --headless --convert-to pdf output.pptx --outdir ./output
```

**Step 2: PDF → JPG Images**
```bash
pdftoppm -jpeg -r 300 output.pdf output/slide
# Result: slide-1.jpg, slide-2.jpg, ...
```

## Input Format

Expected JSON structure:

```json
{
  "title": "How Superhuman Actually Grows",
  "pillar": "pillar_01",
  "slides": [
    {
      "index": 1,
      "title": "The Real Reason Superhuman Grows",
      "text_lines": [
        "Line 1 of content...",
        "Line 2 of content...",
        "Line 3 of content..."
      ]
    }
  ],
  "created_at": "2026-02-06T10:00:00",
  "total_slides": 10
}
```

## Output

- **PPTX File**: `data/carousel_images/<carousel-name>.pptx`
- **Slide Size**: 10" x 12.5" (Instagram portrait format: 1080x1350px)
- **Quality**: 300 DPI images when converted

## Design System

### Colors
- **Background**: Deep burgundy radial gradient
- **Accent**: Cream/gold (#F4F4F1, #D4B896)
- **Text**: Cream white (#F4F4F1)

### Typography
- **Display**: Georgia (titles, headers)
- **Body**: Georgia (content)
- **Brand**: Arial (SNEHA header)

### Layout
- **Slide 1**: Title slide with category pill and hook
- **Slides 2+**: Content slides with title, lines, and accent elements
- **Components**: Glass-morphism cards, tilted accent boxes, left accent bars

## Project Structure

```
carousel-image-generator/
├── package.json
├── README.md
├── src/
│   ├── index.js           # Main entry point (CLI)
│   ├── generator.js       # PPTX generation logic
│   ├── design-system.js   # Colors, fonts, layout constants
│   ├── background.js      # Gradient background generator
│   └── components.js      # Reusable slide components
```

## Requirements

- Node.js 18+
- LibreOffice (for PPTX → PDF conversion)
- poppler-utils (for PDF → images conversion)

### Install System Dependencies

**macOS:**
```bash
brew install --cask libreoffice
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice poppler-utils
```

## Development

Run with a test carousel:

```bash
npm test
```

This generates a carousel from `Superhuman_pillar_01_growth_loops_are_changing.json`.

## Next Steps

1. Generate PPTX from all carousel JSON files
2. Batch convert to images
3. Upload to Instagram (manual or via API)
