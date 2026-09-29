import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function usePagination(defaultLimit = 10) {
  const route = useRoute()
  const router = useRouter()

  const page = ref(Number(route.query.page) || 1)
  const limit = ref(Number(route.query.limit) || defaultLimit)
  const search = ref((route.query.search as string) || '')

  let debounceTimer: ReturnType<typeof setTimeout>
  function setSearch(value: string) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      search.value = value
      page.value = 1
    }, 300)
  }

  function setPage(p: number) {
    page.value = p
  }

  // sinkron ke query URL supaya bisa di-refresh/bagikan linknya
  watch([page, limit, search], () => {
    router.replace({
      query: { ...route.query, page: String(page.value), limit: String(limit.value), search: search.value || undefined },
    })
  })

  return { page, limit, search, setPage, setSearch }
}