/**
 * Guarded Recommendations Service
 * Service for getting career recommendations with ML guardrails applied
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';

/**
 * Guarded recommendation request types
 */
export interface GuardedRecommendationConstraints {
  min_wage?: number;
  remote_preferred?: boolean;
  max_education_level?: number;
  [key: string]: any;
}

export interface GuardedRecommendationRequest {
  skills?: string[];
  skill_importance?: Record<string, number>; // 0-5 scale
  interests?: Record<string, number>; // RIASEC categories, 0-7 scale
  work_values?: Record<string, number>; // 0-7 scale
  constraints?: GuardedRecommendationConstraints;
  top_n?: number; // 1-20, default 5
  use_ml?: boolean; // default true
}

/**
 * Guarded recommendation response types
 */
export interface GuardedRecommendation {
  career_id: string;
  name: string;
  soc_code: string;
  score: number;
  confidence: 'Low' | 'Med' | 'High';
  explanation?: {
    method: string;
    confidence: 'Low' | 'Med' | 'High';
    top_contributing_skills?: Array<{
      feature: string;
      contribution: number;
      user_value: number;
      career_value: number;
    }>;
    why_points?: string[];
    [key: string]: any;
  };
  [key: string]: any;
}

export interface GuardedRecommendationsResponse {
  recommendations: GuardedRecommendation[];
  total_count: number;
  method: 'ml_model' | 'baseline';
  user_features?: {
    num_skills_provided: number;
    interests_provided: boolean;
    values_provided: boolean;
    constraints_provided: boolean;
  };
  [key: string]: any;
}

/**
 * Guardrails information response
 */
export interface GuardrailsInfo {
  guardrails: string[];
  demographic_keywords_blocked: string[];
  minimum_recommendations: number;
  default_recommendations: number;
}

/**
 * Simple guarded recommendations query parameters
 */
export interface SimpleGuardedRecommendationsParams {
  skills?: string; // Comma-separated list of skills
  top_n?: number; // 1-20, default 5
}

/**
 * POST /api/recommendations-guarded/recommend - Guarded recommendations
 * Get career recommendations with ML guardrails applied
 * 
 * Guardrails:
 * - No demographic features accepted
 * - Always returns multiple recommendations (minimum 3)
 * - Includes uncertainty ranges and confidence indicators
 * - Fallback behavior for thin/empty inputs
 */
export const getGuardedRecommendations = async (
  request: GuardedRecommendationRequest
): Promise<GuardedRecommendationsResponse> => {
  const response = await apiClient.post<BaseResponse<GuardedRecommendationsResponse>>(
    '/api/recommendations-guarded/recommend',
    {
      skills: request.skills,
      skill_importance: request.skill_importance,
      interests: request.interests,
      work_values: request.work_values,
      constraints: request.constraints,
      top_n: request.top_n ?? 5,
      use_ml: request.use_ml ?? true,
    }
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get guarded recommendations');
  }

  return response.data.data!;
};

/**
 * GET /api/recommendations-guarded/recommend/simple - Simple guarded recommendations
 * Simple recommendation endpoint with guardrails
 * Just provide skills as comma-separated string
 */
export const getSimpleGuardedRecommendations = async (
  params: SimpleGuardedRecommendationsParams
): Promise<GuardedRecommendationsResponse> => {
  const queryParams: Record<string, string | number> = {};

  if (params.skills) {
    queryParams.skills = params.skills;
  }

  if (params.top_n !== undefined) {
    queryParams.top_n = params.top_n;
  }

  const response = await apiClient.get<BaseResponse<GuardedRecommendationsResponse>>(
    '/api/recommendations-guarded/recommend/simple',
    {
      params: queryParams,
    }
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get simple guarded recommendations');
  }

  return response.data.data!;
};

/**
 * GET /api/recommendations-guarded/guardrails/info - Guardrails information
 * Get information about ML guardrails in place
 */
export const getGuardrailsInfo = async (): Promise<GuardrailsInfo> => {
  const response = await apiClient.get<BaseResponse<GuardrailsInfo>>(
    '/api/recommendations-guarded/guardrails/info'
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get guardrails information');
  }

  return response.data.data!;
};

/**
 * Guarded recommendations service object with all methods
 */
export const recommendationsGuardedService = {
  getGuardedRecommendations,
  getSimpleGuardedRecommendations,
  getGuardrailsInfo,
};

export default recommendationsGuardedService;






