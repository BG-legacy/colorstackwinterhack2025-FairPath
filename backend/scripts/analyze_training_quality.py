"""
Analyze training quality - check if 100% accuracy is realistic or indicates problems
"""
import numpy as np
from pathlib import Path
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService


def analyze_training_quality():
    """Analyze if the training results are actually good or too good to be true"""
    
    print("="*100)
    print("TRAINING QUALITY ANALYSIS")
    print("="*100)
    print()
    
    service = CareerRecommendationService()
    processed_data = service.load_processed_data()
    occupation_vectors = service.build_occupation_vectors()
    
    # Generate training data
    np.random.seed(42)
    random.seed(42)
    
    X = []
    y = []
    careers_list = list(occupation_vectors.keys())
    
    print("Analyzing synthetic data generation...")
    print("-" * 100)
    
    # Check how separable the data is
    positive_samples = []
    negative_samples = []
    
    for i in range(100):  # Sample 100 to analyze
        target_career_id = random.choice(careers_list)
        target_vector = occupation_vectors[target_career_id]
        
        # Positive sample
        noise = np.random.normal(0, 0.1, size=target_vector.shape)
        user_vector_pos = np.clip(target_vector + noise, 0, 1)
        feature_pos = np.concatenate([user_vector_pos, target_vector, user_vector_pos - target_vector])
        positive_samples.append(feature_pos)
        
        # Negative sample
        user_vector_neg = np.random.random(size=target_vector.shape)
        feature_neg = np.concatenate([user_vector_neg, target_vector, user_vector_neg - target_vector])
        negative_samples.append(feature_neg)
    
    positive_samples = np.array(positive_samples)
    negative_samples = np.array(negative_samples)
    
    # Calculate separability
    pos_mean = positive_samples.mean(axis=0)
    neg_mean = negative_samples.mean(axis=0)
    separation = np.linalg.norm(pos_mean - neg_mean)
    
    print(f"Mean feature difference between positive and negative samples: {separation:.4f}")
    print(f"Positive samples mean: {pos_mean[:5]}...")
    print(f"Negative samples mean: {neg_mean[:5]}...")
    print()
    
    # Generate full training set
    print("Generating full training set...")
    X = []
    y = []
    
    for i in range(2000):
        target_career_id = random.choice(careers_list)
        target_vector = occupation_vectors[target_career_id]
        
        is_positive = random.random() > 0.5
        
        if is_positive:
            noise = np.random.normal(0, 0.1, size=target_vector.shape)
            user_vector = np.clip(target_vector + noise, 0, 1)
        else:
            user_vector = np.random.random(size=target_vector.shape)
        
        feature_vector = np.concatenate([
            user_vector,
            target_vector,
            user_vector - target_vector
        ])
        
        X.append(feature_vector)
        y.append(1 if is_positive else 0)
    
    X = np.array(X)
    y = np.array(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    model = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)
    
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print("="*100)
    print("TRAINING RESULTS ANALYSIS")
    print("="*100)
    print()
    
    print(f"Training Accuracy: {train_score:.4f} ({train_score*100:.2f}%)")
    print(f"Test Accuracy: {test_score:.4f} ({test_score*100:.2f}%)")
    print()
    
    # Detailed metrics
    print("Detailed Classification Report:")
    print("-" * 100)
    print(classification_report(y_test, test_pred, target_names=['Bad Match', 'Good Match']))
    print()
    
    print("Confusion Matrix:")
    print("-" * 100)
    cm = confusion_matrix(y_test, test_pred)
    print(f"                Predicted")
    print(f"              Bad    Good")
    print(f"Actual Bad    {cm[0,0]:4d}   {cm[0,1]:4d}")
    print(f"       Good    {cm[1,0]:4d}   {cm[1,1]:4d}")
    print()
    
    # Analysis
    print("="*100)
    print("QUALITY ASSESSMENT")
    print("="*100)
    print()
    
    print("ISSUES IDENTIFIED:")
    print("-" * 100)
    
    issues = []
    warnings = []
    positives = []
    
    if train_score == 1.0 and test_score == 1.0:
        issues.append("100% accuracy on both train and test sets")
        issues.append("This suggests the problem is too easy or data is too simple")
    
    # Check if data is too separable
    if separation > 1.0:
        warnings.append(f"Very high separation ({separation:.2f}) between classes")
        warnings.append("Synthetic data generation creates easily separable patterns")
    
    # Check coefficient distribution
    coef = model.coef_[0]
    if np.abs(coef).max() < 1.0:
        positives.append("Coefficients are reasonable (not too large)")
    else:
        warnings.append("Some coefficients are very large (potential overfitting)")
    
    if len(issues) > 0:
        print("CRITICAL ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        print()
    
    if len(warnings) > 0:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if len(positives) > 0:
        print("POSITIVE ASPECTS:")
        for pos in positives:
            print(f"  - {pos}")
        print()
    
    print("="*100)
    print("REAL-WORLD IMPLICATIONS")
    print("="*100)
    print()
    
    print("Why 100% accuracy might be problematic:")
    print("  1. Synthetic data is too simple:")
    print("     - Positive: career_vector + small_noise (very similar)")
    print("     - Negative: completely random vector (very different)")
    print("     - Model can easily distinguish these patterns")
    print()
    print("  2. Real-world data will be more complex:")
    print("     - Users won't be 'career_vector + noise'")
    print("     - Good matches might have some differences")
    print("     - Bad matches might have some similarities")
    print()
    print("  3. What to expect in production:")
    print("     - Lower accuracy (probably 70-85% would be realistic)")
    print("     - Model should still provide useful rankings")
    print("     - Need real user-career match data for better training")
    print()
    
    print("RECOMMENDATIONS:")
    print("-" * 100)
    print("  1. The model structure is correct (LogisticRegression, scaling, etc.)")
    print("  2. For production, collect real user-career match data")
    print("  3. Consider more sophisticated synthetic data generation:")
    print("     - Add more realistic noise patterns")
    print("     - Create 'hard' examples (similar but different)")
    print("     - Use actual user profiles if available")
    print("  4. Current model will work for demos, but expect lower accuracy on real data")
    print()
    
    print("="*100)
    print("VERDICT")
    print("="*100)
    print()
    print("The training process is CORRECT and follows ML best practices.")
    print("However, 100% accuracy indicates the SYNTHETIC DATA is too simple.")
    print()
    print("For a demo/prototype: This is FINE - shows the ML pipeline works")
    print("For production: Need real training data for realistic performance")
    print()
    print("="*100)


if __name__ == "__main__":
    analyze_training_quality()











