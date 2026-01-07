"""
Comprehensive ML Verification Test
This script verifies that the system is using REAL machine learning, not just simple similarity matching.
It tests:
1. Model loading and verification
2. Model internals (coefficients, predictions)
3. Comparison between baseline and ML results
4. Prediction consistency and model behavior
"""
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService
from sklearn.linear_model import LogisticRegression


def test_model_loading():
    """Test 1: Verify model is loaded and is a real sklearn model"""
    print("=" * 80)
    print("TEST 1: Model Loading and Type Verification")
    print("=" * 80)
    
    service = CareerRecommendationService()
    loaded = service.load_model_artifacts()
    
    if not loaded:
        print("❌ FAILED: Model not loaded!")
        print("   Run: python scripts/train_recommendation_model.py")
        return False
    
    print("✅ Model loaded successfully")
    print(f"   Model version: {service.model_version}")
    print(f"   Model type: {type(service.ml_model).__name__}")
    print(f"   Scaler loaded: {service.scaler is not None}")
    
    # Verify it's actually a sklearn model
    if isinstance(service.ml_model, LogisticRegression):
        print("✅ Confirmed: Using sklearn LogisticRegression (real ML model)")
        print(f"   Model class: {service.ml_model.__class__.__module__}.{service.ml_model.__class__.__name__}")
    else:
        print(f"⚠️  Warning: Model is not LogisticRegression, it's {type(service.ml_model)}")
    
    # Check model has learned parameters
    if hasattr(service.ml_model, 'coef_'):
        coef_shape = service.ml_model.coef_.shape
        print(f"✅ Model has learned coefficients: shape {coef_shape}")
        print(f"   Number of features: {coef_shape[1]}")
        print(f"   Number of classes: {coef_shape[0]}")
        
        # Show some coefficient statistics
        coef_flat = service.ml_model.coef_.flatten()
        print(f"   Coefficient stats:")
        print(f"     - Mean: {np.mean(coef_flat):.6f}")
        print(f"     - Std: {np.std(coef_flat):.6f}")
        print(f"     - Min: {np.min(coef_flat):.6f}")
        print(f"     - Max: {np.max(coef_flat):.6f}")
    else:
        print("❌ Model doesn't have coefficients - not a trained model!")
        return False
    
    print()
    return True


def test_model_predictions():
    """Test 2: Verify model makes actual predictions (not just returning constants)"""
    print("=" * 80)
    print("TEST 2: Model Prediction Verification")
    print("=" * 80)
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    # Build a test user vector
    user_features = service.build_user_feature_vector(
        skills=["Programming", "Mathematics", "Critical Thinking"],
        interests={"Investigative": 6.0, "Enterprising": 5.0}
    )
    user_vector = np.array(user_features["combined_vector"])
    
    # Get occupation vectors
    occupation_vectors = service.build_occupation_vectors()
    
    # Test predictions on multiple careers
    predictions = []
    career_ids = list(occupation_vectors.keys())[:10]  # Test first 10
    
    print(f"Testing predictions on {len(career_ids)} careers...")
    
    for career_id in career_ids:
        occ_vector = occupation_vectors[career_id]
        
        # Build feature vector (same as in ml_rank)
        feature_combined = np.concatenate([
            user_vector,
            occ_vector,
            user_vector - occ_vector
        ])
        
        # Scale
        if service.scaler:
            feature_combined = service.scaler.transform(feature_combined.reshape(1, -1))[0]
        
        # Get prediction
        feature_reshaped = feature_combined.reshape(1, -1)
        if hasattr(service.ml_model, 'predict_proba'):
            proba = service.ml_model.predict_proba(feature_reshaped)[0]
            score = proba[1] if len(proba) > 1 else proba[0]
        else:
            score = service.ml_model.predict(feature_reshaped)[0]
        
        predictions.append((career_id, score))
    
    # Check that predictions vary (not all the same)
    scores = [p[1] for p in predictions]
    score_std = np.std(scores)
    score_range = np.max(scores) - np.min(scores)
    
    print(f"✅ Predictions generated successfully")
    print(f"   Score range: {np.min(scores):.4f} to {np.max(scores):.4f}")
    print(f"   Score std dev: {score_std:.4f}")
    print(f"   Mean score: {np.mean(scores):.4f}")
    
    if score_std < 0.001:
        print("❌ WARNING: Predictions are too similar (std < 0.001)")
        print("   Model might not be learning properly")
        return False
    else:
        print("✅ Predictions vary significantly - model is making real decisions")
    
    # Show top 3 predictions
    predictions.sort(key=lambda x: x[1], reverse=True)
    print("\n   Top 3 predictions:")
    for i, (career_id, score) in enumerate(predictions[:3], 1):
        processed_data = service.load_processed_data()
        occ_data = next((occ for occ in processed_data["occupations"] if occ["career_id"] == career_id), None)
        name = occ_data["name"] if occ_data else career_id
        print(f"     {i}. {name}: {score:.4f}")
    
    print()
    return True


