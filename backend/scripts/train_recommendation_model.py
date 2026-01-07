"""
Training script for career recommendation model
I'm training a simple linear classifier that learns to rank careers based on user features
This should be reproducible - same data should give same results
"""
import numpy as np
from pathlib import Path
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import random

# Add parent directory to path so I can import services
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.recommendation_service import CareerRecommendationService
from services.data_processing import DataProcessingService


def generate_synthetic_training_data(service: CareerRecommendationService, num_samples: int = 1000):
    """
    Generate synthetic training data since we don't have real user-career matches
    I'm creating pairs where user vectors similar to career vectors get positive labels
    This is a simple approach - in production you'd use real user data
    """
    processed_data = service.load_processed_data()
    occupation_vectors = service.build_occupation_vectors()
    
    X = []  # Feature pairs (user_vector, occupation_vector combined)
    y = []  # Labels (1 = good match, 0 = bad match)
    
    all_skills = processed_data["skill_names"]
    careers_list = list(occupation_vectors.keys())
    
    print(f"Generating {num_samples} training samples...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    for i in range(num_samples):
        # Pick a random career as the "target"
        target_career_id = random.choice(careers_list)
        target_vector = occupation_vectors[target_career_id]
        
        # Create user vector - for positive samples, make it similar to target
        # For negative samples, make it different
        is_positive = random.random() > 0.5
        
        if is_positive:
            # Positive sample: user vector similar to target (add some noise)
            noise = np.random.normal(0, 0.1, size=target_vector.shape)
            user_vector = np.clip(target_vector + noise, 0, 1)
        else:
            # Negative sample: user vector different from target
            user_vector = np.random.random(size=target_vector.shape)
        
        # Create feature representation: concatenate user and career vectors, plus difference
        # This gives the model information about both vectors and their relationship
        feature_vector = np.concatenate([
            user_vector,
            target_vector,
            user_vector - target_vector  # Difference helps model understand alignment
        ])
        
        X.append(feature_vector)
        y.append(1 if is_positive else 0)
    
    return np.array(X), np.array(y), careers_list


def train_model(
    service: CareerRecommendationService,
    num_samples: int = 1000,
    test_size: float = 0.2,
    version: str = "1.0.0"
):
    """
    Train the recommendation model
    I'm using a logistic regression classifier - simple but works well for ranking
    """
    print("Starting model training...")
    
    # Generate training data
    X, y, careers_list = generate_synthetic_training_data(service, num_samples)
    
    print(f"Training data shape: {X.shape}")
    print(f"Positive samples: {np.sum(y)}, Negative samples: {np.sum(1-y)}")
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Scale features - this helps the model learn better
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model - using logistic regression for now
    # Could upgrade to more complex models later, but this works fine
    print("Training logistic regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs'  # Good solver for this type of problem
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f"Train accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    # Save model artifacts
    service.save_model_artifacts(
        model=model,
        scaler=scaler,
        vectorizer=None,  # Not using vectorizer in this simple setup
        version=version
    )
    
    print("Model training complete!")
    return model, scaler


if __name__ == "__main__":
    # Set seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Initialize service
    service = CareerRecommendationService()
    
    # Train model
    model, scaler = train_model(
        service,
        num_samples=2000,  # More samples = better model usually
        test_size=0.2,
        version="1.0.0"
    )
    
    print("\nModel saved successfully!")
    print("You can now use CareerRecommendationService.load_model_artifacts() to load it")









