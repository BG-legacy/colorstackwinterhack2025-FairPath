/**
 * Health & Version Service
 * Service for health checks and version information
 */
import apiClient from './apiClient';

/**
 * Health check response types
 */
export interface HealthStatus {
  status: 'ok' | 'healthy' | 'degraded';
  message?: string;
  model_loaded?: boolean;
  data_loaded?: boolean;
}

export interface VersionInfo {
  app_version: string;
  commit: string;
  dataset_version: string;
  model_version: string;
}

/**
 * GET / - Health check
 * Simple health check endpoint
 */
export const getHealthCheck = async (): Promise<HealthStatus> => {
  const response = await apiClient.get<HealthStatus>('/');
  return response.data;
};

/**
 * GET /health - Detailed health status
 * Returns detailed health information including model and data loading status
 */
export const getDetailedHealth = async (): Promise<HealthStatus> => {
  const response = await apiClient.get<HealthStatus>('/health');
  return response.data;
};

/**
 * GET /version - Version info
 * Returns version information for app, commit, dataset, and model
 */
export const getVersionInfo = async (): Promise<VersionInfo> => {
  const response = await apiClient.get<VersionInfo>('/version');
  return response.data;
};

/**
 * Health service object with all methods
 */
export const healthService = {
  getHealthCheck,
  getDetailedHealth,
  getVersionInfo,
};

export default healthService;






