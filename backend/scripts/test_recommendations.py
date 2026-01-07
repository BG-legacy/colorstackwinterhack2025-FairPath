"""
Quick test script for recommendations
Just running through the basic flows to make sure everything works
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService


def test_baseline():
    """Test baseline recommendations"""
    print("Testing baseline recommendations...")
    service = CareerRecommendationService()
    
    result = service.recommend(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        top_n=5,
        use_ml=False
    )
    
    print(f"Got {len(result['recommendations'])} recommendations using {result['method']}")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"{i}. {rec['name']} (score: {rec['score']:.3f}, confidence: {rec['confidence']})")
    print()


def test_ml_model():
    """Test ML model recommendations"""
    print("Testing ML model recommendations...")
    service = CareerRecommendationService()
    
    # Try to load model
    loaded = service.load_model_artifacts()
    if not loaded:
        print("No model found - run train_recommendation_model.py first")
        return
    
    result = service.recommend(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Enterprising": 5.0, "Investigative": 6.0},
        top_n=5,
        use_ml=True
    )
    
    print(f"Got {len(result['recommendations'])} recommendations using {result['method']}")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"{i}. {rec['name']} (score: {rec['score']:.3f}, confidence: {rec['confidence']})")
        if rec['explanation']['top_contributing_skills']:
            top_skill = rec['explanation']['top_contributing_skills'][0]
            print(f"   Top skill: {top_skill['skill']} (contribution: {top_skill['contribution']:.3f})")
    print()


def test_explainability():
    """Test explainability features"""
    print("Testing explainability...")
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    result = service.recommend(
        skills=["Writing", "Speaking", "Social Perceptiveness"],
        top_n=1,
        use_ml=True
    )
    
    if result['recommendations']:
        rec = result['recommendations'][0]
        print(f"Career: {rec['name']}")
        print(f"Confidence: {rec['confidence']} (score: {rec['score']:.3f})")
        print("Top contributing skills:")
        for skill in rec['explanation']['top_contributing_skills'][:3]:
            print(f"  - {skill['skill']}: contribution={skill['contribution']:.3f}")
        print("Why points:")
        for point in rec['explanation']['why_points'][:3]:
            print(f"  - {point}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Career Recommendation System")
    print("=" * 60)
    print()
    
    test_baseline()
    test_ml_model()
    test_explainability()
    
    print("=" * 60)
    print("Tests complete!")









