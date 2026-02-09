#!/usr/bin/env node
// ============================================
// MAIN ENTRY POINT
// Usage: node src/index.js <path-to-carousel-json>
// ============================================
import fs from 'fs';
import path from 'path';
import { generateCarousel } from './generator.js';

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('❌ Usage: node src/index.js <path-to-carousel-json>');
    console.error('Example: node src/index.js ../data/carousel_outputs/Superhuman_pillar_01_growth_loops_are_changing.json');
    process.exit(1);
  }

  const inputPath = args[0];

  if (!fs.existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    process.exit(1);
  }

  console.log('📚 Loading carousel data...');
  const carouselData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

  console.log(`✓ Title: ${carouselData.title}`);
  console.log(`✓ Slides: ${carouselData.slides?.length || 0}`);

  // Generate output path
  const inputFilename = path.basename(inputPath, '.json');
  const outputDir = path.join(path.dirname(inputPath), '..', 'carousel_images');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const outputPath = path.join(outputDir, `${inputFilename}.pptx`);

  console.log('🎨 Generating PPTX carousel...');
  await generateCarousel(carouselData, outputPath);

  console.log('');
  console.log('======================================');
  console.log('✅ PPTX Generated Successfully');
  console.log('======================================');
  console.log(`📁 Output: ${outputPath}`);
  console.log('');
  console.log('Next steps:');
  console.log('1. Open the PPTX in PowerPoint to verify');
  console.log('2. Convert to images:');
  console.log(`   soffice --headless --convert-to pdf "${outputPath}" --outdir "${path.dirname(outputPath)}"`);
  console.log(`   pdftoppm -jpeg -r 300 "${outputPath.replace('.pptx', '.pdf')}" "${outputPath.replace('.pptx', '')}"`);
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  console.error(err.stack);
  process.exit(1);
});
