import axios from 'axios';
import { getToken, refreshToken, removeToken } from './auth';
import { API_BASE } from './api-base';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !originalRequest.url?.startsWith('/auth/')) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshToken();
        if (newToken) {
          api.defaults.headers.common.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (e) {
        removeToken();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
