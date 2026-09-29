import html2canvas from 'html2canvas-pro'
import { jsPDF } from 'jspdf'

/** Ubah elemen struk menjadi PDF selebar kertas thermal 80 mm. */
export function usePdf() {
  async function download(el: HTMLElement, filename: string) {
    const canvas = await html2canvas(el, { scale: 2, backgroundColor: '#ffffff' })
    const width = 80
    const height = (canvas.height * width) / canvas.width
    const pdf = new jsPDF({ unit: 'mm', format: [width, height], orientation: 'portrait' })
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, width, height)
    pdf.save(filename)
  }
  return { download }
}
