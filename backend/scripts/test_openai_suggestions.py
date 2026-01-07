"""
Test OpenAI suggestions - verify it adds better recommendations
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService


def test_openai_suggestions():
    """Test that OpenAI can suggest additional careers"""
    
    print("="*80)
    print(" TESTING OPENAI CAREER SUGGESTIONS")
    print("="*80)
    print()
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    print("Testing with user profile:")
    print("  Skills: Programming, Mathematics, Critical Thinking")
    print("  Interests: Investigative (7.0), Enterprising (5.0)")
    print()
    
    print("Getting ML recommendations...")
    result = service.recommend(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Investigative": 7.0, "Enterprising": 5.0},
        top_n=5,
        use_ml=True,
        use_openai=True
    )
    
    print(f"\nMethod: {result['method']}")
    if service.openai_service.is_available():
        print("OpenAI: Enabled")
    else:
        print("OpenAI: Not available (need API key)")
    print()
    
    print("Recommendations:")
    print()
    
    ml_recommendations = [r for r in result['recommendations'] if not r.get('openai_suggested', False)]
    openai_suggestions = [r for r in result['recommendations'] if r.get('openai_suggested', False)]
    
    print("ML Model Recommendations:")
    for i, rec in enumerate(ml_recommendations[:5], 1):
        print(f"  {i}. {rec['name']}")
        print(f"     Match: {rec['score']:.1%} | Confidence: {rec['confidence']}")
        if rec.get('outlook', {}).get('median_wage_2024'):
            print(f"     Salary: ${rec['outlook']['median_wage_2024']:,.0f}/year")
        print()
    
    if openai_suggestions:
        print("OpenAI Additional Suggestions:")
        for i, rec in enumerate(openai_suggestions, 1):
            print(f"  {i}. {rec['name']} (OpenAI Suggested)")
            print(f"     Match: {rec['score']:.1%} | Confidence: {rec['confidence']}")
            if rec.get('outlook', {}).get('median_wage_2024'):
                print(f"     Salary: ${rec['outlook']['median_wage_2024']:,.0f}/year")
            if rec.get('openai_enhancement', {}).get('enhanced_explanation'):
                print(f"     Why: {rec['openai_enhancement']['enhanced_explanation'][:100]}...")
            print()
    else:
        print("No OpenAI suggestions (either not available or ML recommendations were sufficient)")
        print()
    
    print("="*80)
    print(" TEST COMPLETE")
    print("="*80)
    print()
    print(f"Total recommendations: {len(result['recommendations'])}")
    print(f"  - ML model: {len(ml_recommendations)}")
    print(f"  - OpenAI suggestions: {len(openai_suggestions)}")
    print()


if __name__ == "__main__":
    test_openai_suggestions()









