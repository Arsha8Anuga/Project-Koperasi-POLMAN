import { toast } from 'vue-sonner'

/**
 * Notifikasi singkat (Sonner dari shadcn-vue). Pesan error dari backend boleh langsung ditampilkan.
 * Toaster-nya dipasang sekali di App.vue.
 */
export function useToast() {
  return {
    success: (message: string) => toast.success(message),
    info: (message: string) => toast.info(message),
    error: (message: string) => toast.error(message, { duration: 6000 }),
  }
}
