/**
 * Paths Query Hooks
 * React Query hooks for education pathways
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import pathsService, { EducationPathways } from '../../services/paths';

/**
 * Query keys factory for paths
 */
export const pathsQueryKeys = {
  all: ['paths'] as const,
  pathways: (careerId: string) => [...pathsQueryKeys.all, 'pathways', careerId] as const,
};

/**
 * Get education pathways for a career
 */
export const useEducationPathways = (
  careerId: string,
  options?: Omit<UseQueryOptions<EducationPathways>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: pathsQueryKeys.pathways(careerId),
    queryFn: () => pathsService.getEducationPathways(careerId),
    enabled: !!careerId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};






