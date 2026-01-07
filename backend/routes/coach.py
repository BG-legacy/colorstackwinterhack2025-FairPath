"""
API routes for coach mode
"""
from fastapi import APIRouter, HTTPException, status, Body
from models.schemas import BaseResponse, ErrorResponse
from services.coach_service import CoachService
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

router = APIRouter()
coach_service = CoachService()


class CoachNextStepsRequest(BaseModel):
    """Request schema for coach next steps"""
    career_name: str = Field(..., description="Name of the target career")
    career_id: Optional[str] = Field(None, description="Optional career ID for detailed data")
    user_skills: Optional[List[str]] = Field(None, description="List of user's current skills")
    user_interests: Optional[Dict[str, float]] = Field(
        None,
        description="Dict mapping RIASEC categories to scores (0-7). Categories: Realistic, Investigative, Artistic, Social, Enterprising, Conventional"
    )
    user_work_values: Optional[Dict[str, float]] = Field(
        None,
        description="Dict mapping work values to scores (0-7). Values: Achievement, Working Conditions, Recognition, Relationships, Support, Independence"
    )
    include_portfolio: bool = Field(False, description="Whether to include portfolio building steps")
    include_interview: bool = Field(False, description="Whether to include interview preparation steps")


@router.post("/next-steps", response_model=BaseResponse)
async def get_next_steps(request: CoachNextStepsRequest = Body(...)):
    """
    Get coaching next steps for a career transition
    
    Returns:
    - next_actions_today: 3 actionable items for today
    - seven_day_plan: Daily activities for the next 7 days
    - learning_roadmap: Structured roadmap for 2-6 weeks (with weekly themes, objectives, activities, resources, milestones)
    - portfolio_steps: Optional portfolio building steps (if include_portfolio=true)
    - interview_steps: Optional interview preparation steps (if include_interview=true)
    """
    try:
        result = coach_service.get_next_steps(
            career_name=request.career_name,
            career_id=request.career_id,
            user_skills=request.user_skills,
            user_interests=request.user_interests,
            user_work_values=request.user_work_values,
            include_portfolio=request.include_portfolio,
            include_interview=request.include_interview
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    success=False,
                    message=result.get("error", "Failed to generate coaching next steps")
                ).model_dump()
            )
        
        if not result.get("available", False):
            # Service not available (e.g., OpenAI not configured)
            return BaseResponse(
                success=False,
                message=result.get("message", "Coach mode not available"),
                data=result
            )
        
        # Structure response according to requirements
        coaching_data = {
            "career": result.get("career", {}),
            "next_actions_today": result.get("next_actions_today", []),
            "seven_day_plan": result.get("seven_day_plan", []),
            "learning_roadmap": result.get("learning_roadmap", {}),
            "portfolio_steps": result.get("portfolio_steps"),
            "interview_steps": result.get("interview_steps")
        }
        
        return BaseResponse(
            success=True,
            message=f"Generated coaching plan with {len(coaching_data['next_actions_today'])} next actions, 7-day plan, and {coaching_data['learning_roadmap'].get('duration_weeks', 0)}-week roadmap",
            data=coaching_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                message="Failed to generate coaching next steps",
                error=str(e)
            ).model_dump()
        )







