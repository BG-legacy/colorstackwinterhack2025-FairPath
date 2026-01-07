/**
 * Certifications Service
 * Service for getting certifications for careers
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';

/**
 * Certification details
 */
export interface Certification {
  name: string;
  issuer?: string;
  description?: string;
  cost?: number | { min?: number; max?: number };
  duration?: string;
  difficulty?: string;
  value?: string;
  rationale?: string; // For optional/overhyped certifications
  [key: string]: any;
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
 * Certifications response
 */
export interface CareerCertifications {
  career: CareerInfo;
  entry_level: Certification[];
  career_advancing: Certification[];
  optional_overhyped: Certification[];
  available: boolean;
}

/**
 * GET /api/certs/{career_id} - Get certifications
 * Returns entry-level, career-advancing, and optional/overhyped certifications for a specific career
 */
export const getCertifications = async (career_id: string): Promise<CareerCertifications> => {
  const response = await apiClient.get<BaseResponse<CareerCertifications>>(
    `/api/certs/${career_id}`
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get certifications');
  }

  return response.data.data!;
};

/**
 * Certifications service object with all methods
 */
export const certsService = {
  getCertifications,
};

export default certsService;




