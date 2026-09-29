import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { appRoutes } from './routes'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      meta: { public: true, title: 'Login' },
      component: () => import('@/pages/auth/LoginPage.vue'),
    },
    {
      path: '',
      component: () => import('@/layouts/DashboardLayout.vue'),
      children: appRoutes,
    },
    {
      path: '/403',
      name: 'forbidden',
      meta: { title: 'Akses Ditolak' },
      component: () => import('@/pages/errors/ForbiddenPage.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      meta: { public: true, title: 'Tidak Ditemukan' },
      component: () => import('@/pages/errors/NotFoundPage.vue'),
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.name === 'login' && auth.isAuthenticated) return '/'
  if (to.meta.public) return true
  if (!auth.isAuthenticated) return { path: '/login', query: { redirect: to.fullPath } }

  // token tersimpan tapi data user belum ada (habis refresh)
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { path: '/login' }
    }
  }

  const roles = to.meta.roles
  if (roles && !auth.hasRole(...roles)) return '/403'
  return true
})

export default router