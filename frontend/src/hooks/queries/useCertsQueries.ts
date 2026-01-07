/**
 * Certifications Query Hooks
 * React Query hooks for certifications
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import certsService, { CareerCertifications } from '../../services/certs';

/**
 * Query keys factory for certifications
 */
export const certsQueryKeys = {
  all: ['certs'] as const,
  certifications: (careerId: string) => [...certsQueryKeys.all, 'certifications', careerId] as const,
};

/**
 * Get certifications for a career
 */
export const useCertifications = (
  careerId: string,
  options?: Omit<UseQueryOptions<CareerCertifications>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: certsQueryKeys.certifications(careerId),
    queryFn: () => certsService.getCertifications(careerId),
    enabled: !!careerId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};






