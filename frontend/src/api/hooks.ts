import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, setAuthToken } from './client';
import type {
  ChatHistoryItem,
  ChatResponse,
  EvaluationResultsResponse,
  GuardrailLog,
  HealthResponse,
  LegalSearchResponse,
  Metric,
  User,
} from '../types/api';

export function useCurrentUser() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => (await apiClient.get<User>('/auth/me')).data,
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) =>
      (await apiClient.post<{ access_token: string }>('/auth/login', payload)).data,
    onSuccess: (data) => {
      setAuthToken(data.access_token);
      void queryClient.invalidateQueries({ queryKey: ['me'] });
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; full_name: string; password: string }) =>
      (await apiClient.post<User>('/auth/register', payload)).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['me'] });
    },
  });
}

export function useChatMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (query: string) =>
      (await apiClient.post<ChatResponse>('/chat/query', { query })).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['history'] });
    },
  });
}

export function useHistory() {
  return useQuery({
    queryKey: ['history'],
    queryFn: async () => (await apiClient.get<ChatHistoryItem[]>('/chat/history')).data,
  });
}

export function useLegalSearch() {
  return useMutation({
    mutationFn: async (query: string) =>
      (await apiClient.post<LegalSearchResponse>('/search/legal', { query })).data,
  });
}

export function useEvaluation() {
  return useQuery({
    queryKey: ['evaluation'],
    queryFn: async () => (await apiClient.get<EvaluationResultsResponse>('/evaluation/results')).data,
  });
}

export function useAdminMetrics() {
  return useQuery({
    queryKey: ['admin-metrics'],
    queryFn: async () => (await apiClient.get<Metric[]>('/admin/metrics')).data,
  });
}

export function useGuardrails() {
  return useQuery({
    queryKey: ['guardrails'],
    queryFn: async () => (await apiClient.get<GuardrailLog[]>('/admin/guardrails')).data,
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => (await apiClient.get<HealthResponse>('/health')).data,
    staleTime: 30_000,
  });
}

export function useSubmitFeedback() {
  return useMutation({
    mutationFn: async (payload: { chat_id: string; rating: number; comment?: string }) =>
      (await apiClient.post('/feedback', payload)).data,
  });
}
