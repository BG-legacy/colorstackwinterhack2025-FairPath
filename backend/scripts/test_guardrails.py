"""
Quick test script for ML guardrails
I'm testing that guardrails work - no demographics, multiple recommendations, uncertainty, fallbacks
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.guardrails_service import GuardrailsService


def test_demographic_rejection():
    """Test that demographic features are rejected"""
    print("=" * 60)
    print("Testing Demographic Feature Rejection")
    print("=" * 60)
    
    service = GuardrailsService()
    
    # Test with age in skills
    result = service.recommend_with_guardrails(
        skills=["Programming", "Age 25", "Mathematics"]
    )
    
    if "error" in result and "demographic" in result.get("error", "").lower():
        print("✓ Correctly rejected demographic data in skills")
        print(f"  Issues: {result.get('issues', [])}")
    else:
        print("✗ Failed to reject demographic data")
    
    # Test with gender in constraints
    result = service.recommend_with_guardrails(
        skills=["Programming"],
        constraints={"gender": "male", "min_wage": 50000}
    )
    
    if "error" in result and "demographic" in result.get("error", "").lower():
        print("✓ Correctly rejected demographic data in constraints")
        print(f"  Issues: {result.get('issues', [])}")
    else:
        print("✗ Failed to reject demographic data in constraints")
    
    print()


def test_multiple_recommendations():
    """Test that we always get multiple recommendations"""
    print("=" * 60)
    print("Testing Multiple Recommendations")
    print("=" * 60)
    
    service = GuardrailsService()
    
    # Test with empty input
    result = service.recommend_with_guardrails()
    
    count = result.get("total_count", 0)
    if count >= 3:
        print(f"✓ Empty input returned {count} recommendations (minimum 3)")
    else:
        print(f"✗ Empty input only returned {count} recommendations")
    
    # Test with thin input
    result = service.recommend_with_guardrails(
        skills=["Programming"]
    )
    
    count = result.get("total_count", 0)
    if count >= 3:
        print(f"✓ Thin input returned {count} recommendations (minimum 3)")
    else:
        print(f"✗ Thin input only returned {count} recommendations")
    
    # Test with sufficient input
    result = service.recommend_with_guardrails(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Investigative": 6.0, "Enterprising": 5.0},
        work_values={"Achievement": 6.0}
    )
    
    count = result.get("total_count", 0)
    if count >= 3:
        print(f"✓ Sufficient input returned {count} recommendations (minimum 3)")
    else:
        print(f"✗ Sufficient input only returned {count} recommendations")
    
    print()


def test_uncertainty_ranges():
    """Test that uncertainty ranges are included"""
    print("=" * 60)
    print("Testing Uncertainty Ranges")
    print("=" * 60)
    
    service = GuardrailsService()
    
    # Test with empty input
    result = service.recommend_with_guardrails()
    recommendations = result.get("recommendations", [])
    
    if recommendations:
        rec = recommendations[0]
        if "score_range" in rec and "uncertainty" in rec:
            print("✓ Uncertainty ranges included in recommendations")
            print(f"  Example: score_range={rec['score_range']}")
            print(f"  Uncertainty: {rec['uncertainty']}")
        else:
            print("✗ Missing uncertainty ranges")
    else:
        print("✗ No recommendations returned")
    
    print()


def test_fallback_behavior():
    """Test fallback behavior for empty/thin inputs"""
    print("=" * 60)
    print("Testing Fallback Behavior")
    print("=" * 60)
    
    service = GuardrailsService()
    
    # Test with empty input
    result = service.recommend_with_guardrails()
    
    if result.get("guardrails_applied", {}).get("fallback_used"):
        print("✓ Fallback used for empty input")
        print(f"  Input quality: {result.get('input_quality')}")
        print(f"  Total recommendations: {result.get('total_count')}")
    else:
        print("✗ Fallback not used for empty input")
    
    # Test with thin input
    result = service.recommend_with_guardrails(
        skills=["Programming"]
    )
    
    if result.get("input_quality") == "thin":
        print("✓ Correctly identified thin input")
        print(f"  Input quality: {result.get('input_quality')}")
        if "input_quality_note" in result:
            print(f"  Note: {result['input_quality_note']}")
    else:
        print(f"✗ Incorrectly classified input quality: {result.get('input_quality')}")
    
    print()


def test_full_workflow():
    """Test a full recommendation workflow"""
    print("=" * 60)
    print("Testing Full Workflow")
    print("=" * 60)
    
    service = GuardrailsService()
    
    result = service.recommend_with_guardrails(
        skills=["Writing", "Speaking", "Social Perceptiveness"],
        interests={"Social": 6.0, "Artistic": 5.0},
        top_n=5
    )
    
    if "error" in result:
        print(f"✗ Error: {result['error']}")
        return
    
    print(f"✓ Generated {result.get('total_count')} recommendations")
    print(f"  Input quality: {result.get('input_quality')}")
    print(f"  Guardrails applied: {result.get('guardrails_applied')}")
    
    if result.get("recommendations"):
        rec = result["recommendations"][0]
        print(f"\n  Example recommendation:")
        print(f"    Career: {rec.get('name')}")
        print(f"    Score range: {rec.get('score_range')}")
        print(f"    Confidence: {rec.get('confidence')}")
        print(f"    Uncertainty: {rec.get('uncertainty', {}).get('level')}")
    
    print()


def main():
    print("\nTesting ML Guardrails Service\n")
    
    test_demographic_rejection()
    test_multiple_recommendations()
    test_uncertainty_ranges()
    test_fallback_behavior()
    test_full_workflow()
    
    print("=" * 60)
    print("Guardrails testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()









