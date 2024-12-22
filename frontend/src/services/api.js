import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
};

export const tradesAPI = {
  getTrades: () => api.get('/api/trades'),
  createTrade: (tradeData) => api.post('/api/trades', tradeData),
  closeTrade: (tradeId) => api.put(`/api/trades/${tradeId}/close`),
};

export const userAPI = {
  getProfile: () => api.get('/api/users/me'),
  updateProfile: (userData) => api.put('/api/users/me', userData),
};

export default api; 