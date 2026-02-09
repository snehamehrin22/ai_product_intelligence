# PPTX Manipulation & Generation Skill

## Overview
This skill enables reading, editing, and creating PowerPoint (PPTX) files programmatically, with a focus on generating branded carousel slides for social media.

## Core Capabilities

### 1. Reading PPTX Files
- Extract text content from slides
- Analyze layout structures
- Identify design patterns (colors, fonts, spacing)
- Parse shapes, images, and formatting

### 2. Editing PPTX Files
- Modify text content while preserving formatting
- Update colors and styles
- Replace images
- Adjust positioning and sizing

### 3. Creating PPTX Files
- Generate slides from scratch using templates
- Apply consistent branding (colors, fonts, logos)
- Create complex layouts with shapes and images
- Export to various formats (PDF, images)

## Recommended Approach: PptxGenJS

**Library:** [PptxGenJS](https://gitbrent.github.io/PptxGenJS/) (Node.js)

**Why PptxGenJS:**
- Clean, declarative API
- Precise positioning control (inches, percentages, points)
- Rich text formatting (bold, colors, fonts, alignment)
- Shape primitives (rectangles, circles, lines)
- Image embedding (PNG, JPG, SVG)
- Chart and table support
- No PowerPoint installation required

**Installation:**
```bash
npm install pptxgenjs
```

## Design Guidelines for Carousel Slides

### Brand Identity Elements

**Typography Hierarchy:**
1. **Header (Slide 1):** 48-60pt, Bold, Condensed/Sans-serif
2. **Slide Titles:** 32-42pt, Bold
3. **Body Text:** 18-24pt, Regular/Medium
4. **Subtext/Footer:** 12-16pt, Regular

**Color Palette (Based on Training Examples):**

**Style 1: Burgundy/Maroon**
- Background: `#4A1F2F` (deep burgundy)
- Accent: `#F5E6D3` (cream) for pills/badges
- Text: `#FFFFFF` (white primary), `#E8D5C4` (cream secondary)

**Style 2: Dark Gray/Charcoal**
- Background: `#2C2C2E` (charcoal gray)
- Accent: `#D4AF79` (gold/tan) for tilted boxes
- Text: `#FFFFFF` (white primary), `#B0B0B0` (gray secondary)

**Style 3: Forest Green**
- Background: `#1A3A2E` (deep green)
- Accent: `#E74C3C` (red/coral) for tilted boxes
- Text: `#FFFFFF` (white primary), `#A8D5BA` (mint secondary)

**Layout Patterns:**

**Consistent Elements (All Slides):**
- **Header:** Brand name "SNEHA" in top-left or centered (18-24pt)
- **Footer:** Social icons + handle (@sneha) bottom-right
- **Swipe Indicator:** "◀ SWIPE" text or dots (e.g., "1/10")
- **Safe Margins:** 0.5-0.75" from edges

**Slide Layouts:**

1. **Title Slide (Slide 1):**
   - Large bold headline (2-3 lines max)
   - Subtitle or hook (1-2 lines)
   - Optional accent pill/badge with category
   - Minimal visual clutter

2. **Content Slide (Simple):**
   - Slide number indicator (top-left, small)
   - Bold section title (1 line, top)
   - Body text (3-5 lines, 18-22pt)
   - Optional accent shape (pill, tilted box) for emphasis

3. **Content Slide (Diagram/Visual):**
   - Title (top)
   - Central diagram or icon
   - Short supporting text (below diagram)
   - Arrows or connectors for flow

4. **List Slide:**
   - Title (top)
   - 3-5 bullet points with emoji or icon bullets
   - Consistent spacing between items

5. **Comparison Slide:**
   - Title (top)
   - Two columns (Before/After, Old/New, etc.)
   - Visual separator line or shape

6. **Stats/Numbers Slide:**
   - Large number (60-80pt, center)
   - Context label (above/below number)
   - Supporting text (bottom)

**Design Principles:**
- **Hierarchy:** Use size, weight, and color to guide the eye
- **White Space:** Don't crowd slides; leave breathing room
- **Consistency:** Repeat colors, fonts, and spacing patterns
- **Scannability:** Mobile users swipe fast; key info should be instantly readable
- **Accent Use:** Use accent colors sparingly for emphasis (10-20% of slide)

## Workflow: Text → PPTX → Images

### Step 1: Parse Carousel Text
Input format (from ChatGPT editor):
```
**Title: [Carousel Title]**

**Slide 1: [Slide Title]**

[Line 1]
[Line 2]
[Line 3]

---

**Slide 2: [Slide Title]**
...
```

Parse into structured data:
```json
{
  "title": "How Superhuman Actually Grows",
  "slides": [
    {
      "index": 1,
      "title": "The Real Reason Superhuman Grows",
      "lines": [
        "I triaged 80 emails in 12 minutes...",
        "Superhuman didn't grow because of AI...",
        "AI changed how value is delivered..."
      ]
    }
  ]
}
```

### Step 2: Generate PPTX
Use PptxGenJS to create slides programmatically:
```javascript
const pptx = new PptxGenJS();

// Slide 1 (Title)
let slide1 = pptx.addSlide();
slide1.background = { color: '4A1F2F' };
slide1.addText('SNEHA', { x: 0.5, y: 0.3, fontSize: 18, color: 'FFFFFF', bold: true });
slide1.addText(carouselTitle, { x: 0.5, y: 2.0, w: 9, fontSize: 48, color: 'FFFFFF', bold: true, align: 'center', valign: 'middle' });

// Slide 2+ (Content)
carouselData.slides.forEach(slide => {
  let s = pptx.addSlide();
  s.background = { color: '4A1F2F' };
  s.addText(`Slide ${slide.index}`, { x: 0.5, y: 0.3, fontSize: 14, color: 'F5E6D3' });
  s.addText(slide.title, { x: 0.5, y: 1.2, w: 9, fontSize: 36, color: 'FFFFFF', bold: true });

  let yPos = 2.5;
  slide.lines.forEach(line => {
    s.addText(line, { x: 0.5, y: yPos, w: 9, fontSize: 20, color: 'FFFFFF' });
    yPos += 0.6;
  });

  s.addText('@sneha', { x: 8.5, y: 7, fontSize: 12, color: 'F5E6D3' });
});

pptx.writeFile({ fileName: 'carousel.pptx' });
```

### Step 3: Convert PPTX to Images

**Method A: LibreOffice + pdftoppm (Best Quality)**
```bash
# Convert PPTX to PDF
soffice --headless --convert-to pdf carousel.pptx --outdir output/

# Convert PDF pages to images
pdftoppm -jpeg -r 300 output/carousel.pdf output/carousel

# Result: carousel-1.jpg, carousel-2.jpg, ...
```

**Method B: PowerPoint Automation (Windows/Mac)**
```bash
# macOS with PowerPoint installed
osascript -e 'tell application "Microsoft PowerPoint"
  open POSIX file "/path/to/carousel.pptx"
  save active presentation in "/path/to/output/" as save as PNG
end tell'
```

**Method C: Playwright + HTML Preview (Fallback)**
- Render each slide as HTML with exact dimensions
- Use Playwright to screenshot
- Lower quality but more portable

### Step 4: QA & Verification
Before finalizing:
- [ ] Text is fully readable on mobile (Instagram preview)
- [ ] Brand colors match guidelines
- [ ] Header and footer are consistent across slides
- [ ] Swipe indicator is visible
- [ ] No text is cut off or overlapping
- [ ] Accent elements are properly positioned
- [ ] Font sizes follow hierarchy
- [ ] Images are 1080x1080px or 1080x1350px (Instagram format)

## Implementation Checklist

### Phase 1: Setup
- [ ] Install PptxGenJS (`npm install pptxgenjs`)
- [ ] Install LibreOffice for conversion (`brew install --cask libreoffice` or `apt-get install libreoffice`)
- [ ] Install poppler-utils for pdftoppm (`brew install poppler` or `apt-get install poppler-utils`)

### Phase 2: Template Creation
- [ ] Create slide master templates for each style (burgundy, gray, green)
- [ ] Define reusable components (header, footer, accent shapes)
- [ ] Set up brand constants (colors, fonts, spacing)

### Phase 3: Content Parsing
- [ ] Parse ChatGPT-edited carousel text into JSON
- [ ] Validate structure (title, slides, lines)
- [ ] Handle edge cases (long titles, varying line counts)

### Phase 4: PPTX Generation
- [ ] Map parsed content to slide layouts
- [ ] Apply appropriate template based on content type (simple, list, stats, etc.)
- [ ] Generate PPTX file

### Phase 5: Conversion & Export
- [ ] Convert PPTX to PDF
- [ ] Convert PDF to high-res images (300 DPI)
- [ ] Optimize images for Instagram (1080x1080px, JPEG quality 90%)

### Phase 6: Testing & Iteration
- [ ] Generate test carousels for all 3 pillars
- [ ] Compare against training examples
- [ ] Iterate on spacing, font sizes, and colors
- [ ] Get user approval on final output

## Common Pitfalls

1. **Text Overflow:** Long text may not fit in defined space
   - Solution: Implement text truncation or dynamic font sizing

2. **Font Availability:** Custom fonts may not render correctly
   - Solution: Stick to web-safe fonts or embed fonts in PPTX

3. **Color Inconsistency:** Hex colors may appear differently in PowerPoint
   - Solution: Test colors in actual PowerPoint viewer

4. **Image Quality Loss:** Low-DPI conversion produces blurry images
   - Solution: Use 300 DPI for pdftoppm conversion

5. **Layout Shifts:** Text positioning may vary across PowerPoint versions
   - Solution: Use absolute positioning (inches) instead of relative

## Resources

- [PptxGenJS Documentation](https://gitbrent.github.io/PptxGenJS/docs/quick-start/)
- [PptxGenJS GitHub](https://github.com/gitbrent/PptxGenJS)
- [Instagram Image Size Guide](https://help.instagram.com/1631821640426723)
- [LibreOffice Headless Conversion](https://help.libreoffice.org/latest/en-US/text/shared/guide/startcenter.html)

## Next Steps

Once skill files are created, proceed to:
1. Analyze training carousel images to extract exact design patterns
2. Create PptxGenJS component library (header, footer, accent shapes)
3. Build content → layout mapping logic
4. Implement full pipeline (text → PPTX → images)
5. Test with Superhuman carousel and iterate
