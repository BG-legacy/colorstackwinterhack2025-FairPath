/**
 * Enhanced Mutation Hook with Automatic Toast Notifications
 * Wraps React Query mutations to automatically show success/error toasts
 */
import { useMutation, UseMutationOptions, UseMutationResult } from '@tanstack/react-query';
import { showSuccessToast, showErrorToast } from '../utils/toast';
import { ApiError } from '../services/apiClient';

interface MutationWithToastOptions<TData, TError, TVariables, TContext> 
  extends Omit<UseMutationOptions<TData, TError, TVariables, TContext>, 'onSuccess' | 'onError'> {
  successMessage?: string | ((data: TData, variables: TVariables) => string);
  errorMessage?: string;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  onSuccess?: (data: TData, variables: TVariables, context: TContext | undefined) => void | Promise<void>;
  onError?: (error: TError, variables: TVariables, context: TContext | undefined) => void | Promise<void>;
}

/**
 * Enhanced mutation hook that automatically shows toast notifications
 * 
 * @example
 * const mutation = useMutationWithToast({
 *   mutationFn: myService.createItem,
 *   successMessage: 'Item created successfully!',
 *   onSuccess: (data) => {
 *     // Custom success handler
 *   }
 * });
 */
export function useMutationWithToast<TData = unknown, TError = ApiError, TVariables = void, TContext = unknown>(
  options: MutationWithToastOptions<TData, TError, TVariables, TContext>
): UseMutationResult<TData, TError, TVariables, TContext> {
  const {
    successMessage,
    errorMessage,
    showSuccessToast: enableSuccessToast = true,
    showErrorToast: enableErrorToast = true,
    onSuccess: userOnSuccess,
    onError: userOnError,
    ...mutationOptions
  } = options;

  return useMutation<TData, TError, TVariables, TContext>({
    ...mutationOptions,
    onSuccess: (data, variables, context) => {
      // Show success toast if enabled
      if (enableSuccessToast && successMessage) {
        const message = typeof successMessage === 'function' 
          ? successMessage(data, variables)
          : successMessage;
        showSuccessToast(message);
      }

      // Call user's onSuccess handler
      if (userOnSuccess) {
        userOnSuccess(data, variables, context);
      }
    },
    onError: (error, variables, context) => {
      // Show error toast if enabled (default error handler will also show, but this gives custom messages)
      if (enableErrorToast && errorMessage) {
        showErrorToast(errorMessage);
      } else if (enableErrorToast) {
        // Fallback to default error handling
        showErrorToast(error);
      }

      // Call user's onError handler
      if (userOnError) {
        userOnError(error, variables, context);
      }
    },
  });
}




