/**
 * Paths Service
 * Service for getting education pathways for careers
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';

/**
 * Cost range for a pathway
 */
export interface CostRange {
  min: number;
  max: number;
  currency: string;
  description?: string;
}

/**
 * Time range for a pathway
 */
export interface TimeRange {
  min_months: number;
  max_months: number;
  description?: string;
}

/**
 * Education pathway
 */
export interface EducationPathway {
  name: string;
  cost_range: CostRange;
  time_range: TimeRange;
  pros: string[];
  tradeoffs: string[];
  description: string;
}

/**
 * Career information
 */
export interface CareerInfo {
  career_id: string;
  name: string;
  soc_code?: string;
}

/**
 * Education pathways response
 */
export interface EducationPathways {
  career: CareerInfo;
  pathways: EducationPathway[];
  available: boolean;
}

/**
 * GET /api/paths/{career_id} - Get education pathways
 * Returns 3-5 education pathways for a specific career, each with cost, time, pros, and tradeoffs
 */
export const getEducationPathways = async (career_id: string): Promise<EducationPathways> => {
  const response = await apiClient.get<BaseResponse<EducationPathways>>(
    `/api/paths/${career_id}`
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get education pathways');
  }

  return response.data.data!;
};

/**
 * Paths service object with all methods
 */
export const pathsService = {
  getEducationPathways,
};

export default pathsService;




