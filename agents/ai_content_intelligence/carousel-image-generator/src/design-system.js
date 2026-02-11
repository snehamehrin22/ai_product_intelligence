// ============================================
// DESIGN SYSTEM - Brand Colors, Fonts, Layout
// ============================================

export const COLORS = {
  burgundyDeep: "3B0510",
  burgundyMid: "5A1025",
  burgundyLight: "7A2040",
  cream: "F4F4F1",
  gold: "D4B896",
  clay: "E1DBD7",
  warmAccent: "A0674B",
  glassBorder: "F4F4F1",
  white20: "FFFFFF",
};

// Custom slide size: 10" x 12.5" (maps to 1080x1350 at 108dpi)
export const LAYOUT = {
  W: 10,
  H: 12.5,
  PAD: 0.7, // side padding
  get CONTENT_W() {
    return this.W - this.PAD * 2;
  }
};

// Typography
export const FONTS = {
  DISPLAY: "Georgia",
  BODY: "Georgia",
  BRAND: "Arial",
};

// Reusable factory functions (avoid object reuse pitfall)
export const makeShadow = () => ({
  type: "outer",
  blur: 12,
  offset: 4,
  angle: 135,
  color: "000000",
  opacity: 0.25,
});

export const makeGlassBg = () => ({
  color: COLORS.cream,
  transparency: 92,
});

export const makeGlassBorder = () => ({
  color: COLORS.cream,
  width: 1,
  transparency: 80,
});
