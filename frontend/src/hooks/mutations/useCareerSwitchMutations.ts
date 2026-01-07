/**
 * Career Switch Mutation Hooks
 * React Query mutation hooks for career switch endpoints
 */
import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import careerSwitchService, {
  CareerSwitchRequest,
  CareerSwitchAnalysis,
  CareerSwitchFormatted,
} from '../../services/careerSwitch';

/**
 * Analyze career switch mutation
 */
export const useAnalyzeCareerSwitch = (
  options?: Omit<UseMutationOptions<CareerSwitchAnalysis, Error, CareerSwitchRequest>, 'mutationFn'>
) => {
  return useMutation({
    mutationFn: (request: CareerSwitchRequest) =>
      careerSwitchService.analyzeCareerSwitch(request),
    ...options,
  });
};

/**
 * Get career switch mutation (formatted)
 */
export const useGetCareerSwitch = (
  options?: Omit<UseMutationOptions<CareerSwitchFormatted, Error, CareerSwitchRequest>, 'mutationFn'>
) => {
  return useMutation({
    mutationFn: (request: CareerSwitchRequest) =>
      careerSwitchService.getCareerSwitch(request),
    ...options,
  });
};




