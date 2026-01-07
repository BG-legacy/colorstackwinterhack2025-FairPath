"""
Production-ready training script with realistic synthetic data generation
Creates more challenging training examples that better simulate real-world scenarios
"""
import numpy as np
from pathlib import Path
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService


def generate_realistic_user_vector(career_vector, match_type, all_careers, occupation_vectors):
    """
    Generate realistic user vectors based on match type
    
    match_type options:
    - 'strong_match': User has most skills/interests aligned (70-90% similarity)
    - 'moderate_match': User has some alignment (50-70% similarity) 
    - 'weak_match': User has minimal alignment (30-50% similarity)
    - 'poor_match': User has different profile (0-30% similarity)
    - 'partial_match': User matches some aspects but not others
    - 'wrong_interests': User has right skills but wrong interests
    """
    vector_dim = len(career_vector)
    
    if match_type == 'strong_match':
        # Strong match: 70-90% similarity
        # User has most skills/interests, with some variation
        similarity_target = np.random.uniform(0.70, 0.90)
        # Create user vector that's similar but not identical
        noise_scale = 1.0 - similarity_target
        noise = np.random.normal(0, noise_scale * 0.3, size=career_vector.shape)
        user_vector = np.clip(career_vector + noise, 0, 1)
        # Add some random skills user might have that career doesn't need
        random_skills = np.random.random(size=(int(vector_dim * 0.1))) * 0.5
        skill_indices = np.random.choice(vector_dim, size=len(random_skills), replace=False)
        user_vector[skill_indices] = np.maximum(user_vector[skill_indices], random_skills)
        return user_vector, True
        
    elif match_type == 'moderate_match':
        # Moderate match: 50-70% similarity
        # User has some relevant skills but also different ones
        similarity_target = np.random.uniform(0.50, 0.70)
        # Mix of career skills and random skills
        overlap = int(vector_dim * similarity_target)
        user_vector = np.zeros(vector_dim)
        # Copy some skills from career
        overlap_indices = np.random.choice(vector_dim, size=overlap, replace=False)
        user_vector[overlap_indices] = career_vector[overlap_indices] * np.random.uniform(0.7, 1.0, size=overlap)
        # Add some different skills
        remaining_indices = np.setdiff1d(np.arange(vector_dim), overlap_indices)
        user_vector[remaining_indices] = np.random.random(size=len(remaining_indices)) * 0.6
        return user_vector, True
        
    elif match_type == 'weak_match':
        # Weak match: 30-50% similarity - borderline case
        similarity_target = np.random.uniform(0.30, 0.50)
        overlap = int(vector_dim * similarity_target)
        user_vector = np.random.random(size=vector_dim) * 0.7
        # Add some career-relevant skills
        overlap_indices = np.random.choice(vector_dim, size=overlap, replace=False)
        user_vector[overlap_indices] = career_vector[overlap_indices] * np.random.uniform(0.5, 0.8, size=overlap)
        return user_vector, False  # Borderline - could go either way
        
    elif match_type == 'poor_match':
        # Poor match: 0-30% similarity
        # User has different profile, maybe from different career cluster
        similarity_target = np.random.uniform(0.0, 0.30)
        # Pick a different career as base
        other_career_id = random.choice(all_careers)
        other_career_vector = occupation_vectors[other_career_id]
        # Mix with random
        mix_ratio = similarity_target
        user_vector = (other_career_vector * mix_ratio) + (np.random.random(size=vector_dim) * (1 - mix_ratio))
        return user_vector, False
        
    elif match_type == 'partial_match':
        # Partial match: User matches skills but not interests, or vice versa
        # Split vector into skills (first part) and interests/values (later part)
        skill_dim = int(vector_dim * 0.7)  # Assume 70% skills, 30% interests/values
        # Match skills but not interests
        if random.random() > 0.5:
            user_vector = np.zeros(vector_dim)
            user_vector[:skill_dim] = career_vector[:skill_dim] * np.random.uniform(0.7, 1.0, size=skill_dim)
            user_vector[skill_dim:] = np.random.random(size=vector_dim - skill_dim) * 0.4
        else:
            # Match interests but not skills
            user_vector = np.zeros(vector_dim)
            user_vector[:skill_dim] = np.random.random(size=skill_dim) * 0.4
            user_vector[skill_dim:] = career_vector[skill_dim:] * np.random.uniform(0.7, 1.0, size=vector_dim - skill_dim)
        return user_vector, False
        
    elif match_type == 'wrong_interests':
        # User has right skills but wrong interests/values
        skill_dim = int(vector_dim * 0.7)
        user_vector = np.zeros(vector_dim)
        # Match skills
        user_vector[:skill_dim] = career_vector[:skill_dim] * np.random.uniform(0.7, 1.0, size=skill_dim)
        # Wrong interests - pick opposite or random
        user_vector[skill_dim:] = np.random.random(size=vector_dim - skill_dim) * 0.3
        return user_vector, False
    
    else:
        # Default: random
        return np.random.random(size=vector_dim), False


