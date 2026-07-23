import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 120_000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('legal_assistant_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401 / expired token
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const token = localStorage.getItem('legal_assistant_token');
      if (token) {
        localStorage.removeItem('legal_assistant_token');
        // Redirect to home — AuthContext will pick up the missing token
        if (window.location.pathname !== '/') {
          window.location.href = '/';
        }
      }
    }
    return Promise.reject(error);
  },
);

export function setAuthToken(token: string): void {
  localStorage.setItem('legal_assistant_token', token);
}

export function clearAuthToken(): void {
  localStorage.removeItem('legal_assistant_token');
}
