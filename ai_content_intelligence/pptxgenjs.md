# PptxGenJS Comprehensive Tutorial

## Table of Contents
1. [Setup & Installation](#setup--installation)
2. [Basic Concepts](#basic-concepts)
3. [Creating Presentations](#creating-presentations)
4. [Text Formatting](#text-formatting)
5. [Shapes & Visual Elements](#shapes--visual-elements)
6. [Images & Icons](#images--icons)
7. [Charts & Tables](#charts--tables)
8. [Slide Masters & Layouts](#slide-masters--layouts)
9. [Advanced Positioning](#advanced-positioning)
10. [Complete Example: Instagram Carousel](#complete-example-instagram-carousel)
11. [Common Pitfalls & Solutions](#common-pitfalls--solutions)

---

## Setup & Installation

### Node.js Project Setup
```bash
# Initialize Node.js project
npm init -y

# Install PptxGenJS
npm install pptxgenjs

# Optional: Install for React Icons (if using SVG icons)
npm install react-icons
npm install @svgr/core  # For converting React Icons to static SVG
```

### Basic Import
```javascript
// ES6 import
import PptxGenJS from 'pptxgenjs';

// CommonJS
const PptxGenJS = require('pptxgenjs');

// Create presentation instance
const pptx = new PptxGenJS();
```

---

## Basic Concepts

### Coordinate System
PptxGenJS uses **inches** by default (PowerPoint standard).

```javascript
// Standard slide size: 10" x 7.5"
{
  x: 0,      // Left edge
  y: 0,      // Top edge
  w: 10,     // Width (full slide width)
  h: 7.5     // Height (full slide height)
}
```

**Common conversions:**
- 1 inch = 2.54 cm
- 1 inch = 72 points
- Instagram square: 10" x 10" (custom layout)

### Slide Creation
```javascript
// Add a new slide
let slide = pptx.addSlide();

// Add slide with specific layout
let slide2 = pptx.addSlide({ masterName: 'TITLE_SLIDE' });
```

### Saving Files
```javascript
// Save to file (Node.js)
pptx.writeFile({ fileName: 'presentation.pptx' });

// Get as base64 (for web/storage)
pptx.write('base64').then(data => {
  console.log(data);
});

// Stream (Node.js)
pptx.stream().then(stream => {
  // Handle stream
});
```

---

## Text Formatting

### Basic Text
```javascript
slide.addText('Hello World', {
  x: 1,
  y: 1,
  fontSize: 24,
  color: '000000'
});
```

### Rich Text Options
```javascript
slide.addText('Formatted Text', {
  // Position & Size
  x: 0.5,          // Inches from left
  y: 1.0,          // Inches from top
  w: 5,            // Width
  h: 1,            // Height (auto if not specified)

  // Font
  fontSize: 18,    // Points
  fontFace: 'Arial',
  bold: true,
  italic: false,
  underline: false,
  strike: false,

  // Color
  color: '363636', // Hex (no #)

  // Alignment
  align: 'center', // left, center, right, justify
  valign: 'middle', // top, middle, bottom

  // Spacing
  lineSpacing: 1.5,
  paraSpaceAfter: 12,
  paraSpaceBefore: 0,

  // Margins
  margin: 0.1,     // All sides
  // Or specific: [top, right, bottom, left]
  margin: [0.1, 0.2, 0.1, 0.2],

  // Fill/Background
  fill: { color: 'F1F1F1' },

  // Border
  line: { color: '000000', width: 1 },

  // Shadow
  shadow: {
    type: 'outer',
    blur: 3,
    offset: 2,
    angle: 45,
    color: '000000',
    opacity: 0.5
  }
});
```

### Multi-Line Text with Different Formatting
```javascript
slide.addText([
  { text: 'Bold Title\n', options: { fontSize: 24, bold: true, color: 'FF0000' } },
  { text: 'Regular subtitle', options: { fontSize: 16, color: '666666' } }
], {
  x: 1,
  y: 1,
  w: 5,
  h: 2
});
```

### Text Bullet Points
```javascript
slide.addText([
  { text: 'First bullet point', options: { bullet: true } },
  { text: 'Second bullet point', options: { bullet: true } },
  { text: 'Third bullet point', options: { bullet: true } }
], {
  x: 1,
  y: 2,
  w: 8,
  fontSize: 18
});
```

---

## Shapes & Visual Elements

### Rectangle
```javascript
slide.addShape(pptx.ShapeType.rect, {
  x: 1,
  y: 1,
  w: 3,
  h: 2,
  fill: { color: 'FF5733' },
  line: { color: '000000', width: 2 }
});
```

### Rounded Rectangle (Accent Pills)
```javascript
slide.addShape(pptx.ShapeType.roundRect, {
  x: 0.5,
  y: 0.3,
  w: 2,
  h: 0.5,
  fill: { color: 'F5E6D3' },
  line: { type: 'none' },
  rectRadius: 0.25  // Corner radius
});
```

### Tilted Box (Accent Element)
```javascript
// Create rectangle and rotate
slide.addShape(pptx.ShapeType.rect, {
  x: 7,
  y: 2,
  w: 2.5,
  h: 1.5,
  fill: { color: 'D4AF79', transparency: 20 },
  line: { type: 'none' },
  rotate: 5  // Degrees
});
```

### Circle
```javascript
slide.addShape(pptx.ShapeType.ellipse, {
  x: 4,
  y: 3,
  w: 1,
  h: 1,  // Same as w for perfect circle
  fill: { color: 'E74C3C' }
});
```

### Line/Arrow
```javascript
slide.addShape(pptx.ShapeType.line, {
  x: 1,
  y: 2,
  w: 3,
  h: 0,
  line: { color: 'FFFFFF', width: 3, dashType: 'solid' }
});

// Arrow
slide.addShape(pptx.ShapeType.rightArrow, {
  x: 5,
  y: 3,
  w: 2,
  h: 0.5,
  fill: { color: 'FFFFFF' }
});
```

### Available Shape Types
```javascript
pptx.ShapeType.rect
pptx.ShapeType.ellipse
pptx.ShapeType.roundRect
pptx.ShapeType.triangle
pptx.ShapeType.line
pptx.ShapeType.rightArrow
pptx.ShapeType.leftArrow
pptx.ShapeType.upArrow
pptx.ShapeType.downArrow
// ... and many more
```

---

## Images & Icons

### Adding Images
```javascript
// From file path
slide.addImage({
  path: '/path/to/image.png',
  x: 1,
  y: 1,
  w: 3,
  h: 2
});

// From URL
slide.addImage({
  path: 'https://example.com/image.jpg',
  x: 1,
  y: 1,
  w: 3,
  h: 2
});

// From base64 data
slide.addImage({
  data: 'image/png;base64,iVBORw0KG...',
  x: 1,
  y: 1,
  w: 3,
  h: 2
});
```

### Image Sizing Options
```javascript
slide.addImage({
  path: 'logo.png',
  x: 0.5,
  y: 0.5,
  w: 1.5,
  h: 1.5,
  sizing: {
    type: 'contain', // contain, cover, crop
    w: 1.5,
    h: 1.5
  },
  rounding: true  // Rounded corners
});
```

### Using React Icons (SVG → PNG → PPTX)

**Step 1: Generate SVG from React Icons**
```javascript
import { FaTwitter, FaInstagram, FaLinkedin } from 'react-icons/fa';
import { renderToStaticMarkup } from 'react-dom/server';
import fs from 'fs';

// Render icon to SVG string
const iconSvg = renderToStaticMarkup(<FaTwitter size={48} color="#1DA1F2" />);

// Save SVG
fs.writeFileSync('twitter-icon.svg', iconSvg);
```

**Step 2: Convert SVG to PNG (using sharp or canvas)**
```javascript
import sharp from 'sharp';

await sharp('twitter-icon.svg')
  .resize(200, 200)
  .png()
  .toFile('twitter-icon.png');
```

**Step 3: Add to PPTX**
```javascript
slide.addImage({
  path: 'twitter-icon.png',
  x: 8.5,
  y: 7,
  w: 0.3,
  h: 0.3
});
```

**Alternative: Use Pre-generated Icon Library**
Create a library of commonly used icons once, then reference them:
```javascript
const icons = {
  twitter: 'assets/icons/twitter.png',
  instagram: 'assets/icons/instagram.png',
  linkedin: 'assets/icons/linkedin.png',
  swipe: 'assets/icons/swipe.png'
};

slide.addImage({ path: icons.twitter, x: 8.5, y: 7, w: 0.25, h: 0.25 });
```

---

## Charts & Tables

### Simple Table
```javascript
const rows = [
  ['Header 1', 'Header 2', 'Header 3'],
  ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
  ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3']
];

slide.addTable(rows, {
  x: 1,
  y: 1,
  w: 8,
  fontSize: 14,
  border: { pt: 1, color: '000000' },
  fill: { color: 'F7F7F7' }
});
```

### Bar Chart
```javascript
const chartData = [
  {
    name: 'Series 1',
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    values: [10, 20, 30, 40]
  }
];

slide.addChart(pptx.ChartType.bar, chartData, {
  x: 1,
  y: 1,
  w: 8,
  h: 4,
  showTitle: true,
  title: 'Quarterly Revenue'
});
```

---

## Slide Masters & Layouts

### Define Slide Master
```javascript
pptx.defineSlideMaster({
  title: 'BRAND_MASTER',
  background: { color: '4A1F2F' },
  objects: [
    // Header
    { text: { text: 'SNEHA', options: { x: 0.5, y: 0.3, fontSize: 18, color: 'FFFFFF', bold: true } } },
    // Footer
    { text: { text: '@sneha', options: { x: 8.5, y: 7, fontSize: 12, color: 'F5E6D3' } } }
  ]
});
```

### Use Slide Master
```javascript
let slide = pptx.addSlide({ masterName: 'BRAND_MASTER' });
```

---

## Advanced Positioning

### Grid System (for consistent spacing)
```javascript
const GRID = {
  marginX: 0.5,
  marginY: 0.5,
  gutterX: 0.2,
  gutterY: 0.3,
  cols: 12,
  rows: 10
};

function getGridPosition(col, row, colSpan = 1, rowSpan = 1) {
  const colWidth = (10 - GRID.marginX * 2 - GRID.gutterX * (GRID.cols - 1)) / GRID.cols;
  const rowHeight = (7.5 - GRID.marginY * 2 - GRID.gutterY * (GRID.rows - 1)) / GRID.rows;

  return {
    x: GRID.marginX + col * (colWidth + GRID.gutterX),
    y: GRID.marginY + row * (rowHeight + GRID.gutterY),
    w: colSpan * colWidth + (colSpan - 1) * GRID.gutterX,
    h: rowSpan * rowHeight + (rowSpan - 1) * GRID.gutterY
  };
}

// Usage
slide.addText('Title', {
  ...getGridPosition(0, 0, 12, 2),
  fontSize: 36,
  bold: true
});
```

### Dynamic Text Fitting
```javascript
function addDynamicText(slide, text, options) {
  let fontSize = options.fontSize || 20;
  const maxFontSize = fontSize;
  const minFontSize = 12;

  // Estimate if text will fit (rough heuristic)
  const charsPerLine = Math.floor((options.w * 72) / (fontSize * 0.6));
  const linesNeeded = Math.ceil(text.length / charsPerLine);
  const heightNeeded = linesNeeded * (fontSize / 72) * 1.2;

  if (heightNeeded > options.h) {
    fontSize = Math.max(minFontSize, fontSize * (options.h / heightNeeded));
  }

  slide.addText(text, { ...options, fontSize });
}
```

---

## Complete Example: Instagram Carousel

### Full Pipeline
```javascript
import PptxGenJS from 'pptxgenjs';
import fs from 'fs';

// Brand constants
const BRAND = {
  colors: {
    background: '4A1F2F',
    accent: 'F5E6D3',
    text: 'FFFFFF',
    textSecondary: 'E8D5C4'
  },
  fonts: {
    header: 'Arial Black',
    body: 'Arial'
  },
  layout: {
    headerY: 0.3,
    titleY: 1.2,
    contentStartY: 2.5,
    footerY: 9.2,
    marginX: 0.5,
    contentWidth: 9
  }
};

// Load carousel data
const carouselData = JSON.parse(fs.readFileSync('carousel_data.json', 'utf8'));

// Create presentation
const pptx = new PptxGenJS();

// Set custom slide size (Instagram square)
pptx.layout = 'LAYOUT_WIDE';
pptx.defineLayout({ name: 'INSTAGRAM_SQUARE', width: 10, height: 10 });
pptx.layout = 'INSTAGRAM_SQUARE';

// Define slide master
pptx.defineSlideMaster({
  title: 'CAROUSEL_MASTER',
  background: { color: BRAND.colors.background },
  objects: [
    {
      text: {
        text: 'SNEHA',
        options: {
          x: BRAND.layout.marginX,
          y: BRAND.layout.headerY,
          fontSize: 18,
          color: BRAND.colors.text,
          bold: true,
          fontFace: BRAND.fonts.header
        }
      }
    },
    {
      text: {
        text: '@sneha',
        options: {
          x: 8.5,
          y: BRAND.layout.footerY,
          fontSize: 12,
          color: BRAND.colors.accent
        }
      }
    }
  ]
});

// Slide 1: Title Slide
let slide1 = pptx.addSlide({ masterName: 'CAROUSEL_MASTER' });

slide1.addText(carouselData.title, {
  x: BRAND.layout.marginX,
  y: 3.5,
  w: BRAND.layout.contentWidth,
  h: 3,
  fontSize: 48,
  bold: true,
  color: BRAND.colors.text,
  fontFace: BRAND.fonts.header,
  align: 'center',
  valign: 'middle'
});

// Add accent pill
slide1.addShape(pptx.ShapeType.roundRect, {
  x: 3.5,
  y: 2.5,
  w: 3,
  h: 0.5,
  fill: { color: BRAND.colors.accent },
  line: { type: 'none' },
  rectRadius: 0.25
});

slide1.addText('GROWTH LOOPS', {
  x: 3.5,
  y: 2.5,
  w: 3,
  h: 0.5,
  fontSize: 14,
  bold: true,
  color: BRAND.colors.background,
  align: 'center',
  valign: 'middle'
});

// Slides 2+: Content Slides
carouselData.slides.forEach((slideData, idx) => {
  let slide = pptx.addSlide({ masterName: 'CAROUSEL_MASTER' });

  // Slide number
  slide.addText(`${idx + 1}/${carouselData.slides.length}`, {
    x: BRAND.layout.marginX,
    y: 0.8,
    fontSize: 12,
    color: BRAND.colors.accent
  });

  // Title
  slide.addText(slideData.title, {
    x: BRAND.layout.marginX,
    y: BRAND.layout.titleY,
    w: BRAND.layout.contentWidth,
    fontSize: 32,
    bold: true,
    color: BRAND.colors.text,
    fontFace: BRAND.fonts.header
  });

  // Content lines
  let yPos = BRAND.layout.contentStartY;
  slideData.lines.forEach(line => {
    slide.addText(line, {
      x: BRAND.layout.marginX,
      y: yPos,
      w: BRAND.layout.contentWidth,
      fontSize: 18,
      color: BRAND.colors.text,
      fontFace: BRAND.fonts.body,
      lineSpacing: 1.3
    });
    yPos += 0.6;
  });

  // Add tilted accent box (varies position per slide)
  if (idx % 3 === 0) {
    slide.addShape(pptx.ShapeType.rect, {
      x: 7.5,
      y: 1.5,
      w: 2,
      h: 1.2,
      fill: { color: BRAND.colors.accent, transparency: 80 },
      line: { type: 'none' },
      rotate: 5
    });
  }
});

// Add swipe indicator to last slide
let lastSlide = pptx.addSlide({ masterName: 'CAROUSEL_MASTER' });
lastSlide.addText('◀ SWIPE TO SEE MORE', {
  x: 0.5,
  y: 9.5,
  fontSize: 14,
  color: BRAND.colors.accent,
  align: 'center'
});

// Save
pptx.writeFile({ fileName: 'carousel.pptx' });
console.log('✅ Carousel generated: carousel.pptx');
```

---

## Common Pitfalls & Solutions

### 1. Text Overflowing Slide
**Problem:** Long text doesn't fit in defined area.

**Solution:**
```javascript
function truncateText(text, maxLength) {
  return text.length > maxLength ? text.slice(0, maxLength - 3) + '...' : text;
}

// Or dynamically reduce font size
function fitText(slide, text, bounds, baseFontSize) {
  let fontSize = baseFontSize;
  const estimated = text.length * (fontSize * 0.6) / 72;

  if (estimated > bounds.w) {
    fontSize = Math.max(12, fontSize * (bounds.w / estimated));
  }

  slide.addText(text, { ...bounds, fontSize });
}
```

### 2. Colors Not Matching
**Problem:** Hex colors look different in PowerPoint.

**Solution:** Always test in actual PowerPoint viewer. Use uppercase hex without `#`:
```javascript
// ✅ Correct
fill: { color: 'FF5733' }

// ❌ Incorrect
fill: { color: '#ff5733' }
```

### 3. Positioning Inconsistencies
**Problem:** Elements shift when opening in different PowerPoint versions.

**Solution:** Use absolute positioning in inches, avoid percentages:
```javascript
// ✅ Better
{ x: 1.5, y: 2.0, w: 6, h: 1 }

// ⚠️ Avoid
{ x: '15%', y: '20%', w: '60%', h: '10%' }
```

### 4. Missing Fonts
**Problem:** Custom fonts don't render correctly.

**Solution:** Stick to web-safe fonts or embed fonts explicitly:
```javascript
const SAFE_FONTS = ['Arial', 'Helvetica', 'Times New Roman', 'Courier', 'Georgia'];
```

### 5. Image Quality Loss
**Problem:** Images appear blurry in final output.

**Solution:** Use high-resolution images (300 DPI minimum):
```javascript
// For 1" x 1" image, use at least 300x300px source image
slide.addImage({
  path: 'high-res-logo.png', // 600x600px for 2x quality
  x: 0.5,
  y: 0.5,
  w: 1,
  h: 1
});
```

### 6. Performance with Many Slides
**Problem:** Generation slows down with 50+ slides.

**Solution:** Generate in batches or use streaming:
```javascript
async function generateLargePresentation(slidesData) {
  const pptx = new PptxGenJS();

  for (let i = 0; i < slidesData.length; i++) {
    addSlide(pptx, slidesData[i]);

    if (i % 20 === 0) {
      console.log(`Generated ${i}/${slidesData.length} slides...`);
    }
  }

  await pptx.writeFile({ fileName: 'large-presentation.pptx' });
}
```

---

## Best Practices

1. **Use Constants for Brand Values:**
   ```javascript
   const BRAND = { colors: {...}, fonts: {...}, spacing: {...} };
   ```

2. **Create Reusable Component Functions:**
   ```javascript
   function addHeader(slide) { /* ... */ }
   function addFooter(slide) { /* ... */ }
   ```

3. **Validate Data Before Generation:**
   ```javascript
   if (!carouselData.title || carouselData.slides.length === 0) {
     throw new Error('Invalid carousel data');
   }
   ```

4. **Test in Real PowerPoint:**
   Always open generated PPTX in PowerPoint to verify rendering.

5. **Version Control Your Templates:**
   Store brand constants and templates in separate config files.

---

## Resources

- [PptxGenJS Official Docs](https://gitbrent.github.io/PptxGenJS/)
- [PptxGenJS GitHub](https://github.com/gitbrent/PptxGenJS)
- [PowerPoint Shapes Reference](https://gitbrent.github.io/PptxGenJS/docs/api-shapes/)
- [React Icons Library](https://react-icons.github.io/react-icons/)

---

## Next Steps for Your Project

1. **Extract Design Patterns:** Analyze training carousel images to extract exact spacing, font sizes, and layout rules.

2. **Create Component Library:** Build reusable functions for:
   - `addBrandHeader(slide)`
   - `addBrandFooter(slide)`
   - `addTitleSlide(slide, title, subtitle)`
   - `addContentSlide(slide, slideNumber, title, lines)`
   - `addAccentPill(slide, text, x, y)`
   - `addTiltedBox(slide, x, y)`

3. **Build Layout Templates:** Define layouts for each content type (simple, list, stats, comparison).

4. **Implement Content Parser:** Map parsed carousel text to appropriate slide layouts.

5. **Test & Iterate:** Generate test carousels and compare against training examples.
