/**
 * Coach Mutation Hooks
 * React Query mutation hooks for coaching endpoints
 */
import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import coachService, { CoachNextStepsRequest, CoachingNextSteps } from '../../services/coach';

/**
 * Get coaching next steps mutation
 */
export const useGetNextSteps = (
  options?: Omit<UseMutationOptions<CoachingNextSteps, Error, CoachNextStepsRequest>, 'mutationFn'>
) => {
  return useMutation({
    mutationFn: (request: CoachNextStepsRequest) => coachService.getNextSteps(request),
    ...options,
  });
};






