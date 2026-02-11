#!/usr/bin/env node
// ============================================
// FULL PIPELINE: JSON → PPTX → IMAGES
// Usage: node src/generate-images.js <path-to-carousel-json>
// ============================================
import fs from 'fs';
import path from 'path';
import { generateCarousel } from './generator.js';
import { convertPPTXToImages } from './converter.js';

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('❌ Usage: node src/generate-images.js <path-to-carousel-json>');
    console.error('Example: node src/generate-images.js ../data/carousel_outputs/Superhuman_pillar_01_growth_loops_are_changing.json');
    process.exit(1);
  }

  const inputPath = args[0];

  if (!fs.existsSync(inputPath)) {
    console.error(`❌ File not found: ${inputPath}`);
    process.exit(1);
  }

  console.log('');
  console.log('======================================');
  console.log('🎨 CAROUSEL IMAGE GENERATOR');
  console.log('======================================');
  console.log('');

  // Step 1: Load carousel data
  console.log('📚 Loading carousel data...');
  const carouselData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  console.log(`   ✓ Title: ${carouselData.title}`);
  console.log(`   ✓ Slides: ${carouselData.slides?.length || 0}`);

  // Step 2: Generate PPTX
  const inputFilename = path.basename(inputPath, '.json');
  const outputDir = path.join(path.dirname(inputPath), '..', 'carousel_images');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  const pptxPath = path.join(outputDir, `${inputFilename}.pptx`);

  console.log('');
  console.log('🎨 Generating PPTX...');
  await generateCarousel(carouselData, pptxPath);

  // Step 3: Convert to images
  const imageFiles = await convertPPTXToImages(pptxPath, outputDir);

  console.log('======================================');
  console.log('✅ ALL DONE!');
  console.log('======================================');
  console.log(`📁 Images saved to: ${outputDir}`);
  console.log(`🖼️  Total images: ${imageFiles.length}`);
  console.log('');
}

main().catch(err => {
  console.error('');
  console.error('❌ Error:', err.message);
  console.error('');
  if (err.stack) {
    console.error(err.stack);
  }
  process.exit(1);
});
