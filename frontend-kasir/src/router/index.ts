import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginPage from '../pages/LoginPage.vue';
import PosPage from '../pages/PosPage.vue';
import PaymentPage from '../pages/PaymentPage.vue';
import InvoicePage from '../pages/InvoicePage.vue';
import HistoryPage from '../pages/HistoryPage.vue';

const routes = [
  { path: '/', redirect: '/pos' },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/pos', name: 'Pos', component: PosPage, meta: { requiresAuth: true } },
  { path: '/payment', name: 'Payment', component: PaymentPage, meta: { requiresAuth: true } },
  { path: '/invoice/:id', name: 'Invoice', component: InvoicePage, meta: { requiresAuth: true } },
  { path: '/history', name: 'History', component: HistoryPage, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login';
  }
  
  if (to.path === '/login' && authStore.isAuthenticated) {
    return '/pos';
  }
});

export default router;