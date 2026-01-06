/**
 * Resume Service
 * Service for resume analysis and rewriting
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';
import {
  validateFile,
  validateFileSize,
  validateFileType,
  validateFileMimeType,
  validateFilename,
  createFormData,
  createUploadConfig,
  MAX_FILE_SIZE,
  ALLOWED_FILE_TYPES,
  ALLOWED_MIME_TYPES,
  type FileValidationError,
  type AllowedFileType,
  type AllowedMimeType,
  type UploadProgressCallback,
} from '../utils/fileUpload';

// Re-export file upload utilities for backward compatibility
export {
  MAX_FILE_SIZE,
  ALLOWED_FILE_TYPES,
  ALLOWED_MIME_TYPES,
  validateFile,
  validateFileSize,
  validateFileType,
  validateFileMimeType,
  validateFilename,
  createFormData,
  createUploadConfig,
  type FileValidationError,
  type AllowedFileType,
  type AllowedMimeType,
  type UploadProgressCallback,
};

/**
 * Resume analysis response types
 */
export interface DetectedSkill {
  skill: string;
  confidence?: number;
  [key: string]: any;
}

export interface ResumeStructure {
  sections?: string[];
  bullets?: string[];
  [key: string]: any;
}

export interface GapAnalysis {
  target_career?: {
    career_id: string;
    name: string;
    user_input?: string;  // Original user input if different from matched name
  };
  missing_important_skills?: string[];
  missing_skills?: string[];
  matching_skills?: string[];
  recommended_skills?: string[];
  extra_skills?: string[];
  skill_gaps?: Array<{
    skill: string;
    importance: number;
    gap_level: 'low' | 'medium' | 'high';
    explanation?: string;
  }>;
  analysis_explanation?: string;
  coverage_percentage?: number;
  is_poor_match?: boolean;  // True if coverage is 0% or no skills match
  summary?: {
    resume_skills_count: number;
    target_skills_count: number;
    target_important_count: number;
    matching_count: number;
    missing_important_count: number;
  };
  error?: string;
  [key: string]: any;
}

export interface ResumeAnalysisResponse {
  extracted_text: string;
  detected_skills: DetectedSkill[];
  structure: ResumeStructure;
  gap_analysis: GapAnalysis | null;
  metadata: {
    filename: string;
    file_type: string;
    text_length: number;
    skills_count: number;
  };
}

/**
 * Resume rewrite request types
 */
export interface ResumeRewriteRequest {
  bullets: string[];
  target_career_id?: string;
  target_career_name?: string;
  resume_text?: string;
}

/**
 * Resume rewrite response types
 */
export interface BulletRewrite {
  original: string;
  rewritten: string;
  explanation?: string;
  compliance_note?: string;
  [key: string]: any;
}

export interface ResumeRewriteResponse {
  rewrites: BulletRewrite[];
  target_career: {
    career_id: string;
    name: string;
    [key: string]: any;
  };
  [key: string]: any;
}


/**
 * POST /api/resume/analyze - Analyze resume (file upload)
 * Accepts PDF, DOCX, or TXT files and returns:
 * - extracted text (not persisted)
 * - detected skills
 * - bullet list + sections
 * - gaps vs target career (if target_career_id provided)
 * 
 * PRIVACY: Resume content is processed entirely in-memory and never stored or logged.
 */
export const analyzeResume = async (
  file: File,
  targetCareerId?: string,
  targetCareerName?: string,
  onProgress?: UploadProgressCallback
): Promise<ResumeAnalysisResponse> => {
  // Validate file before upload
  const validationError = validateFile(file);
  if (validationError) {
    throw new Error(validationError.message);
  }

  // Create FormData for file upload with sanitized filename
  const additionalData: Record<string, string> = {};
  if (targetCareerId) {
    additionalData.target_career_id = targetCareerId;
  }
  if (targetCareerName) {
    additionalData.target_career_name = targetCareerName;
  }
  const formData = createFormData(file, Object.keys(additionalData).length > 0 ? additionalData : undefined);

  // Create upload config with progress tracking
  const uploadConfig = createUploadConfig(onProgress);

  // Use multipart/form-data for file upload
  // Note: Don't set Content-Type header - axios will set it automatically with boundary
  // The apiClient interceptor will detect multipart/form-data and set the upload timeout automatically
  const response = await apiClient.post<BaseResponse<ResumeAnalysisResponse>>(
    '/api/resume/analyze',
    formData,
    uploadConfig
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to analyze resume');
  }

  return response.data.data!;
};

/**
 * POST /api/resume/rewrite - Rewrite resume bullets
 * Rewrite resume bullets to better align with target career
 * 
 * Returns:
 * - before → after bullets
 * - explanation per rewrite
 * - "no fabrication" compliance notes
 * 
 * PRIVACY: Resume content is processed entirely in-memory and never stored or logged.
 */
export const rewriteResumeBullets = async (
  request: ResumeRewriteRequest
): Promise<ResumeRewriteResponse> => {
  // Validate request
  if (!request.bullets || request.bullets.length === 0) {
    throw new Error('At least one bullet point is required');
  }

  if ((!request.target_career_id || request.target_career_id.trim().length === 0) &&
      (!request.target_career_name || request.target_career_name.trim().length === 0)) {
    throw new Error('Either target career ID or target career name is required');
  }

  const response = await apiClient.post<BaseResponse<ResumeRewriteResponse>>(
    '/api/resume/rewrite',
    {
      bullets: request.bullets,
      target_career_id: request.target_career_id,
      target_career_name: request.target_career_name,
      resume_text: request.resume_text,
    }
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to rewrite resume bullets');
  }

  return response.data.data!;
};

/**
 * Resume service object with all methods
 */
export const resumeService = {
  analyzeResume,
  rewriteResumeBullets,
  // File validation methods (re-exported from fileUpload utilities)
  validateFile,
  validateFileSize,
  validateFileType,
  validateFileMimeType,
  validateFilename,
};

export default resumeService;

