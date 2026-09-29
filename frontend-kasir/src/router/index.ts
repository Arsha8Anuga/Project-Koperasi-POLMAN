import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginPage from '../pages/LoginPage.vue';
import PosPage from '../pages/PosPage.vue';

const routes = [
  { path: '/', redirect: '/pos' },
  { path: '/login', name: 'Login', component: LoginPage },
  { path: '/pos', name: 'Pos', component: PosPage, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ROUTE GUARD MODERN (Menggunakan return alih-alih next)
router.beforeEach((to) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'; // Lempar ke login jika belum terautentikasi
  }
  
  if (to.path === '/login' && authStore.isAuthenticated) {
    return '/pos'; // Lempar ke pos jika sudah login tetapi mencoba buka /login
  }
});

export default router;