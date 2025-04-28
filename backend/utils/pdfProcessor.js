/**
 * FILE: pdfProcessor.js
 * DESCRIPTION:
 *   Generates a stylized PDF from Grok responses preserving formatting.
 */


const { PDFDocument, rgb, StandardFonts } = require('pdf-lib');
const fs = require('fs');
const path = require('path');

async function generateResponsePDF(plain, mid, deep, outputPath = null) {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([600, 800]);
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

  const content = `Plain:\n${plain}\n\nMid:\n${mid}\n\nDeep:\n${deep}`;
  page.drawText(content, {
    x: 50,
    y: 750,
    size: 12,
    font,
    color: rgb(0, 0, 0)
  });

  const pdfBytes = await pdfDoc.save();

  if (outputPath) {
    const filePath = path.resolve(outputPath, `response_${Date.now()}.pdf`);
    fs.writeFileSync(filePath, pdfBytes);
    return filePath;
  } else {
    return pdfBytes;
  }
}

module.exports = { generateResponsePDF };
