// ============================================
// DYNAMIC CAROUSEL GENERATOR
// Takes JSON carousel data and generates PPTX
// ============================================
import PptxGenJS from 'pptxgenjs';
import { COLORS, LAYOUT, FONTS, makeGlassBg, makeGlassBorder } from './design-system.js';
import { createGradientBg } from './background.js';
import { addBrandHeader, addSwipeCue, addGlassCard } from './components.js';

const { W, H, PAD, CONTENT_W } = LAYOUT;

export async function generateCarousel(carouselData, outputPath) {
  const pres = new PptxGenJS();
  pres.defineLayout({ name: "INSTAGRAM", width: W, height: H });
  pres.layout = "INSTAGRAM";
  pres.author = "Sneha";
  pres.title = carouselData.title;

  const bgData = await createGradientBg();

  // Slide 1: Title/Cover Slide
  await buildTitleSlide(pres, bgData, carouselData);

  // Slides 2+: Content Slides
  for (let i = 0; i < carouselData.slides.length; i++) {
    await buildContentSlide(pres, bgData, carouselData.slides[i], i, carouselData.slides.length);
  }

  // Save
  await pres.writeFile({ fileName: outputPath });
  console.log(`✅ Carousel generated: ${outputPath}`);
  return outputPath;
}

// ============================================
// SLIDE BUILDERS
// ============================================

async function buildTitleSlide(pres, bgData, carouselData) {
  const slide = pres.addSlide();
  slide.background = { data: bgData };
  addBrandHeader(slide);

  // Extract pillar type from data for categorization
  const pillar = carouselData.pillar || "pillar_01";
  const pillarLabels = {
    "pillar_01": "GROWTH LOOPS",
    "pillar_02": "MEASUREMENT GAP",
    "pillar_03": "THINKING LAYER"
  };

  // Main title (split into max 4 lines for readability)
  const titleLines = splitTitle(carouselData.title);
  slide.addText(titleLines.join("\n"), {
    x: PAD,
    y: 1.2,
    w: CONTENT_W,
    h: 4.2,
    fontFace: FONTS.DISPLAY,
    fontSize: titleLines.length > 3 ? 60 : 72,
    color: COLORS.gold,
    bold: true,
    lineSpacingMultiple: 0.85,
    margin: 0,
  });

  // Category pill
  const pillarLabel = pillarLabels[pillar] || "ANALYSIS";
  const pillW = 3;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: (W - pillW) / 2,
    y: 6.0,
    w: pillW,
    h: 0.5,
    fill: { color: COLORS.cream },
    line: { type: 'none' },
    rectRadius: 0.25
  });
  slide.addText(pillarLabel, {
    x: (W - pillW) / 2,
    y: 6.0,
    w: pillW,
    h: 0.5,
    fontSize: 14,
    bold: true,
    color: COLORS.burgundyDeep,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  // First slide content preview (if available)
  if (carouselData.slides && carouselData.slides.length > 0) {
    const firstLine = carouselData.slides[0].text_lines[0];
    if (firstLine) {
      addGlassCard(slide, pres, PAD, 7.0, CONTENT_W * 0.9, 1.2, { leftAccent: true });
      slide.addText(truncateText(firstLine, 120), {
        x: PAD + 0.35,
        y: 7.1,
        w: CONTENT_W * 0.9 - 0.7,
        h: 1.0,
        fontFace: FONTS.BODY,
        fontSize: 20,
        color: COLORS.cream,
        valign: "middle",
        margin: 0,
      });
    }
  }

  addSwipeCue(slide);
}

async function buildContentSlide(pres, bgData, slideData, index, totalSlides) {
  const slide = pres.addSlide();
  slide.background = { data: bgData };
  addBrandHeader(slide);

  // Slide number indicator
  slide.addText(`${index + 1}/${totalSlides}`, {
    x: PAD,
    y: 0.8,
    fontSize: 12,
    color: COLORS.clay,
    margin: 0,
  });

  // Slide title (if exists)
  let contentStartY = 2.5;
  if (slideData.title) {
    const titleFontSize = slideData.title.length > 60 ? 28 : 32;
    slide.addText(slideData.title, {
      x: PAD,
      y: 1.2,
      w: CONTENT_W,
      fontSize: titleFontSize,
      bold: true,
      color: COLORS.gold,
      fontFace: FONTS.DISPLAY,
      lineSpacingMultiple: 1.1,
      margin: 0,
    });
    contentStartY = 2.3;
  }

  // Content lines
  const lines = slideData.text_lines || [];
  let yPos = contentStartY;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isLongLine = line.length > 200;
    const fontSize = isLongLine ? 18 : 20;
    const lineHeight = isLongLine ? 0.8 : 0.7;

    slide.addText(line, {
      x: PAD,
      y: yPos,
      w: CONTENT_W,
      fontSize: fontSize,
      color: COLORS.cream,
      fontFace: FONTS.BODY,
      lineSpacingMultiple: 1.3,
      margin: 0,
    });

    yPos += lineHeight;

    // Stop if running out of space
    if (yPos > H - 2.5) break;
  }

  // Add accent element (varies per slide for visual interest)
  if (index % 3 === 0) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 7.5,
      y: 1.5,
      w: 2,
      h: 1.2,
      fill: { color: COLORS.cream, transparency: 90 },
      line: { type: 'none' },
      rotate: 5
    });
  } else if (index % 3 === 1) {
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.3,
      y: H - 2.5,
      w: 2.5,
      h: 0.5,
      fill: { color: COLORS.warmAccent, transparency: 85 },
      line: { type: 'none' },
      rectRadius: 0.25
    });
  }

  addSwipeCue(slide);
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function splitTitle(title) {
  // Split title into lines (max 4 lines, max ~25 chars per line for readability)
  const words = title.toUpperCase().split(' ');
  const lines = [];
  let currentLine = '';

  for (const word of words) {
    if ((currentLine + ' ' + word).trim().length > 25 && currentLine.length > 0) {
      lines.push(currentLine.trim());
      currentLine = word;
    } else {
      currentLine = currentLine ? currentLine + ' ' + word : word;
    }
  }

  if (currentLine) lines.push(currentLine.trim());

  // If too many lines, combine some
  if (lines.length > 4) {
    const combined = [];
    for (let i = 0; i < lines.length; i += 2) {
      combined.push(lines.slice(i, i + 2).join(' '));
    }
    return combined.slice(0, 4);
  }

  return lines;
}

function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}
