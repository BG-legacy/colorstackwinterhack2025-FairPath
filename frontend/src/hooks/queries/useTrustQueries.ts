/**
 * Trust Query Hooks
 * React Query hooks for trust panel and model cards
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import trustService, { TrustPanelData, ModelCardsData } from '../../services/trust';

/**
 * Query keys factory for trust
 */
export const trustQueryKeys = {
  all: ['trust'] as const,
  trustPanel: () => [...trustQueryKeys.all, 'trust-panel'] as const,
  modelCards: () => [...trustQueryKeys.all, 'model-cards'] as const,
};

/**
 * Get trust panel data
 */
export const useTrustPanel = (
  options?: Omit<UseQueryOptions<TrustPanelData>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: trustQueryKeys.trustPanel(),
    queryFn: () => trustService.getTrustPanel(),
    staleTime: 60 * 60 * 1000, // 1 hour - trust panel rarely changes
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    ...options,
  });
};

/**
 * Get model cards data
 */
export const useModelCards = (
  options?: Omit<UseQueryOptions<ModelCardsData>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: trustQueryKeys.modelCards(),
    queryFn: () => trustService.getModelCards(),
    staleTime: 60 * 60 * 1000, // 1 hour - model cards rarely change
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    ...options,
  });
};






