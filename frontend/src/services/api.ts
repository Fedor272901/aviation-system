import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для JWT (заготовка на будущее)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

export const personApi = {
  getAll: () => api.get<Person[]>('/persons/'),
};

export const flightApi = {
  getAll: () => api.get<Flight[]>('/flights/'),
  getAirports: () => api.get<Airport[]>('/flights/airports/'),
};