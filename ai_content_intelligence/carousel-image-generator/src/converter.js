// ============================================
// PPTX → IMAGE CONVERTER
// Converts PPTX to high-quality JPG images
// ============================================
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

export async function convertPPTXToImages(pptxPath, outputDir = null) {
  if (!fs.existsSync(pptxPath)) {
    throw new Error(`PPTX file not found: ${pptxPath}`);
  }

  const dir = outputDir || path.dirname(pptxPath);
  const basename = path.basename(pptxPath, '.pptx');
  const pdfPath = path.join(dir, `${basename}.pdf`);

  console.log('');
  console.log('======================================');
  console.log('🔄 Converting PPTX → Images');
  console.log('======================================');

  // Step 1: Check if LibreOffice is installed
  console.log('1️⃣  Checking LibreOffice installation...');
  try {
    await execAsync('soffice --version');
    console.log('   ✓ LibreOffice found');
  } catch (err) {
    throw new Error('LibreOffice not installed. Install with: brew install --cask libreoffice (macOS) or apt-get install libreoffice (Linux)');
  }

  // Step 2: Convert PPTX → PDF
  console.log('2️⃣  Converting PPTX → PDF...');
  try {
    const { stdout, stderr } = await execAsync(
      `soffice --headless --convert-to pdf "${pptxPath}" --outdir "${dir}"`,
      { timeout: 120000 }
    );
    if (stderr && !stderr.includes('terminate')) {
      console.warn('   ⚠️  Warning:', stderr);
    }
    console.log('   ✓ PDF created:', pdfPath);
  } catch (err) {
    throw new Error(`Failed to convert PPTX → PDF: ${err.message}`);
  }

  // Step 3: Check if pdftoppm is installed
  console.log('3️⃣  Checking pdftoppm installation...');
  try {
    await execAsync('pdftoppm -v');
    console.log('   ✓ pdftoppm found');
  } catch (err) {
    throw new Error('pdftoppm not installed. Install with: brew install poppler (macOS) or apt-get install poppler-utils (Linux)');
  }

  // Step 4: Convert PDF → JPG images
  console.log('4️⃣  Converting PDF → JPG images (300 DPI)...');
  const imagePrefix = path.join(dir, basename);
  try {
    const { stdout, stderr } = await execAsync(
      `pdftoppm -jpeg -r 300 "${pdfPath}" "${imagePrefix}"`,
      { timeout: 120000 }
    );
    if (stderr) {
      console.warn('   ⚠️  Warning:', stderr);
    }
  } catch (err) {
    throw new Error(`Failed to convert PDF → images: ${err.message}`);
  }

  // Find all generated images
  const files = fs.readdirSync(dir);
  const imageFiles = files
    .filter(f => f.startsWith(path.basename(imagePrefix)) && f.endsWith('.jpg'))
    .sort()
    .map(f => path.join(dir, f));

  if (imageFiles.length === 0) {
    throw new Error('No images were generated. Check pdftoppm output.');
  }

  console.log(`   ✓ Generated ${imageFiles.length} images`);

  // Cleanup PDF
  if (fs.existsSync(pdfPath)) {
    fs.unlinkSync(pdfPath);
    console.log('   ✓ Cleaned up intermediate PDF');
  }

  console.log('');
  console.log('======================================');
  console.log('✅ Conversion Complete');
  console.log('======================================');
  imageFiles.forEach((img, idx) => {
    console.log(`   ${idx + 1}. ${path.basename(img)}`);
  });
  console.log('');

  return imageFiles;
}
