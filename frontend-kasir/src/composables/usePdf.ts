import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

export function usePdf() {
  async function download(el: HTMLElement, filename: string) {
    const canvas = await html2canvas(el, { scale: 2, backgroundColor: '#ffffff' })
    const imgData = canvas.toDataURL('image/png')

    const pageWidth = 80 // mm
    const pageHeight = (canvas.height * pageWidth) / canvas.width

    const pdf = new jsPDF({
      unit: 'mm',
      format: [pageWidth, pageHeight],
      orientation: pageHeight > pageWidth ? 'portrait' : 'landscape',
    })
    pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, pageHeight)
    pdf.save(filename)
  }

  return { download }
}