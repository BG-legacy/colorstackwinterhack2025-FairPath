/**
 * Outlook Service
 * Service for getting 5-10 year career outlook and assumptions
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';

/**
 * Growth outlook classification
 */
export type GrowthOutlook = 'Strong' | 'Moderate' | 'Declining' | 'Uncertain';

/**
 * Automation risk level
 */
export type AutomationRisk = 'Low' | 'Medium' | 'High' | 'Uncertain';

/**
 * Stability signal
 */
export type StabilitySignal = 'Expanding' | 'Shifting' | 'Declining' | 'Uncertain';

/**
 * Confidence level
 */
export type ConfidenceLevel = 'Low' | 'Medium' | 'High';

/**
 * Growth outlook details
 */
export interface GrowthOutlookData {
  outlook: GrowthOutlook;
  range: {
    growth_rate_percent?: number;
    employment_2024?: number;
    employment_2034?: number;
    annual_openings?: number;
  };
  confidence: ConfidenceLevel;
  reasoning: string;
}

/**
 * Automation risk details
 */
export interface AutomationRiskData {
  risk: AutomationRisk;
  confidence: ConfidenceLevel;
  reasoning: string;
}

/**
 * Stability signal details
 */
export interface StabilityData {
  signal: StabilitySignal;
  confidence: ConfidenceLevel;
  reasoning: string;
}

/**
 * Confidence indicator
 */
export interface ConfidenceIndicator {
  level: ConfidenceLevel;
  reasoning?: string;
  factors?: string[];
}

/**
 * Assumptions and limitations
 */
export interface AssumptionsAndLimitations {
  assumptions: string[];
  limitations: string[];
  data_sources?: string[];
  methodology?: string;
  last_updated?: string;
}

/**
 * Career outlook response
 */
export interface CareerOutlook {
  growth_outlook: GrowthOutlookData;
  automation_risk: AutomationRiskData;
  stability: StabilityData;
  confidence: ConfidenceIndicator;
  assumptions: AssumptionsAndLimitations;
}

/**
 * GET /api/outlook/{career_id} - Get 5-10 year outlook
 * Returns growth outlook, automation risk, stability signal, and confidence indicators
 */
export const getCareerOutlook = async (career_id: string): Promise<CareerOutlook> => {
  const response = await apiClient.get<BaseResponse<CareerOutlook>>(
    `/api/outlook/${career_id}`
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get career outlook');
  }

  return response.data.data!;
};

/**
 * GET /api/outlook/assumptions - Get assumptions and limitations
 * Returns documented assumptions and limitations for the outlook model
 */
export const getOutlookAssumptions = async (): Promise<AssumptionsAndLimitations> => {
  const response = await apiClient.get<BaseResponse<AssumptionsAndLimitations>>(
    '/api/outlook/assumptions'
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get outlook assumptions');
  }

  return response.data.data!;
};

/**
 * Outlook service object with all methods
 */
export const outlookService = {
  getCareerOutlook,
  getOutlookAssumptions,
};

export default outlookService;




