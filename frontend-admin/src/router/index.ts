import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { appRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/auth/LoginPage.vue'),
      meta: { public: true, title: 'Masuk' },
    },
    { path: '/', component: () => import('@/layouts/DashboardLayout.vue'), children: appRoutes },
    {
      path: '/403',
      name: 'forbidden',
      component: () => import('@/pages/errors/ForbiddenPage.vue'),
      meta: { title: 'Akses Ditolak' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/errors/NotFoundPage.vue'),
      meta: { public: true, title: 'Tidak Ditemukan' },
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.name === 'login' && auth.isAuthenticated) return { name: 'dashboard' }
  if (to.meta.public) return true
  if (!auth.isAuthenticated) return { name: 'login', query: { redirect: to.fullPath } }

  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.clear()
      return { name: 'login' }
    }
  }

  const roles = to.meta.roles
  if (roles && !auth.hasRole(...roles)) return { name: 'forbidden' }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Admin Koperasi` : 'Admin Koperasi'
})

export default router