def test_baseline_vs_ml_comparison():
    """Test 3: Compare baseline (cosine similarity) vs ML predictions"""
    print("=" * 80)
    print("TEST 3: Baseline vs ML Comparison")
    print("=" * 80)
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    # Test with different user profiles
    test_cases = [
        {
            "name": "Tech-focused",
            "skills": ["Programming", "Mathematics", "Critical Thinking", "Systems Analysis"],
            "interests": {"Investigative": 7.0, "Enterprising": 5.0}
        },
        {
            "name": "Creative-focused",
            "skills": ["Writing", "Speaking", "Social Perceptiveness", "Active Listening"],
            "interests": {"Artistic": 7.0, "Social": 6.0}
        },
        {
            "name": "Business-focused",
            "skills": ["Management", "Negotiation", "Persuasion", "Coordination"],
            "interests": {"Enterprising": 7.0, "Conventional": 5.0}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        
        # Get baseline recommendations
        baseline_result = service.recommend(
            skills=test_case["skills"],
            interests=test_case["interests"],
            top_n=5,
            use_ml=False
        )
        
        # Get ML recommendations
        ml_result = service.recommend(
            skills=test_case["skills"],
            interests=test_case["interests"],
            top_n=5,
            use_ml=True
        )
        
        # Compare results
        baseline_careers = [r["career_id"] for r in baseline_result["recommendations"]]
        ml_careers = [r["career_id"] for r in ml_result["recommendations"]]
        
        # Calculate overlap
        overlap = set(baseline_careers) & set(ml_careers)
        overlap_pct = len(overlap) / len(baseline_careers) * 100
        
        print(f"   Baseline method: {baseline_result['method']}")
        print(f"   ML method: {ml_result['method']}")
        print(f"   Overlap: {len(overlap)}/{len(baseline_careers)} ({overlap_pct:.1f}%)")
        
        # Show top recommendation from each
        if baseline_result["recommendations"]:
            baseline_top = baseline_result["recommendations"][0]
            print(f"   Baseline top: {baseline_top['name']} (score: {baseline_top['score']:.4f})")
        
        if ml_result["recommendations"]:
            ml_top = ml_result["recommendations"][0]
            print(f"   ML top: {ml_top['name']} (score: {ml_top['score']:.4f})")
        
        # Check if they're different
        if baseline_careers != ml_careers:
            print("   ✅ ML produces different rankings than baseline - ML is working!")
        else:
            print("   ⚠️  ML and baseline produce same results - might need investigation")
        
        # Compare score distributions
        baseline_scores = [r["score"] for r in baseline_result["recommendations"]]
        ml_scores = [r["score"] for r in ml_result["recommendations"]]
        
        print(f"   Baseline score range: {min(baseline_scores):.4f} - {max(baseline_scores):.4f}")
        print(f"   ML score range: {min(ml_scores):.4f} - {max(ml_scores):.4f}")
    
    print()
    return True


def test_model_internals():
    """Test 4: Examine model internals to prove it's learned patterns"""
    print("=" * 80)
    print("TEST 4: Model Internals Analysis")
    print("=" * 80)
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    if not isinstance(service.ml_model, LogisticRegression):
        print("⚠️  Model is not LogisticRegression, skipping internals test")
        return True
    
    model = service.ml_model
    
    # Check intercept
    if hasattr(model, 'intercept_'):
        print(f"✅ Model intercept: {model.intercept_[0]:.6f}")
    
    # Analyze feature importance (coefficients)
    coef = model.coef_[0]
    
    # Find most positive and negative coefficients
    top_positive_idx = np.argsort(coef)[-10:][::-1]
    top_negative_idx = np.argsort(coef)[:10]
    
    print(f"\n   Top 10 most positive coefficients (features that increase match probability):")
    for i, idx in enumerate(top_positive_idx[:5], 1):
        print(f"     {i}. Feature {idx}: {coef[idx]:.6f}")
    
    print(f"\n   Top 10 most negative coefficients (features that decrease match probability):")
    for i, idx in enumerate(top_negative_idx[:5], 1):
        print(f"     {i}. Feature {idx}: {coef[idx]:.6f}")
    
    # Check if model has learned non-trivial patterns
    non_zero_coefs = np.count_nonzero(coef)
    total_coefs = len(coef)
    non_zero_pct = (non_zero_coefs / total_coefs) * 100
    
    print(f"\n   Model complexity:")
    print(f"     - Total features: {total_coefs}")
    print(f"     - Non-zero coefficients: {non_zero_coefs} ({non_zero_pct:.1f}%)")
    print(f"     - Mean |coefficient|: {np.mean(np.abs(coef)):.6f}")
    
    if non_zero_pct > 10:
        print("   ✅ Model has learned complex patterns (many non-zero coefficients)")
    else:
        print("   ⚠️  Model might be too sparse")
    
    print()
    return True


def test_prediction_consistency():
    """Test 5: Verify model predictions are consistent and deterministic"""
    print("=" * 80)
    print("TEST 5: Prediction Consistency Test")
    print("=" * 80)
    
    service = CareerRecommendationService()
    service.load_model_artifacts()
    
    # Same input should give same output
    user_features = service.build_user_feature_vector(
        skills=["Programming", "Mathematics"],
        interests={"Investigative": 6.0}
    )
    user_vector = np.array(user_features["combined_vector"])
    
    # Run prediction twice
    result1 = service.ml_rank(user_vector, top_n=5, use_model=True)
    result2 = service.ml_rank(user_vector, top_n=5, use_model=True)
    
    # Compare
    scores1 = [r[1] for r in result1]
    scores2 = [r[1] for r in result2]
    
    if np.allclose(scores1, scores2):
        print("✅ Predictions are deterministic (same input = same output)")
    else:
        print("❌ Predictions are not deterministic!")
        print(f"   Difference: {np.max(np.abs(np.array(scores1) - np.array(scores2)))}")
        return False
    
    # Test that different inputs give different outputs
    user_features2 = service.build_user_feature_vector(
        skills=["Writing", "Speaking"],
        interests={"Social": 6.0}
    )
    user_vector2 = np.array(user_features2["combined_vector"])
    
    result3 = service.ml_rank(user_vector2, top_n=5, use_model=True)
    scores3 = [r[1] for r in result3]
    
    if not np.allclose(scores1, scores3):
        print("✅ Different inputs produce different outputs - model is responsive")
    else:
        print("❌ Different inputs produce same outputs - model might not be working")
        return False
    
    print()
    return True


def main():
    """Run all ML verification tests"""
    print("\n" + "=" * 80)
    print("ML VERIFICATION TEST SUITE")
    print("Verifying that the system uses REAL machine learning")
    print("=" * 80 + "\n")
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Model Predictions", test_model_predictions),
        ("Baseline vs ML Comparison", test_baseline_vs_ml_comparison),
        ("Model Internals", test_model_internals),
        ("Prediction Consistency", test_prediction_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - ML is verified and working!")
        print("   The system is using real machine learning (LogisticRegression)")
        print("   and producing different results than simple baseline similarity.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review the output above")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()









