/**
 * Resume Mutation Hooks
 * React Query mutation hooks for resume endpoints
 */
import { useMutation, UseMutationOptions } from '@tanstack/react-query';
import resumeService, {
  ResumeAnalysisResponse,
  ResumeRewriteRequest,
  ResumeRewriteResponse,
} from '../../services/resume';

/**
 * Analyze resume mutation
 */
export const useAnalyzeResume = (
  options?: Omit<UseMutationOptions<ResumeAnalysisResponse, Error, { file: File; targetCareerId?: string }>, 'mutationFn'>
) => {
  return useMutation({
    mutationFn: ({ file, targetCareerId }) =>
      resumeService.analyzeResume(file, targetCareerId),
    ...options,
  });
};

/**
 * Rewrite resume bullets mutation
 * Optimistic update: We can show the rewritten bullets immediately
 */
export const useRewriteResumeBullets = (
  options?: Omit<UseMutationOptions<ResumeRewriteResponse, Error, ResumeRewriteRequest>, 'mutationFn' | 'onMutate'>
) => {
  return useMutation({
    mutationFn: (request: ResumeRewriteRequest) =>
      resumeService.rewriteResumeBullets(request),
    // Optimistic update: We could show a loading state with the original bullets
    // while the rewrite is in progress
    ...options,
  });
};






