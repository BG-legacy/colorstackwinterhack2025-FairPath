/**
 * Feedback API Service
 * Handles user feedback on career recommendations
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface FeedbackSubmission {
  user_id?: string;
  user_profile: {
    skills?: string[];
    interests?: Record<string, number>;
    values?: Record<string, number>;
    constraints?: Record<string, any>;
  };
  career_id: string;
  career_name: string;
  soc_code: string;
  feedback_type: 'selected' | 'liked' | 'disliked' | 'applied' | 'hired';
  predicted_score: number;
  metadata?: Record<string, any>;
}

export interface UserCareer {
  career_name: string;
  soc_code: string;
  feedback_type: string;
  added_date: string;
}

export interface PopularCareer {
  career_name: string;
  soc_code: string;
  total_selections: number;
  total_likes: number;
  total_hires: number;
}

export interface FeedbackStats {
  total_feedback: number;
  unique_users: number;
  unique_careers: number;
  feedback_types: Record<string, number>;
  avg_predicted_score?: number;
  popular_careers?: Record<string, number>;
}

/**
 * Submit user feedback on a career recommendation
 */
export async function submitFeedback(feedback: FeedbackSubmission): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/feedback/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
}

/**
 * Get careers selected/liked by a specific user
 */
export async function getUserCareers(userId: string): Promise<UserCareer[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/feedback/user-careers/${userId}`);

    if (!response.ok) {
      throw new Error(`Failed to get user careers: ${response.statusText}`);
    }

    const data = await response.json();
    return data.careers;
  } catch (error) {
    console.error('Error getting user careers:', error);
    throw error;
  }
}

/**
 * Get globally popular careers based on user feedback
 */
export async function getPopularCareers(topN: number = 20): Promise<PopularCareer[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/feedback/popular-careers?top_n=${topN}`);

    if (!response.ok) {
      throw new Error(`Failed to get popular careers: ${response.statusText}`);
    }

    const data = await response.json();
    return data.careers;
  } catch (error) {
    console.error('Error getting popular careers:', error);
    throw error;
  }
}

/**
 * Get feedback statistics
 */
export async function getFeedbackStats(): Promise<FeedbackStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/feedback/stats`);

    if (!response.ok) {
      throw new Error(`Failed to get feedback stats: ${response.statusText}`);
    }

    const data = await response.json();
    return data.stats;
  } catch (error) {
    console.error('Error getting feedback stats:', error);
    throw error;
  }
}






