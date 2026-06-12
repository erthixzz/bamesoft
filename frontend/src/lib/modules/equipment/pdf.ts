import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

/**
 * Captura un nodo del DOM y produce un PDF tamaño A4 (paginado si excede una
 * página). Devuelve el Blob para descargar o subir al storage.
 */
export async function exportLifeSheetPdf(node: HTMLElement): Promise<Blob> {
  const canvas = await html2canvas(node, {
    scale: 2,
    backgroundColor: '#ffffff',
    useCORS: true,
    logging: false,
  });

  const pdf = new jsPDF({ unit: 'pt', format: 'a4' });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const imgW = pageW;
  const fullImgH = (canvas.height * imgW) / canvas.width;

  if (fullImgH <= pageH) {
    pdf.addImage(canvas.toDataURL('image/jpeg', 0.95), 'JPEG', 0, 0, imgW, fullImgH);
    return pdf.output('blob');
  }

  // Paginar: cortar el canvas en franjas de alto de página.
  const pageSlicePx = (canvas.width * pageH) / pageW;
  let renderedPx = 0;
  let first = true;
  while (renderedPx < canvas.height) {
    const sliceHeight = Math.min(pageSlicePx, canvas.height - renderedPx);
    const pageCanvas = document.createElement('canvas');
    pageCanvas.width = canvas.width;
    pageCanvas.height = sliceHeight;
    const ctx = pageCanvas.getContext('2d');
    if (ctx) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
      ctx.drawImage(canvas, 0, renderedPx, canvas.width, sliceHeight, 0, 0, canvas.width, sliceHeight);
    }
    const sliceImgH = (sliceHeight * imgW) / canvas.width;
    if (!first) pdf.addPage();
    pdf.addImage(pageCanvas.toDataURL('image/jpeg', 0.95), 'JPEG', 0, 0, imgW, sliceImgH);
    first = false;
    renderedPx += sliceHeight;
  }

  return pdf.output('blob');
}
