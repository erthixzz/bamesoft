import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

/**
 * Exporta un nodo imprimible a PDF A4 **paginando por bloques**: captura cada
 * sección (hijo directo del contenedor) por separado y la coloca completa en la
 * página; si no cabe, salta a la siguiente. Así ninguna fila/sección se corta a
 * la mitad. Un bloque más alto que una página se divide solo como último recurso.
 */
export async function exportLifeSheetPdf(node: HTMLElement): Promise<Blob> {
  const root = (node.firstElementChild as HTMLElement) ?? node;
  const blocks = Array.from(root.children) as HTMLElement[];

  const pdf = new jsPDF({ unit: 'pt', format: 'a4' });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const M = 22; // margen (pt)
  const GAP = 8; // separación entre secciones
  const imgW = pageW - 2 * M;
  const usableH = pageH - 2 * M;
  let y = M;

  const render = (el: HTMLElement) =>
    html2canvas(el, { scale: 2, backgroundColor: '#ffffff', useCORS: true, logging: false });

  for (const el of blocks) {
    const canvas = await render(el);
    if (!canvas.width || !canvas.height) continue;
    const h = (canvas.height * imgW) / canvas.width;

    if (h <= usableH) {
      if (y + h > pageH - M) {
        pdf.addPage();
        y = M;
      }
      pdf.addImage(canvas.toDataURL('image/jpeg', 0.95), 'JPEG', M, y, imgW, h);
      y += h + GAP;
    } else {
      // Bloque más alto que una página: dividirlo en franjas (raro).
      if (y > M) {
        pdf.addPage();
        y = M;
      }
      const slicePx = (canvas.width * usableH) / imgW;
      let done = 0;
      let first = true;
      while (done < canvas.height) {
        const sh = Math.min(slicePx, canvas.height - done);
        const pc = document.createElement('canvas');
        pc.width = canvas.width;
        pc.height = sh;
        const ctx = pc.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(0, 0, pc.width, sh);
          ctx.drawImage(canvas, 0, done, canvas.width, sh, 0, 0, canvas.width, sh);
        }
        if (!first) pdf.addPage();
        pdf.addImage(pc.toDataURL('image/jpeg', 0.95), 'JPEG', M, M, imgW, (sh * imgW) / canvas.width);
        first = false;
        done += sh;
      }
      y = pageH; // fuerza nueva página para el siguiente bloque
    }
  }

  return pdf.output('blob');
}
