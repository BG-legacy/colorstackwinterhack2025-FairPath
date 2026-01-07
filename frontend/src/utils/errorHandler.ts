/**
 * Error Handling Utilities
 * Centralized error handling, sanitization, and formatting
 */

import { ApiError } from '../services/apiClient';

/**
 * Sanitize error messages to prevent sensitive data exposure
 * Removes potential tokens, keys, paths, and other sensitive information
 */
export const sanitizeErrorMessage = (message: string): string => {
  if (typeof message !== 'string') {
    return 'An unexpected error occurred';
  }

  let sanitized = message;

  // Remove potential API keys/tokens (patterns like "key_...", "token_...", etc.)
  sanitized = sanitized.replace(/(?:(?:api[_-]?key|token|secret|password|auth)[\s:=]+)?[a-zA-Z0-9_-]{20,}/gi, '[REDACTED]');

  // Remove file paths (but keep error messages)
  sanitized = sanitized.replace(/\/[^\s]+\.(?:py|js|ts|json|txt|log)/g, '[FILE_PATH]');

  // Remove email addresses
  sanitized = sanitized.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]');

  // Remove IP addresses
  sanitized = sanitized.replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, '[IP_ADDRESS]');

  // Remove potential UUIDs
  sanitized = sanitized.replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '[UUID]');

  // Limit message length
  if (sanitized.length > 500) {
    sanitized = sanitized.substring(0, 500) + '...';
  }

  return sanitized.trim() || 'An unexpected error occurred';
};

/**
 * Format error for user display
 */
export const formatErrorForUser = (error: unknown): string => {
  if (error instanceof Error) {
    return sanitizeErrorMessage(error.message);
  }

  if (typeof error === 'string') {
    return sanitizeErrorMessage(error);
  }

  if (error && typeof error === 'object' && 'message' in error) {
    return sanitizeErrorMessage(String(error.message));
  }

  return 'An unexpected error occurred. Please try again.';
};

/**
 * Check if error is a network error
 */
export const isNetworkError = (error: unknown): boolean => {
  if (error && typeof error === 'object') {
    const apiError = error as ApiError;
    return apiError.code === 'NETWORK_ERROR' || apiError.code === 'ECONNABORTED';
  }
  return false;
};

/**
 * Check if error is a timeout error
 */
export const isTimeoutError = (error: unknown): boolean => {
  if (error && typeof error === 'object') {
    const apiError = error as ApiError;
    return apiError.code === 'ECONNABORTED' || apiError.message?.toLowerCase().includes('timeout');
  }
  return false;
};

/**
 * Get user-friendly error message based on error type
 */
export const getUserFriendlyErrorMessage = (error: unknown): string => {
  if (isNetworkError(error)) {
    return 'Unable to connect to the server. Please check your internet connection and try again.';
  }

  if (isTimeoutError(error)) {
    return 'The request took too long to complete. Please try again.';
  }

  if (error && typeof error === 'object' && 'status' in error) {
    const apiError = error as ApiError;
    const status = apiError.status;

    switch (status) {
      case 400:
        return 'Invalid request. Please check your input and try again.';
      case 401:
        return 'You are not authorized to perform this action. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 413:
        return 'The file you are trying to upload is too large. Please use a smaller file.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case 500:
        return 'An internal server error occurred. Please try again later.';
      case 502:
      case 503:
        return 'The server is temporarily unavailable. Please try again later.';
      case 504:
        return 'The server took too long to respond. Please try again.';
      default:
        return formatErrorForUser(error);
    }
  }

  return formatErrorForUser(error);
};




