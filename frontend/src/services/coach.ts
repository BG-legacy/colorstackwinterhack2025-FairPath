/**
 * Coach Service
 * Service for getting personalized coaching next steps and learning roadmaps
 */
import apiClient from './apiClient';
import { BaseResponse } from './types';

/**
 * RIASEC interest categories
 */
export type RIASECCategory =
  | 'Realistic'
  | 'Investigative'
  | 'Artistic'
  | 'Social'
  | 'Enterprising'
  | 'Conventional';

/**
 * Work values
 */
export type WorkValue =
  | 'Achievement'
  | 'Working Conditions'
  | 'Recognition'
  | 'Relationships'
  | 'Support'
  | 'Independence';

/**
 * Coach next steps request
 */
export interface CoachNextStepsRequest {
  career_name: string;
  career_id?: string;
  user_skills?: string[];
  user_interests?: Record<RIASECCategory, number>; // 0-7 scale
  user_work_values?: Record<WorkValue, number>; // 0-7 scale
  include_portfolio?: boolean;
  include_interview?: boolean;
}

/**
 * Next action item
 */
export interface NextAction {
  action: string;
  description: string;
  estimated_time: string;
  priority: 'high' | 'medium' | 'low';
}

/**
 * Day task in 7-day plan
 */
export interface DayTask {
  task: string;
  time_estimate: string;
  resources?: string[];
}

/**
 * Day in 7-day plan
 */
export interface SevenDayPlanDay {
  day: number;
  date: string;
  focus: string;
  tasks: DayTask[];
  milestone: string;
}

/**
 * Learning resource
 */
export interface LearningResource {
  name: string;
  type: 'course' | 'book' | 'article' | 'video' | 'project' | string;
  description: string;
  url?: string;
}

/**
 * Week in learning roadmap
 */
export interface LearningRoadmapWeek {
  week: number;
  theme: string;
  learning_objectives: string[];
  key_activities: string[];
  resources: LearningResource[];
  milestones: string[];
}

/**
 * Learning roadmap
 */
export interface LearningRoadmap {
  duration_weeks: number;
  overview: string;
  weeks: LearningRoadmapWeek[];
}

/**
 * Portfolio step
 */
export interface PortfolioStep {
  step: number;
  title: string;
  description: string;
  purpose: string;
  estimated_time: string;
  tips?: string[];
}

/**
 * Interview step
 */
export interface InterviewStep {
  step: number;
  title: string;
  description: string;
  focus_areas: string[];
  estimated_time: string;
  practice_methods?: string[];
}

/**
 * Career information
 */
export interface CareerInfo {
  career_id?: string;
  name: string;
  soc_code?: string;
}

/**
 * Coaching next steps response
 */
export interface CoachingNextSteps {
  career: CareerInfo;
  next_actions_today: NextAction[];
  seven_day_plan: SevenDayPlanDay[];
  learning_roadmap: LearningRoadmap;
  portfolio_steps?: PortfolioStep[];
  interview_steps?: InterviewStep[];
}

/**
 * POST /api/coach/next-steps - Get coaching next steps
 * Returns personalized coaching plan with next actions, 7-day plan, learning roadmap, and optional portfolio/interview steps
 */
export const getNextSteps = async (
  request: CoachNextStepsRequest
): Promise<CoachingNextSteps> => {
  const response = await apiClient.post<BaseResponse<CoachingNextSteps>>(
    '/api/coach/next-steps',
    request
  );

  if (!response.data.success) {
    throw new Error(response.data.message || 'Failed to get coaching next steps');
  }

  return response.data.data!;
};

/**
 * Coach service object with all methods
 */
export const coachService = {
  getNextSteps,
};

export default coachService;




