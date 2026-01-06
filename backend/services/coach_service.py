"""
Coach Service
Generates personalized next steps, plans, and roadmaps for career transitions
"""
import json
from typing import Dict, List, Optional, Any
from services.data_processing import DataProcessingService
from services.openai_enhancement import OpenAIEnhancementService
from services.paths_service import PathsService
from app.config import settings


class CoachService:
    """
    Service for generating coaching content:
    - 3 next actions (today)
    - 7-day plan
    - Learning roadmap (2-6 weeks)
    - Optional portfolio/interview steps
    """
    
    def __init__(self):
        self.data_service = DataProcessingService()
        self.openai_service = OpenAIEnhancementService()
        self.paths_service = PathsService()
        self._processed_data = None
    
    def load_processed_data(self) -> Dict[str, Any]:
        """Load processed data - caching it so we don't reload constantly"""
        if self._processed_data is None:
            self._processed_data = self.data_service.load_processed_data()
            if not self._processed_data:
                raise ValueError("Processed data not found. Run process_data.py first.")
        return self._processed_data
    
    def get_occupation_data(self, career_id: str) -> Optional[Dict[str, Any]]:
        """Get all processed data for a specific occupation"""
        processed_data = self.load_processed_data()
        
        for occ in processed_data["occupations"]:
            if occ["career_id"] == career_id:
                return occ
        
        return None
    
    def generate_next_steps(
        self,
        career_name: str,
        career_id: Optional[str] = None,
        user_skills: Optional[List[str]] = None,
        user_interests: Optional[Dict[str, float]] = None,
        user_work_values: Optional[Dict[str, float]] = None,
        include_portfolio: bool = False,
        include_interview: bool = False,
        career_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive coaching next steps
        
        Returns:
        - next_actions_today: List of 3 actionable items for today
        - seven_day_plan: List of daily activities for the next 7 days
        - learning_roadmap: Structured roadmap for 2-6 weeks
        - portfolio_steps: Optional portfolio building steps
        - interview_steps: Optional interview preparation steps
        """
        if not self.openai_service.is_available():
            return {
                "next_actions_today": [],
                "seven_day_plan": [],
                "learning_roadmap": {},
                "portfolio_steps": [] if include_portfolio else None,
                "interview_steps": [] if include_interview else None,
                "available": False,
                "message": "OpenAI service not available. Set OPENAI_API_KEY to enable coach mode."
            }
        
        try:
            # Build context about the career and user
            context_parts = [f"Target Career: {career_name}"]
            
            if career_data:
                # Add relevant career information
                education = career_data.get('education_data', {})
                if education.get('education_level'):
                    context_parts.append(f"Typical Education: {education.get('education_level')}")
                if education.get('typical_entry_education'):
                    context_parts.append(f"Entry Education: {education.get('typical_entry_education')}")
                
                outlook = career_data.get('outlook_features', {})
                if outlook.get('median_wage_2024'):
                    context_parts.append(f"Median Wage: ${outlook.get('median_wage_2024'):,.0f}")
                if outlook.get('growth_rate'):
                    context_parts.append(f"Growth Rate: {outlook.get('growth_rate'):.1f}%")
                
                # Add skills from career data if available
                skills = career_data.get('skills', [])
                if skills:
                    top_skills = [s.get('name', '') for s in skills[:10]]
                    context_parts.append(f"Key Skills: {', '.join(top_skills)}")
            
            if user_skills:
                context_parts.append(f"User's Current Skills: {', '.join(user_skills[:15])}")
            
            if user_interests:
                top_interests = sorted(user_interests.items(), key=lambda x: x[1], reverse=True)[:3]
                interests_text = ", ".join([f"{k} ({v})" for k, v in top_interests])
                context_parts.append(f"User's Interests: {interests_text}")
            
            context = "\n".join(context_parts)
            
            # Build instructions for optional sections
            optional_instructions = []
            portfolio_section = ""
            interview_section = ""
            
            if include_portfolio:
                portfolio_section = ',\n  "portfolio_steps": [\n    {\n      "step": 1,\n      "title": "Portfolio item title",\n      "description": "What to build/create",\n      "purpose": "Why this matters",\n      "estimated_time": "X hours/days",\n      "tips": ["Tip 1", "Tip 2"]\n    }\n  ]'
                optional_instructions.append("- portfolio_steps: Include practical projects/portfolio items relevant to the career")
            
            if include_interview:
                interview_section = ',\n  "interview_steps": [\n    {\n      "step": 1,\n      "title": "Interview preparation step",\n      "description": "What to prepare/practice",\n      "focus_areas": ["Area 1", "Area 2"],\n      "estimated_time": "X hours",\n      "practice_methods": ["Method 1", "Method 2"]\n    }\n  ]'
                optional_instructions.append("- interview_steps: Include preparation specific to this career field")
            
            # Build the prompt for comprehensive coaching
            prompt = f"""You're an expert career coach helping someone transition to this career. Generate a comprehensive action plan.

{context}

Provide a detailed coaching plan in this exact JSON format:
{{
  "next_actions_today": [
    {{
      "action": "Specific actionable task",
      "description": "Brief description of what to do",
      "estimated_time": "X minutes/hours",
      "priority": "high/medium/low"
    }}
  ],
  "seven_day_plan": [
    {{
      "day": 1,
      "date": "Day 1 (Today)",
      "focus": "Main focus for the day",
      "tasks": [
        {{
          "task": "Specific task description",
          "time_estimate": "X hours",
          "resources": ["Resource 1", "Resource 2"]
        }}
      ],
      "milestone": "What will be achieved by end of day"
    }}
  ],
  "learning_roadmap": {{
    "duration_weeks": 4,
    "overview": "Brief overview of the learning journey",
    "weeks": [
      {{
        "week": 1,
        "theme": "Theme/focus for this week",
        "learning_objectives": [
          "Objective 1",
          "Objective 2",
          "Objective 3"
        ],
        "key_activities": [
          "Activity 1 with description",
          "Activity 2 with description"
        ],
        "resources": [
          {{
            "name": "Resource name",
            "type": "course/book/article/video/project",
            "description": "Brief description",
            "url": "Optional URL if specific resource known"
          }}
        ],
        "milestones": [
          "Milestone to achieve by end of week"
        ]
      }}
    ]
  }}{portfolio_section}{interview_section}
}}

Guidelines:
- next_actions_today: Exactly 3 actionable items the user can do TODAY (within a few hours)
- seven_day_plan: 7 days of structured activities, each with 2-4 specific tasks
- learning_roadmap: 2-6 weeks (typically 4 weeks), with weekly themes and objectives
- Make everything specific, actionable, and realistic
- Focus on building skills, knowledge, and credentials needed for this career
{chr(10).join(optional_instructions) if optional_instructions else ""}
- Be encouraging but realistic about timelines and effort
- Include concrete resources when possible (but URLs are optional)

Return ONLY valid JSON, no other text."""
            
            # Get the correct max tokens parameter based on model
            max_tokens_param = self.openai_service.get_max_tokens_param(settings.OPENAI_MODEL, 4000)
            
            # Make the OpenAI API call
            try:
                response = self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're an expert career coach. Provide detailed, actionable coaching plans in JSON format only. Be specific, realistic, and encouraging."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
            except Exception as e:
                # Fallback if json_object format not supported
                print(f"JSON object format not supported, using regular format: {e}")
                response = self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're an expert career coach. Provide detailed, actionable coaching plans in JSON format only. Return ONLY valid JSON, no markdown, no code blocks."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7
                )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                
                # Ensure structure and validate
                coaching_data = {
                    "next_actions_today": result.get("next_actions_today", [])[:3],
                    "seven_day_plan": result.get("seven_day_plan", [])[:7],
                    "learning_roadmap": result.get("learning_roadmap", {}),
                    "portfolio_steps": result.get("portfolio_steps", []) if include_portfolio else None,
                    "interview_steps": result.get("interview_steps", []) if include_interview else None,
                    "available": True
                }
                
                # Validate we have the required data
                if len(coaching_data["next_actions_today"]) < 3:
                    coaching_data["available"] = False
                    coaching_data["message"] = "Generated fewer than 3 next actions"
                
                if len(coaching_data["seven_day_plan"]) < 7:
                    coaching_data["available"] = False
                    coaching_data["message"] = "Generated fewer than 7 days in plan"
                
                return coaching_data
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse coaching JSON: {e}")
                print(f"Response was: {result_text}")
                return {
                    "next_actions_today": [],
                    "seven_day_plan": [],
                    "learning_roadmap": {},
                    "portfolio_steps": [] if include_portfolio else None,
                    "interview_steps": [] if include_interview else None,
                    "available": False,
                    "error": "Failed to parse response"
                }
            
        except Exception as e:
            print(f"OpenAI coaching generation failed: {e}")
            return {
                "next_actions_today": [],
                "seven_day_plan": [],
                "learning_roadmap": {},
                "portfolio_steps": [] if include_portfolio else None,
                "interview_steps": [] if include_interview else None,
                "available": False,
                "error": str(e)
            }
    
    def get_next_steps(
        self,
        career_name: str,
        career_id: Optional[str] = None,
        user_skills: Optional[List[str]] = None,
        user_interests: Optional[Dict[str, float]] = None,
        user_work_values: Optional[Dict[str, float]] = None,
        include_portfolio: bool = False,
        include_interview: bool = False
    ) -> Dict[str, Any]:
        """
        Main method - get coaching next steps for a career transition
        
        Args:
            career_name: Name of the target career
            career_id: Optional career ID to get detailed career data
            user_skills: Optional list of user's current skills
            user_interests: Optional dict of user's interests (RIASEC)
            user_work_values: Optional dict of user's work values
            include_portfolio: Whether to include portfolio building steps
            include_interview: Whether to include interview preparation steps
        """
        career_data = None
        if career_id:
            career_data = self.get_occupation_data(career_id)
            if career_data and not career_name:
                career_name = career_data.get("name", career_name)
        
        # Generate coaching content
        coaching_result = self.generate_next_steps(
            career_name=career_name,
            career_id=career_id,
            user_skills=user_skills,
            user_interests=user_interests,
            user_work_values=user_work_values,
            include_portfolio=include_portfolio,
            include_interview=include_interview,
            career_data=career_data
        )
        
        if "error" in coaching_result:
            return coaching_result
        
        return {
            "career": {
                "career_id": career_id,
                "name": career_name
            },
            **coaching_result
        }

