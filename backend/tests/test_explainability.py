"""
Unit tests for explainability output
Tests _explain_prediction method in CareerRecommendationService
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from services.recommendation_service import CareerRecommendationService


class TestExplainability:
    """Test suite for explainability output"""
    
    @pytest.fixture
    def mock_service(self, sample_processed_data):
        """Create a mocked recommendation service with test data"""
        service = CareerRecommendationService()
        service._processed_data = sample_processed_data
        service.load_processed_data = Mock(return_value=sample_processed_data)
        return service
    
    def test_explain_prediction_structure(self, mock_service):
        """Test that explanation has correct structure"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set some skill values
        user_vector[0] = 0.8  # Writing
        user_vector[1] = 0.6  # Speaking
        occ_vector[0] = 0.9   # Writing
        occ_vector[1] = 0.7   # Speaking
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        # Check structure
        assert "top_contributing_skills" in explanation
        assert "why_points" in explanation
        assert "similarity_breakdown" in explanation
        
        assert isinstance(explanation["top_contributing_skills"], list)
        assert isinstance(explanation["why_points"], list)
        assert isinstance(explanation["similarity_breakdown"], dict)
    
    def test_explain_prediction_top_skills(self, mock_service):
        """Test that top contributing skills are identified correctly"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set high values for Writing (index 0) and Speaking (index 1)
        user_vector[0] = 0.9  # Writing
        user_vector[1] = 0.8  # Speaking
        occ_vector[0] = 0.9   # Writing
        occ_vector[1] = 0.8   # Speaking
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        top_skills = explanation["top_contributing_skills"]
        
        # Should have at least one contributing skill
        assert len(top_skills) > 0
        
        # Check structure of top skills
        for skill_info in top_skills:
            assert "skill" in skill_info
            assert "user_value" in skill_info
            assert "occupation_value" in skill_info
            assert "contribution" in skill_info
            
            # Values should be valid
            assert 0 <= skill_info["user_value"] <= 1
            assert 0 <= skill_info["occupation_value"] <= 1
            assert 0 <= skill_info["contribution"] <= 1
        
        # Top skills should be sorted by contribution (descending)
        contributions = [s["contribution"] for s in top_skills]
        assert contributions == sorted(contributions, reverse=True), "Skills should be sorted by contribution"
    
    def test_explain_prediction_why_points(self, mock_service):
        """Test that why_points are generated correctly"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set high user value for Writing
        user_vector[0] = 0.9  # Writing
        occ_vector[0] = 0.8   # Writing
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        why_points = explanation["why_points"]
        
        # Should have at least one why point if user has high skill value
        assert len(why_points) > 0
        
        # Why points should be strings
        assert all(isinstance(point, str) for point in why_points)
        
        # Why points should mention skills
        why_text = " ".join(why_points).lower()
        assert "writing" in why_text or any("skill" in point.lower() for point in why_points)
    
    def test_explain_prediction_similarity_breakdown(self, mock_service):
        """Test that similarity breakdown is calculated correctly"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set some skill values
        user_vector[:5] = [0.8, 0.6, 0.7, 0.5, 0.6]
        occ_vector[:5] = [0.9, 0.7, 0.8, 0.4, 0.5]
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        similarity_breakdown = explanation["similarity_breakdown"]
        
        # Should have skill_similarity
        assert "skill_similarity" in similarity_breakdown
        
        # Similarity should be in [0, 1] range (cosine similarity)
        similarity = similarity_breakdown["skill_similarity"]
        assert 0 <= similarity <= 1, f"Similarity {similarity} should be in [0, 1]"
    
    def test_explain_prediction_threshold_filtering(self, mock_service):
        """Test that low-contribution skills are filtered out"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set very low values (below threshold)
        user_vector[0] = 0.01  # Very low
        occ_vector[0] = 0.01   # Very low
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        top_skills = explanation["top_contributing_skills"]
        
        # Skills with very low contribution should be filtered out (threshold is 0.1)
        for skill_info in top_skills:
            assert skill_info["contribution"] > 0.1, "Low contribution skills should be filtered"
    
    def test_explain_prediction_top_n_limit(self, mock_service):
        """Test that top contributing skills are limited to top 5"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        # Set high values for multiple skills
        for i in range(min(10, num_skills)):
            user_vector[i] = 0.8
            occ_vector[i] = 0.8
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        top_skills = explanation["top_contributing_skills"]
        
        # Should be limited to top 5
        assert len(top_skills) <= 5, "Should return at most 5 top contributing skills"
    
    def test_explain_prediction_empty_inputs(self, mock_service):
        """Test explainability with empty/zero vectors"""
        num_skills = len(mock_service._processed_data["skill_names"])
        user_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        occ_vector = np.zeros(num_skills + len(mock_service.riasec_categories) + len(mock_service.work_values) + 3)
        
        explanation = mock_service._explain_prediction(
            user_vector, occ_vector, "test_engineer_001", mock_service._processed_data
        )
        
        # Should still return valid structure
        assert "top_contributing_skills" in explanation
        assert "why_points" in explanation
        assert "similarity_breakdown" in explanation
        
        # With zero vectors, similarity should be defined (could be 0 or NaN)
        similarity = explanation["similarity_breakdown"].get("skill_similarity", 0)
        assert isinstance(similarity, (int, float))





