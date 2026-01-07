/**
 * Recommendations Query Hooks
 * React Query hooks for recommendation endpoints
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import recommendationsService, {
  ModelStatusResponse,
} from '../../services/recommendations';

/**
 * Query keys factory for recommendations
 */
export const recommendationsQueryKeys = {
  all: ['recommendations'] as const,
  modelStatus: () => [...recommendationsQueryKeys.all, 'model', 'status'] as const,
};

/**
 * Get ML model status
 */
export const useModelStatus = (
  options?: Omit<UseQueryOptions<ModelStatusResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: recommendationsQueryKeys.modelStatus(),
    queryFn: () => recommendationsService.getModelStatus(),
    staleTime: 2 * 60 * 1000, // 2 minutes - model status can change
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    ...options,
  });
};




