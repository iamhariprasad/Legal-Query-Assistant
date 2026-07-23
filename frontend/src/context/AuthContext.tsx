import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, clearAuthToken, setAuthToken } from '../api/client';
import type { User } from '../types/api';

interface AuthContextValue {
  user: User | null | undefined; // undefined = loading, null = not logged in
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  error: Error | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, full_name: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  // Track whether we have a stored token - triggers re-render on login/logout
  const [hasToken, setHasToken] = useState<boolean>(() => {
    try {
      return !!localStorage.getItem('legal_assistant_token');
    } catch {
      return false;
    }
  });

  // Fetch current user if token exists (checked dynamically)
  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery<User>({
    queryKey: ['me'],
    queryFn: async () => (await apiClient.get<User>('/auth/me')).data,
    retry: false,
    enabled: hasToken,
    staleTime: 60_000,
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async (payload: { email: string; password: string }) =>
      (await apiClient.post<{ access_token: string }>('/auth/login', payload)).data,
    onSuccess: (data) => {
      setAuthToken(data.access_token);
      setHasToken(true);
      void queryClient.invalidateQueries({ queryKey: ['me'] });
      void refetch();
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async (payload: { email: string; full_name: string; password: string }) =>
      (await apiClient.post<User>('/auth/register', payload)).data,
  });

  const login = useCallback(
    async (email: string, password: string) => {
      await loginMutation.mutateAsync({ email, password });
    },
    [loginMutation],
  );

  const register = useCallback(
    async (email: string, full_name: string, password: string) => {
      // Register first, then login
      await registerMutation.mutateAsync({ email, full_name, password });
      await login(email, password);
    },
    [registerMutation, login],
  );

  const logout = useCallback(() => {
    clearAuthToken();
    setHasToken(false);
    queryClient.clear();
  }, [queryClient]);

  const clearError = useCallback(() => {
    loginMutation.reset();
    registerMutation.reset();
  }, [loginMutation, registerMutation]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      error: loginMutation.error || registerMutation.error || null,
      login,
      register,
      logout,
      clearError,
    }),
    [user, isLoading, loginMutation.error, registerMutation.error, login, register, logout, clearError],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