def generate_realistic_training_data(service: CareerRecommendationService, num_samples: int = 2000):
    """
    Generate realistic training data that better simulates real-world scenarios
    Creates more challenging examples with various match types
    """
    processed_data = service.load_processed_data()
    occupation_vectors = service.build_occupation_vectors()
    
    X = []
    y = []
    
    all_skills = processed_data["skill_names"]
    careers_list = list(occupation_vectors.keys())
    
    print(f"Generating {num_samples} realistic training samples...")
    print("Using multiple match types to create challenging examples")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Distribution of match types (more realistic distribution)
    match_type_distribution = {
        'strong_match': 0.25,      # 25% strong matches (clear positive)
        'moderate_match': 0.20,    # 20% moderate matches (positive but harder)
        'weak_match': 0.15,        # 15% weak matches (ambiguous - label as negative)
        'poor_match': 0.25,        # 25% poor matches (clear negative)
        'partial_match': 0.10,     # 10% partial matches (negative - missing key aspects)
        'wrong_interests': 0.05    # 5% wrong interests (negative)
    }
    
    match_types = []
    for match_type, prob in match_type_distribution.items():
        count = int(num_samples * prob)
        match_types.extend([match_type] * count)
    
    # Fill remaining with random if needed
    while len(match_types) < num_samples:
        match_types.append(random.choice(list(match_type_distribution.keys())))
    
    random.shuffle(match_types)
    
    match_type_counts = {}
    
    for i, match_type in enumerate(match_types[:num_samples]):
        # Pick a random career as the "target"
        target_career_id = random.choice(careers_list)
        target_vector = occupation_vectors[target_career_id]
        
        # Generate user vector based on match type
        user_vector, is_positive = generate_realistic_user_vector(
            target_vector, match_type, careers_list, occupation_vectors
        )
        
        # Verify actual similarity for quality control
        actual_similarity = cosine_similarity(
            user_vector.reshape(1, -1),
            target_vector.reshape(1, -1)
        )[0][0]
        
        # Adjust label based on actual similarity if needed
        if match_type in ['strong_match', 'moderate_match']:
            is_positive = True
        elif match_type in ['poor_match', 'partial_match', 'wrong_interests']:
            is_positive = False
        elif match_type == 'weak_match':
            # Weak matches: label based on threshold
            is_positive = actual_similarity > 0.45
        
        # Track match types
        if match_type not in match_type_counts:
            match_type_counts[match_type] = {'total': 0, 'positive': 0}
        match_type_counts[match_type]['total'] += 1
        if is_positive:
            match_type_counts[match_type]['positive'] += 1
        
        # Create feature representation
        feature_vector = np.concatenate([
            user_vector,
            target_vector,
            user_vector - target_vector
        ])
        
        X.append(feature_vector)
        y.append(1 if is_positive else 0)
    
    print(f"\nMatch type distribution:")
    for match_type, counts in match_type_counts.items():
        pct_positive = (counts['positive'] / counts['total'] * 100) if counts['total'] > 0 else 0
        print(f"  {match_type:20s}: {counts['total']:4d} samples ({counts['positive']:3d} positive, {pct_positive:5.1f}%)")
    
    return np.array(X), np.array(y), careers_list


def train_production_model(
    service: CareerRecommendationService,
    num_samples: int = 3000,
    test_size: float = 0.2,
    version: str = "1.0.0"
):
    """
    Train the recommendation model with realistic data
    """
    print("="*100)
    print("PRODUCTION MODEL TRAINING")
    print("="*100)
    print()
    
    # Generate realistic training data
    X, y, careers_list = generate_realistic_training_data(service, num_samples)
    
    print(f"\nTraining data shape: {X.shape}")
    print(f"Positive samples: {np.sum(y)} ({np.sum(y)/len(y)*100:.1f}%)")
    print(f"Negative samples: {np.sum(1-y)} ({np.sum(1-y)/len(y)*100:.1f}%)")
    print()
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"Train set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print()
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("Done.")
    print()
    
    # Train model
    print("Training logistic regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs',
        C=1.0  # Regularization parameter
    )
    
    model.fit(X_train_scaled, y_train)
    print("Training complete!")
    print()
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print("="*100)
    print("MODEL PERFORMANCE")
    print("="*100)
    print(f"Training accuracy: {train_score:.4f} ({train_score*100:.2f}%)")
    print(f"Test accuracy: {test_score:.4f} ({test_score*100:.2f}%)")
    print()
    
    # More detailed metrics
    from sklearn.metrics import classification_report, confusion_matrix
    
    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)
    
    print("Test Set Classification Report:")
    print(classification_report(y_test, test_pred, target_names=['Bad Match', 'Good Match']))
    print()
    
    print("Confusion Matrix (Test Set):")
    cm = confusion_matrix(y_test, test_pred)
    print(f"                Predicted")
    print(f"              Bad    Good")
    print(f"Actual Bad    {cm[0,0]:4d}   {cm[0,1]:4d}")
    print(f"       Good    {cm[1,0]:4d}   {cm[1,1]:4d}")
    print()
    
    # Model details
    coef = model.coef_[0]
    print("Model Statistics:")
    print(f"  - Features: {model.n_features_in_}")
    print(f"  - Non-zero coefficients: {np.count_nonzero(coef)} ({np.count_nonzero(coef)/len(coef)*100:.1f}%)")
    print(f"  - Mean |coefficient|: {np.mean(np.abs(coef)):.6f}")
    print(f"  - Intercept: {model.intercept_[0]:.6f}")
    print()
    
    # Save model artifacts
    print("Saving model artifacts...")
    service.save_model_artifacts(
        model=model,
        scaler=scaler,
        vectorizer=None,
        version=version
    )
    
    print("="*100)
    print("TRAINING COMPLETE")
    print("="*100)
    print()
    print("This model uses more realistic training data with:")
    print("  - Various match types (strong, moderate, weak, poor, partial)")
    print("  - More challenging examples that better simulate real users")
    print("  - Expected accuracy: 70-85% (more realistic for production)")
    print()
    
    return model, scaler


if __name__ == "__main__":
    # Set seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Initialize service
    service = CareerRecommendationService()
    
    # Train production model
    model, scaler = train_production_model(
        service,
        num_samples=3000,  # More samples for better learning
        test_size=0.2,
        version="1.0.0"
    )
    
    print("Model saved successfully!")
    print("This version uses realistic synthetic data generation.")









