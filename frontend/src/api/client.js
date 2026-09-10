import axios from 'axios';

// Base Production URLs
const BASE_RENDER_URL = 'https://nearby-watch.onrender.com';
const BASE_WS_URL = 'wss://nearby-watch.onrender.com';

export const API_URL = import.meta.env.VITE_API_URL || `${BASE_RENDER_URL}/api`;
export const WS_URL = import.meta.env.VITE_WS_URL || BASE_WS_URL;

const ACCESS_KEY = 'lf_access_token';
const REFRESH_KEY = 'lf_refresh_token';

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// Single Axios Client Instance
export const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let refreshPromise = null;

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    const isAuthCall = originalRequest?.url?.startsWith('/auth/');

    if (status === 401 && !originalRequest._retry && !isAuthCall) {
      originalRequest._retry = true;
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearTokens();
        return Promise.reject(error);
      }

      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken })
            .then((res) => {
              setTokens(res.data);
              return res.data.access_token;
            })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const newAccessToken = await refreshPromise;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return client(originalRequest);
      } catch (refreshError) {
        clearTokens();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default client;