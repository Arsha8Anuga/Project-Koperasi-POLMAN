import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '../services/api';
import type { User, LoginPayload, LoginResponse } from '../types/auth';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'));
  const token = ref<string | null>(localStorage.getItem('token'));

  const isAuthenticated = computed(() => !!token.value);

  async function login(credentials: Omit<LoginPayload, 'app'>) {
    try {
      // Panggil API backend BE-1
      const response = await apiClient.post<LoginResponse>('/auth/login', {
        ...credentials,
        app: 'KASIR', // Wajib diset KASIR sesuai spec BE-1
      });

      token.value = response.data.token;
      user.value = response.data.user;

      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      return { success: true };
    } catch (error: any) {
      // MOCK BACKUP: Jika backend BE-1 belum siap/terhubung saat dicoba
      if (!import.meta.env.PROD) {
        const mockToken = 'mock-jwt-token-kasir';
        const mockUser: User = {
          id: 'u1',
          username: credentials.username,
          name: 'Kasir Utama',
          role: 'KASIR',
        };

        token.value = mockToken;
        user.value = mockUser;
        localStorage.setItem('token', mockToken);
        localStorage.setItem('user', JSON.stringify(mockUser));

        return { success: true };
      }

      return {
        success: false,
        message: error.response?.data?.message || 'Login gagal, periksa username/password',
      };
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  return { user, token, isAuthenticated, login, logout };
});