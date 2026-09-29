import { reactive, ref, watch, type Ref } from 'vue'

/**
 * State daftar + pagination + filter dengan debounce untuk pencarian.
 *
 *   const list = usePagination(async (q) => userApi.list({ ...q, ...filters }), { search: '' })
 *   list.reload()  // dipanggil setelah create/update
 */
export function usePagination<T, F extends Record<string, unknown>>(
  fetcher: (q: { page: number; limit: number } & F) => Promise<{ data: T[]; meta: { page: number; limit: number; total: number; totalPages: number } }>,
  initialFilters: F,
  limit = 20,
) {
  const rows = ref([]) as Ref<T[]>
  const meta = ref({ page: 1, limit, total: 0, totalPages: 0 })
  const page = ref(1)
  const filters = reactive({ ...initialFilters }) as F
  const loading = ref(false)
  const error = ref('')

  let requestId = 0
  async function load() {
    const id = ++requestId
    loading.value = true
    error.value = ''
    try {
      const res = await fetcher({ page: page.value, limit, ...filters })
      if (id !== requestId) return
      rows.value = res.data
      meta.value = res.meta
    } catch (e) {
      if (id === requestId) error.value = e instanceof Error ? e.message : 'Gagal memuat data'
    } finally {
      if (id === requestId) loading.value = false
    }
  }

  let timer: ReturnType<typeof setTimeout> | undefined
  watch(
    () => ({ ...filters }),
    () => {
      clearTimeout(timer)
      timer = setTimeout(() => {
        if (page.value !== 1) page.value = 1
        else load()
      }, 300)
    },
    { deep: true },
  )
  watch(page, load)

  return { rows, meta, page, filters, loading, error, load, reload: load }
}
