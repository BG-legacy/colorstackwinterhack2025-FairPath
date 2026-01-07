"""
Unit tests for schema validation for all endpoint responses
Tests that all endpoints return data matching BaseResponse schema
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from models.schemas import BaseResponse, ErrorResponse
from app.main import app
from unittest.mock import Mock, patch, MagicMock
import json


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestEndpointSchemaValidation:
    """Test suite for endpoint schema validation"""
    
    def test_base_response_schema(self):
        """Test BaseResponse schema structure"""
        response = BaseResponse(
            success=True,
            message="Test message",
            data={"key": "value"}
        )
        
        # Should be valid Pydantic model
        assert response.success == True
        assert response.message == "Test message"
        assert response.data == {"key": "value"}
        
        # Should serialize to dict
        response_dict = response.model_dump()
        assert "success" in response_dict
        assert "message" in response_dict
        assert "data" in response_dict
    
    def test_error_response_schema(self):
        """Test ErrorResponse schema structure"""
        response = ErrorResponse(
            success=False,
            message="Error message",
            error="Error details"
        )
        
        assert response.success == False
        assert response.message == "Error message"
        assert response.error == "Error details"
    
    @patch('routes.recommendations.recommendation_service')
    def test_recommendations_endpoint_schema(self, mock_service, client):
        """Test /api/recommendations endpoint response schema"""
        # Mock the service response
        mock_service.get_enhanced_recommendations.return_value = {
            "careers": [
                {
                    "career_id": "test_001",
                    "name": "Test Career",
                    "confidence_band": {"level": "High", "min": 0.75, "max": 0.85},
                    "explainability": {"top_features": []},
                    "why": "Test explanation"
                }
            ],
            "alternatives": [],
            "method": "baseline"
        }
        
        response = client.post(
            "/api/recommendations/recommendations",
            json={"skills": ["Python"], "use_ml": False}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Validate BaseResponse schema
        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert data["success"] == True
        
        # Validate that data matches expected structure
        assert "careers" in data["data"]
        assert "alternatives" in data["data"]
    
    @patch('routes.recommendations.recommendation_service')
    def test_recommend_endpoint_schema(self, mock_service, client):
        """Test /api/recommendations/recommend endpoint response schema"""
        mock_service.recommend.return_value = {
            "recommendations": [
                {"career_id": "test_001", "name": "Test", "score": 0.8}
            ],
            "method": "baseline"
        }
        
        response = client.post(
            "/api/recommendations/recommend",
            json={"skills": ["Python"], "use_ml": False}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
    
    @patch('routes.outlook.outlook_service')
    def test_outlook_endpoint_schema(self, mock_service, client):
        """Test /api/outlook/{career_id} endpoint response schema"""
        mock_service.analyze_outlook.return_value = {
            "career": {"career_id": "test_001", "name": "Test"},
            "growth_outlook": {"outlook": "Strong Growth", "confidence": "High"},
            "automation_risk": {"risk": "Low", "confidence": "Medium"},
            "stability_signal": {"signal": "Strong", "confidence": "High"},
            "confidence": {"level": "High", "why": "Test", "factors": []}
        }
        
        response = client.get("/api/outlook/test_001")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert "growth_outlook" in data["data"]
        assert "automation_risk" in data["data"]
    
    @patch('routes.career_switch.switch_service')
    def test_career_switch_endpoint_schema(self, mock_service, client):
        """Test /api/career-switch/switch endpoint response schema"""
        mock_service.analyze_career_switch.return_value = {
            "source_career": {"career_id": "test_001", "name": "Source"},
            "target_career": {"career_id": "test_002", "name": "Target"},
            "skill_overlap": {"percentage": 75.0},
            "transfer_map": {"transfers_directly": [], "needs_learning": []},
            "difficulty": "Medium",
            "transition_time": {"min_months": 6, "max_months": 12},
            "success_risk_assessment": {"success_factors": [], "risk_factors": []}
        }
        
        response = client.post(
            "/api/career-switch/switch",
            json={"source_career_id": "test_001", "target_career_id": "test_002"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert "overlap_percentage" in data["data"]
        assert "difficulty" in data["data"]
    
    @patch('routes.resume.resume_service')
    def test_resume_analyze_endpoint_schema(self, mock_service, client):
        """Test /api/resume/analyze endpoint response schema"""
        mock_service.extract_text_from_file.return_value = "Test resume text"
        mock_service.detect_skills.return_value = ["Python", "JavaScript"]
        mock_service.parse_resume_structure.return_value = {
            "sections": {},
            "bullets": [],
            "section_count": 0,
            "bullet_count": 0
        }
        
        # Create a mock file upload
        from io import BytesIO
        file_content = b"Test resume content"
        
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("resume.txt", BytesIO(file_content), "text/plain")},
            data={"target_career_id": "test_001"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
    
    @patch('routes.intake.intake_service')
    def test_intake_endpoint_schema(self, mock_service, client):
        """Test /api/intake/intake endpoint response schema"""
        mock_service.normalize_profile.return_value = {
            "normalized_profile": {},
            "features_summary": {}
        }
        
        response = client.post(
            "/api/intake/intake",
            json={"skills": ["Python"], "interests": {"Investigative": 5.0}}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
    
    @patch('routes.recommendations_guarded.guardrails_service')
    def test_recommendations_guarded_endpoint_schema(self, mock_service, client):
        """Test /api/recommendations-guarded/recommend endpoint response schema"""
        mock_service.recommend_with_guardrails.return_value = {
            "recommendations": [
                {"career_id": "test_001", "name": "Test", "score": 0.8}
            ],
            "input_quality": "sufficient",
            "total_count": 3,
            "guardrails_applied": {
                "demographic_check": "passed",
                "multiple_recommendations": True,
                "uncertainty_ranges": True
            }
        }
        
        response = client.post(
            "/api/recommendations-guarded/recommend",
            json={"skills": ["Python"]}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert "recommendations" in data["data"]
        assert "guardrails_applied" in data["data"]
    
    @patch('routes.data.service')
    @patch('routes.data.processing_service')
    def test_data_catalog_endpoint_schema(self, mock_processing, mock_service, client):
        """Test /api/data/catalog endpoint response schema"""
        from models.data_models import OccupationCatalog, Occupation, Skill
        
        mock_service.build_occupation_catalog.return_value = [
            OccupationCatalog(
                occupation=Occupation(career_id="test_001", name="Test", soc_code="00-0000.00"),
                skills=[Skill(skill_name="Python", importance=5.0)]
            )
        ]
        
        response = client.get("/api/data/catalog")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
    
    def test_example_endpoint_schema(self, client):
        """Test /api/example/test endpoint response schema"""
        response = client.get("/api/example/test")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
    
    def test_health_endpoint_structure(self, client):
        """Test /health endpoint structure"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "data_loaded" in data
    
    def test_error_response_schema_on_validation_error(self, client):
        """Test that validation errors return proper error schema"""
        # Send invalid request (missing required field)
        response = client.post(
            "/api/recommendations/recommendations",
            json={"invalid": "data"}
        )
        
        # Should return 422 (validation error) or proper error structure
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
        
        # Error responses should have proper structure
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            data = response.json()
            # FastAPI validation errors have 'detail' field
            assert "detail" in data or "error" in data
    
    def test_error_response_schema_on_not_found(self, client):
        """Test that 404 errors return proper error structure"""
        # Try to get non-existent career
        with patch('routes.outlook.outlook_service') as mock_service:
            mock_service.analyze_outlook.return_value = {"error": "Not found"}
            
            response = client.get("/api/outlook/nonexistent_001")
            
            # Should return 404 or error response
            assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
            
            if response.status_code == status.HTTP_404_NOT_FOUND:
                data = response.json()
                # Error should have proper structure
                assert "detail" in data or "error" in data







