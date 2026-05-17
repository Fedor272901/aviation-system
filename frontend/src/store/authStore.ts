import { create } from 'zustand';
import { authApi } from '../services/api';
import type { AuthUser, LoginCredentials, RegisterData } from '../types';

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => {
  // Проверяем сохранённый токен при старте
  const storedToken = localStorage.getItem('token');
  const storedUser = localStorage.getItem('user');

  return {
    user: storedUser ? JSON.parse(storedUser) : null,
    token: storedToken,
    isAuthenticated: !!storedToken,
    isLoading: false,

    login: async (credentials: LoginCredentials) => {
      set({ isLoading: true });
      try {
        console.log('Login attempt:', credentials.email);
        const { data } = await authApi.login(credentials.email, credentials.password);

        console.log('Login success, token received:', data.access_token.substring(0, 20) + '...');

        // Сначала сохраняем токен в localStorage
        localStorage.setItem('token', data.access_token);


        // Получаем данные пользователя с уже сохранённым токеном
        const { data: userData } = await authApi.me();
        console.log('User data:', userData);
        localStorage.setItem('user', JSON.stringify(userData));

        set({
          token: data.access_token,
          user: userData,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error: any) {
        console.error('Login error:', error);
        console.error('Error response:', error.response?.data);
        set({ isLoading: false });
        throw error;
      }
    },

    register: async (data: RegisterData) => {
      set({ isLoading: true });
      try {
        const { data: userData } = await authApi.register(data);

        // Логинимся сразу после регистрации
        const { data: tokenData } = await authApi.login(data.email, data.password);

        localStorage.setItem('token', tokenData.access_token);
        localStorage.setItem('user', JSON.stringify(userData));

        set({
          token: tokenData.access_token,
          user: userData,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error) {
        set({ isLoading: false });
        throw error;
      }
    },

    logout: () => {
      authApi.logout();
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      });
    },

    checkAuth: async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');

      if (!storedToken) {
        set({ isAuthenticated: false, user: null, token: null });
        return;
      }

      try {
        const { data } = await authApi.me();
        localStorage.setItem('user', JSON.stringify(data));
        set({
          user: data,
          token: storedToken,
          isAuthenticated: true,
        });
      } catch (err: any) {
        if (err.response?.status === 401) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          set({ isAuthenticated: false, user: null, token: null });
        }
      }
    },
  };
});
