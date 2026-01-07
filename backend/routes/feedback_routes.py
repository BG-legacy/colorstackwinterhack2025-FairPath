"""
Feedback API Routes
Endpoints for collecting user feedback on career recommendations
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
feedback_service = FeedbackService()


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    user_id: Optional[str] = Field(None, description="User ID (optional, can be anonymous)")
    user_profile: Dict[str, Any] = Field(..., description="User's profile (skills, interests, values)")
    career_id: str = Field(..., description="Career identifier")
    career_name: str = Field(..., description="Career name")
    soc_code: str = Field(..., description="SOC code")
    feedback_type: str = Field(..., description="Type: selected, liked, disliked, applied, hired")
    predicted_score: float = Field(..., description="Score that was shown (0.0-1.0)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CareerListResponse(BaseModel):
    """Response model for career lists"""
    careers: List[Dict[str, Any]]
    total: int


@router.post("/submit")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback on a career recommendation
    
    Example:
        POST /api/feedback/submit
        {
            "user_id": "user123",
            "user_profile": {
                "skills": ["Python", "Data Analysis"],
                "interests": {"Investigative": 7.0},
                "values": {"impact": 6.0}
            },
            "career_id": "15-2041.00",
            "career_name": "Biostatistician",
            "soc_code": "15-2041.00",
            "feedback_type": "selected",
            "predicted_score": 0.92,
            "metadata": {
                "ranking_position": 1,
                "time_to_decision_seconds": 45
            }
        }
    """
    try:
        success = feedback_service.record_feedback(
            user_id=feedback.user_id,
            user_profile=feedback.user_profile,
            career_id=feedback.career_id,
            career_name=feedback.career_name,
            soc_code=feedback.soc_code,
            feedback_type=feedback.feedback_type,
            predicted_score=feedback.predicted_score,
            metadata=feedback.metadata
        )
        
        if success:
            return {
                "success": True,
                "message": "Feedback recorded successfully",
                "career_name": feedback.career_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-careers/{user_id}")
async def get_user_careers(user_id: str) -> CareerListResponse:
    """
    Get careers selected/liked by a specific user
    
    Example:
        GET /api/feedback/user-careers/user123
    """
    try:
        careers = feedback_service.get_user_careers(user_id)
        return CareerListResponse(
            careers=careers,
            total=len(careers)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popular-careers")
async def get_popular_careers(top_n: int = 20) -> CareerListResponse:
    """
    Get globally popular careers based on user feedback
    
    Example:
        GET /api/feedback/popular-careers?top_n=10
    """
    try:
        careers = feedback_service.get_popular_careers(top_n=top_n)
        return CareerListResponse(
            careers=careers,
            total=len(careers)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_feedback_stats():
    """
    Get statistics about collected feedback
    
    Example:
        GET /api/feedback/stats
    """
    try:
        stats = feedback_service.get_feedback_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain-trigger")
async def trigger_retraining(
    min_samples: int = Body(50, description="Minimum feedback samples needed")
):
    """
    Trigger model retraining (admin endpoint)
    
    Example:
        POST /api/feedback/retrain-trigger
        {
            "min_samples": 50
        }
    """
    try:
        # Import here to avoid circular dependencies
        from scripts.retrain_model import ModelRetrainingService
        
        retrainer = ModelRetrainingService()
        result = retrainer.retrain_model(
            min_feedback_samples=min_samples,
            save_model=True
        )
        
        return {
            "success": result["success"],
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






