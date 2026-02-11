// ============================================
// BACKGROUND HELPER - Generate gradient backgrounds
// ============================================
import sharp from 'sharp';

export async function createGradientBg() {
  // Create a radial gradient using sharp
  const w = 1080;
  const h = 1350;

  // Create SVG with radial gradient
  const svg = `<svg width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <radialGradient id="bg" cx="50%" cy="38%" r="70%">
        <stop offset="0%" stop-color="#5A1025"/>
        <stop offset="55%" stop-color="#3B0510"/>
        <stop offset="100%" stop-color="#1a0308"/>
      </radialGradient>
    </defs>
    <rect width="${w}" height="${h}" fill="url(#bg)"/>
  </svg>`;

  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}
