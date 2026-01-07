/**
 * Career Switch Query Hooks
 * React Query hooks for career switch analysis
 */
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import careerSwitchService, { SkillOverlap } from '../../services/careerSwitch';

/**
 * Query keys factory for career switch
 */
export const careerSwitchQueryKeys = {
  all: ['career-switch'] as const,
  overlap: (source: string, target: string) => [...careerSwitchQueryKeys.all, 'overlap', source, target] as const,
};

/**
 * Get skill overlap between two careers
 */
export const useSkillOverlap = (
  sourceCareerId: string,
  targetCareerId: string,
  options?: Omit<UseQueryOptions<SkillOverlap>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: careerSwitchQueryKeys.overlap(sourceCareerId, targetCareerId),
    queryFn: () => careerSwitchService.getSkillOverlap(sourceCareerId, targetCareerId),
    enabled: !!sourceCareerId && !!targetCareerId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    ...options,
  });
};




