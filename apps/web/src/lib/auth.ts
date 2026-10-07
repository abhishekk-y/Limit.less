import axios from 'axios';
import { API_BASE } from './api-base';

export const TOKEN_KEY = 'skillsetu_token';
export const REFRESH_TOKEN_KEY = 'skillsetu_refresh_token';

export const getToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const getRefreshToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setToken = (token: string, refreshToken?: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
    if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
};

export const removeToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
};

export const isAuthenticated = () => {
  return !!getToken();
};

let refreshInFlight: Promise<string> | null = null;

const performRefresh = async () => {
  try {
    const refresh = getRefreshToken();
    if (!refresh) throw new Error('No refresh token');
    const res = await axios.post(`${API_BASE}/auth/refresh`, {
      refresh_token: refresh,
    });
    setToken(res.data.access_token, res.data.refresh_token);
    return res.data.access_token as string;
  } catch (error) {
    removeToken();
    throw error;
  }
};

export const refreshToken = () => {
  if (!refreshInFlight) refreshInFlight = performRefresh().finally(() => { refreshInFlight = null; });
  return refreshInFlight;
};

