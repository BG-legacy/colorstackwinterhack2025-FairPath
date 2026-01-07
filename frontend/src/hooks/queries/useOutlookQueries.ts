/**
 * Outlook Query Hooks
 * React Query hooks for career outlook endpoints
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import outlookService, {
  CareerOutlook,
  AssumptionsAndLimitations,
} from '../../services/outlook';

/**
 * Query keys factory for outlook
 */
export const outlookQueryKeys = {
  all: ['outlook'] as const,
  career: (careerId: string) => [...outlookQueryKeys.all, 'career', careerId] as const,
  assumptions: () => [...outlookQueryKeys.all, 'assumptions'] as const,
};

/**
 * Get career outlook for a specific career
 */
export const useCareerOutlook = (
  careerId: string,
  options?: Omit<UseQueryOptions<CareerOutlook>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: outlookQueryKeys.career(careerId),
    queryFn: () => outlookService.getCareerOutlook(careerId),
    enabled: !!careerId, // Only fetch if careerId is provided
    staleTime: 10 * 60 * 1000, // 10 minutes - outlook data doesn't change frequently
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};

/**
 * Get outlook assumptions and limitations
 */
export const useOutlookAssumptions = (
  options?: Omit<UseQueryOptions<AssumptionsAndLimitations>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: outlookQueryKeys.assumptions(),
    queryFn: () => outlookService.getOutlookAssumptions(),
    staleTime: 60 * 60 * 1000, // 1 hour - assumptions rarely change
    gcTime: 24 * 60 * 60 * 1000, // 24 hours
    ...options,
  });
};




