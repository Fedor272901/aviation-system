import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для автоматической отправки токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log('[API Request]', {
    url: config.url,
    hasToken: !!token,
    tokenPreview: token ? token.substring(0, 30) + '...' : null,
  });

  if (token) {
    // Пробуем разные способы установки заголовка
    config.headers.set('Authorization', `Bearer ${token}`);
    console.log('[API] Set Authorization header:', `Bearer ${token.substring(0, 20)}...`);
  }
  return config;
});

// Интерцептор для обработки ошибок авторизации (временно отключён для отладки)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // console.log('API Error:', error.config?.url, error.response?.status);
    // const isAuthEndpoint = error.config?.url?.includes('/auth/login') ||
    //                       error.config?.url?.includes('/auth/register');

    // if (error.response?.status === 401 && !isAuthEndpoint) {
    //   localStorage.removeItem('token');
    //   localStorage.removeItem('user');
    //   window.location.href = '/login';
    // }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', { email, password }),

  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    middle_name?: string;
    phone?: string;
    passport: string;
  }) => api.post('/auth/register', data),

  me: () => api.get('/auth/me'),

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

export const personApi = {
  getAll: () => api.get<Person[]>('/persons/'),
};

export const flightApi = {
  getAll: () => api.get<Flight[]>('/flights/'),
  getAirports: () => api.get<Airport[]>('/flights/airports/'),
};
