"""
Unit tests for career switch overlap and translation map
Tests compute_skill_overlap and related methods in CareerSwitchService
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from services.career_switch_service import CareerSwitchService


class TestCareerSwitchOverlap:
    """Test suite for career switch overlap and translation map"""
    
    @pytest.fixture
    def mock_service(self, sample_processed_data):
        """Create a mocked career switch service with test data"""
        service = CareerSwitchService()
        service._processed_data = sample_processed_data
        service.load_processed_data = Mock(return_value=sample_processed_data)
        return service
    
    def test_compute_skill_overlap_structure(self, mock_service):
        """Test that skill overlap returns correct structure"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        assert "overlap_percentage" in result
        assert "transfers_directly" in result
        assert "needs_learning" in result
        assert "optional_skills" in result
        assert "num_transferable" in result
        assert "num_to_learn" in result
        assert "num_optional" in result
        
        assert isinstance(result["overlap_percentage"], float)
        assert isinstance(result["transfers_directly"], list)
        assert isinstance(result["needs_learning"], list)
        assert isinstance(result["optional_skills"], list)
    
    def test_compute_skill_overlap_percentage_range(self, mock_service):
        """Test that overlap percentage is in valid range [0, 100]"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        overlap_pct = result["overlap_percentage"]
        assert 0 <= overlap_pct <= 100, f"Overlap percentage {overlap_pct} should be in [0, 100]"
    
    def test_compute_skill_overlap_error_handling(self, mock_service):
        """Test error handling when career IDs are invalid"""
        result = mock_service.compute_skill_overlap(
            "invalid_career_001",
            "test_writer_001"
        )
        
        assert "error" in result
        assert result["overlap_percentage"] == 0.0
    
    def test_compute_skill_overlap_transfers_directly(self, mock_service):
        """Test that transfers_directly contains skills with high values in both"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        transfers = result["transfers_directly"]
        
        # Check structure of transfer skills
        for skill_info in transfers:
            assert "skill" in skill_info
            assert "source_level" in skill_info
            assert "target_level" in skill_info
            
            # Both levels should be >= transfer threshold (0.3)
            assert skill_info["source_level"] >= 0.3
            assert skill_info["target_level"] >= 0.3
        
        # Should be sorted by target_level (descending)
        if len(transfers) > 1:
            target_levels = [s["target_level"] for s in transfers]
            assert target_levels == sorted(target_levels, reverse=True), "Should be sorted by target level"
    
    def test_compute_skill_overlap_needs_learning(self, mock_service):
        """Test that needs_learning contains skills needed in target but not in source"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        needs_learning = result["needs_learning"]
        
        # Check structure
        for skill_info in needs_learning:
            assert "skill" in skill_info
            assert "source_level" in skill_info
            assert "target_level" in skill_info
            assert "gap" in skill_info
            
            # Target should need it (>= 0.4) but source doesn't have it (< 0.2)
            assert skill_info["target_level"] >= 0.4
            assert skill_info["source_level"] < 0.2
            assert skill_info["gap"] > 0  # Gap should be positive
        
        # Should be sorted by gap (descending)
        if len(needs_learning) > 1:
            gaps = [s["gap"] for s in needs_learning]
            assert gaps == sorted(gaps, reverse=True), "Should be sorted by gap"
    
    def test_compute_skill_overlap_optional_skills(self, mock_service):
        """Test that optional_skills contains skills with moderate importance"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        optional = result["optional_skills"]
        
        # Check structure
        for skill_info in optional:
            assert "skill" in skill_info
            assert "source_level" in skill_info
            assert "target_level" in skill_info
            
            # Target level should be in optional range [0.2, 0.4)
            assert 0.2 <= skill_info["target_level"] < 0.4
        
        # Should be sorted by target_level (descending)
        if len(optional) > 1:
            target_levels = [s["target_level"] for s in optional]
            assert target_levels == sorted(target_levels, reverse=True), "Should be sorted by target level"
    
    def test_compute_skill_overlap_limits(self, mock_service):
        """Test that skill lists are limited to top N"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        # Should be limited (top 20 for transfers/needs, top 15 for optional)
        assert len(result["transfers_directly"]) <= 20
        assert len(result["needs_learning"]) <= 20
        assert len(result["optional_skills"]) <= 15
    
    def test_compute_skill_overlap_counts_match(self, mock_service):
        """Test that count fields match the actual lists"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_writer_001"
        )
        
        assert result["num_transferable"] == len(result["transfers_directly"])
        assert result["num_to_learn"] == len(result["needs_learning"])
        assert result["num_optional"] == len(result["optional_skills"])
    
    def test_compute_skill_overlap_same_career(self, mock_service):
        """Test overlap when source and target are the same career"""
        result = mock_service.compute_skill_overlap(
            "test_engineer_001",
            "test_engineer_001"
        )
        
        # Should have high overlap (close to 100%)
        assert result["overlap_percentage"] > 90
        
        # Should have many transferable skills
        assert result["num_transferable"] > 0
        
        # Should have few or no skills to learn
        assert result["num_to_learn"] == 0 or result["num_to_learn"] < result["num_transferable"]
    
    def test_classify_difficulty(self, mock_service):
        """Test difficulty classification based on overlap and skills to learn"""
        # Low difficulty case
        difficulty = mock_service.classify_difficulty(overlap_pct=75.0, num_to_learn=3, num_transferable=10)
        assert difficulty == "Low"
        
        # High difficulty case
        difficulty = mock_service.classify_difficulty(overlap_pct=30.0, num_to_learn=20, num_transferable=5)
        assert difficulty == "High"
        
        # Medium difficulty case
        difficulty = mock_service.classify_difficulty(overlap_pct=55.0, num_to_learn=8, num_transferable=10)
        assert difficulty == "Medium"
        
        # Edge cases
        difficulty = mock_service.classify_difficulty(overlap_pct=50.0, num_to_learn=10, num_transferable=10)
        assert difficulty in ["Medium", "High"]  # Could be either
    
    def test_estimate_transition_time(self, mock_service):
        """Test transition time estimation"""
        time_estimate = mock_service.estimate_transition_time(
            difficulty="Low",
            num_to_learn=3,
            overlap_pct=75.0
        )
        
        assert "min_months" in time_estimate
        assert "max_months" in time_estimate
        assert "range" in time_estimate
        assert "note" in time_estimate
        
        assert time_estimate["min_months"] > 0
        assert time_estimate["max_months"] >= time_estimate["min_months"]
        assert time_estimate["max_months"] <= 48  # Capped at 48 months
        
        # Low difficulty should have shorter time range
        low_time = mock_service.estimate_transition_time("Low", 3, 75.0)
        high_time = mock_service.estimate_transition_time("High", 20, 30.0)
        
        assert low_time["max_months"] < high_time["max_months"], "High difficulty should take longer"
    
    def test_analyze_career_switch_full_structure(self, mock_service):
        """Test full career switch analysis structure"""
        result = mock_service.analyze_career_switch(
            "test_engineer_001",
            "test_writer_001"
        )
        
        # Check all required fields
        assert "source_career" in result
        assert "target_career" in result
        assert "skill_overlap" in result
        assert "transfer_map" in result
        assert "difficulty" in result
        assert "transition_time" in result
        assert "success_risk_assessment" in result
        
        # Check nested structures
        assert "career_id" in result["source_career"]
        assert "name" in result["source_career"]
        assert "career_id" in result["target_career"]
        assert "name" in result["target_career"]
        
        assert "percentage" in result["skill_overlap"]
        assert "transfers_directly" in result["transfer_map"]
        assert "needs_learning" in result["transfer_map"]
        assert "optional_skills" in result["transfer_map"]
        
        assert result["difficulty"] in ["Low", "Medium", "High"]
        
        assert "success_factors" in result["success_risk_assessment"]
        assert "risk_factors" in result["success_risk_assessment"]







