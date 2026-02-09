// ============================================
// REUSABLE SLIDE COMPONENTS
// ============================================
import { COLORS, LAYOUT, FONTS } from './design-system.js';

const { W, H, PAD, CONTENT_W } = LAYOUT;

export function addBrandHeader(slide) {
  slide.addText("SNEHA", {
    x: 0,
    y: 0.35,
    w: W,
    h: 0.4,
    fontFace: FONTS.BRAND,
    fontSize: 18,
    color: COLORS.cream,
    bold: true,
    align: "center",
    charSpacing: 4,
    margin: 0,
  });
}

export function addSwipeCue(slide) {
  slide.addText("›››››", {
    x: W - PAD - 1,
    y: H - 0.8,
    w: 1,
    h: 0.4,
    fontFace: FONTS.BRAND,
    fontSize: 22,
    color: COLORS.clay,
    align: "right",
    bold: true,
    transparency: 50,
    margin: 0,
  });
}

export function addGlassCard(slide, pres, x, y, w, h, opts = {}) {
  const {
    fillTransparency = 92,
    borderTransparency = 80,
    rectRadius = 0.1,
    leftAccent = false,
    accentColor = COLORS.cream
  } = opts;

  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: COLORS.cream, transparency: fillTransparency },
    line: { color: COLORS.cream, width: 1, transparency: borderTransparency },
    rectRadius,
  });

  if (leftAccent) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x,
      y: y + 0.1,
      w: 0.04,
      h: h - 0.2,
      fill: { color: accentColor, transparency: 70 },
    });
  }
}
