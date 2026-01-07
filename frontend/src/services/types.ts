/**
 * Common API response types
 */

/**
 * Base response structure from the API
 */
export interface BaseResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

/**
 * Error response structure from the API
 */
export interface ErrorResponse {
  success: false;
  message: string;
  error?: string;
  details?: Record<string, any>;
}




