import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/pages/LoginPage.vue'), meta: { public: true } },
    {
      path: '/',
      component: () => import('@/layouts/PosLayout.vue'),
      children: [
        { path: '', redirect: { name: 'pos' } },
        { path: 'pos', name: 'pos', component: () => import('@/pages/PosPage.vue') },
        { path: 'payment', name: 'payment', component: () => import('@/pages/PaymentPage.vue') },
        { path: 'invoice/:id', name: 'invoice', component: () => import('@/pages/InvoicePage.vue') },
        { path: 'history', name: 'history', component: () => import('@/pages/HistoryPage.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'pos' } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) return auth.isAuthenticated && to.name === 'login' ? { name: 'pos' } : true
  if (!auth.isAuthenticated) return { name: 'login', query: { redirect: to.fullPath } }
  return true
})

export default router
