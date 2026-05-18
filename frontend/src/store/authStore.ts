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

export const useAuthStore = create<AuthState>((set) => {
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
        const { data } = await authApi.login(credentials.email, credentials.password);

        localStorage.setItem('token', data.access_token);
        const { data: userData } = await authApi.me();
        localStorage.setItem('user', JSON.stringify(userData));

        set({
          token: data.access_token,
          user: userData,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (error: any) {
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
      if (!storedToken) {
        set({ isAuthenticated: false, user: null, token: null, isLoading: false });
        return;
      }
      try {
        const { data } = await authApi.me();
        set({ user: data, token: storedToken, isAuthenticated: true, isLoading: false });
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ isAuthenticated: false, user: null, token: null, isLoading: false });
      }
    },
  };
});
