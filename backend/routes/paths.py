"""
API routes for education pathways
"""
from fastapi import APIRouter, HTTPException, status
from models.schemas import BaseResponse, ErrorResponse
from services.paths_service import PathsService

router = APIRouter()
paths_service = PathsService()


@router.get("/{career_id}", response_model=BaseResponse)
async def get_education_paths(career_id: str):
    """
    Get education pathways for a specific career
    
    Returns 3-5 pathways, each with:
    - name: Pathway name (e.g., "Traditional 4-Year Degree", "Bootcamp + Experience")
    - cost_range: Dictionary with min, max, currency, and description
    - time_range: Dictionary with min_months, max_months, and description
    - pros: List of advantages
    - tradeoffs: List of tradeoffs/downsides
    - description: Brief overview of the pathway
    """
    try:
        result = paths_service.get_education_paths(career_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    success=False,
                    message=result["error"]
                ).model_dump()
            )
        
        # Structure response according to requirements
        paths_data = {
            "career": result.get("career", {}),
            "pathways": result.get("pathways", []),
            "available": result.get("available", False)
        }
        
        return BaseResponse(
            success=True,
            message=f"Generated {len(paths_data['pathways'])} education pathways",
            data=paths_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                success=False,
                message="Failed to generate education pathways",
                error=str(e)
            ).model_dump()
        )







