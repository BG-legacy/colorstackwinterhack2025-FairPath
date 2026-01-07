"""
Model Retraining Script
Uses user feedback to improve career recommendation model
Run periodically (e.g., weekly) or when enough feedback is collected
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime

from services.feedback_service import FeedbackService
from services.data_processing import DataProcessingService


class ModelRetrainingService:
    """
    Retrain the career recommendation model using user feedback
    """
    
    def __init__(self):
        self.feedback_service = FeedbackService()
        self.data_service = DataProcessingService()
        self.artifacts_dir = Path("artifacts")
        self.models_dir = self.artifacts_dir / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def retrain_model(
        self,
        min_feedback_samples: int = 50,
        test_size: float = 0.2,
        save_model: bool = True
    ) -> Dict[str, any]:
        """
        Retrain the model using collected feedback
        
        Args:
            min_feedback_samples: Minimum feedback needed to retrain
            test_size: Fraction of data for testing
            save_model: Whether to save the retrained model
            
        Returns:
            Dictionary with training results and metrics
        """
        print("\n" + "="*60)
        print("STARTING MODEL RETRAINING")
        print("="*60)
        
        # Load feedback data
        feedback_df = self.feedback_service.get_training_data()
        
        if feedback_df is None or len(feedback_df) < min_feedback_samples:
            print(f"❌ Not enough feedback data. Have {len(feedback_df) if feedback_df is not None else 0}, need {min_feedback_samples}")
            return {
                "success": False,
                "reason": "insufficient_data",
                "feedback_count": len(feedback_df) if feedback_df is not None else 0
            }
        
        print(f"✓ Loaded {len(feedback_df)} feedback samples")
        
        # Load processed O*NET data
        processed_data = self.data_service.load_processed_data()
        
        # Build feature vectors from user profiles
        print("\n📊 Building feature vectors...")
        X = []  # Features
        y = []  # Labels (actual_label from feedback)
        career_ids = []
        
        for idx, row in feedback_df.iterrows():
            try:
                user_profile = row["user_profile"]
                
                # Build feature vector (same as in recommendation_service)
                features = self._build_feature_vector(
                    skills=user_profile.get("skills", []),
                    interests=user_profile.get("interests", {}),
                    values=user_profile.get("values", {}),
                    processed_data=processed_data
                )
                
                X.append(features)
                y.append(row["actual_label"])
                career_ids.append(row["career_id"])
                
            except Exception as e:
                print(f"Skipping row {idx}: {e}")
                continue
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"✓ Built {len(X)} feature vectors")
        print(f"  Feature dimensions: {X.shape[1]}")
        print(f"  Positive labels: {sum(y == 1.0)} ({sum(y == 1.0)/len(y)*100:.1f}%)")
        print(f"  Negative labels: {sum(y == 0.0)} ({sum(y == 0.0)/len(y)*100:.1f}%)")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        print(f"\n📚 Training on {len(X_train)} samples, testing on {len(X_test)} samples")
        
        # Train new model
        print("\n🔧 Training model...")
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'  # Handle imbalanced data
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
            "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        print("\n📈 Model Performance:")
        print(f"  Accuracy:  {metrics['accuracy']:.3f}")
        print(f"  Precision: {metrics['precision']:.3f}")
        print(f"  Recall:    {metrics['recall']:.3f}")
        print(f"  F1 Score:  {metrics['f1']:.3f}")
        
        # Save model
        if save_model:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save as new version
            new_model_path = self.models_dir / f"career_model_retrained_{timestamp}.pkl"
            joblib.dump(model, new_model_path)
            print(f"\n💾 Saved retrained model: {new_model_path}")
            
            # Optionally backup old model and replace main model
            main_model_path = self.models_dir / "career_model_v1.0.0.pkl"
            if main_model_path.exists():
                backup_path = self.models_dir / f"career_model_v1.0.0_backup_{timestamp}.pkl"
                import shutil
                shutil.copy(main_model_path, backup_path)
                print(f"📦 Backed up old model: {backup_path}")
            
            # Replace main model
            joblib.dump(model, main_model_path)
            print(f"✅ Updated main model: {main_model_path}")
        
        result = {
            "success": True,
            "feedback_count": len(feedback_df),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "metrics": metrics,
            "timestamp": timestamp if save_model else None
        }
        
        print("\n" + "="*60)
        print("RETRAINING COMPLETE ✅")
        print("="*60 + "\n")
        
        return result
    
    def _build_feature_vector(
        self,
        skills: list,
        interests: dict,
        values: dict,
        processed_data: dict
    ) -> np.ndarray:
        """
        Build feature vector from user profile
        (Simplified version - should match recommendation_service logic)
        """
        all_skills = processed_data.get("skill_names", [])
        skill_vector = np.zeros(len(all_skills))
        
        # Simple skill matching
        if skills:
            skill_lookup = {s.lower(): i for i, s in enumerate(all_skills)}
            for skill in skills:
                skill_lower = skill.lower()
                for skill_name, idx in skill_lookup.items():
                    if skill_lower in skill_name or skill_name in skill_lower:
                        skill_vector[idx] = 0.6  # Fixed importance
                        break
        
        # Interest vector (RIASEC)
        interest_vector = np.array([
            interests.get("Realistic", 0.0) / 7.0,
            interests.get("Investigative", 0.0) / 7.0,
            interests.get("Artistic", 0.0) / 7.0,
            interests.get("Social", 0.0) / 7.0,
            interests.get("Enterprising", 0.0) / 7.0,
            interests.get("Conventional", 0.0) / 7.0
        ])
        
        # Value vector
        value_vector = np.array([
            values.get("impact", 3.5) / 7.0,
            values.get("stability", 3.5) / 7.0,
            values.get("flexibility", 3.5) / 7.0
        ])
        
        # Combine all features
        feature_vector = np.concatenate([skill_vector, interest_vector, value_vector])
        
        return feature_vector


def main():
    """Run model retraining"""
    print("\n🤖 Career Recommendation Model Retraining Tool\n")
    
    retrainer = ModelRetrainingService()
    
    # Check feedback stats
    feedback_service = FeedbackService()
    stats = feedback_service.get_feedback_stats()
    
    print("Current Feedback Statistics:")
    print(f"  Total feedback: {stats.get('total_feedback', 0)}")
    print(f"  Unique users: {stats.get('unique_users', 0)}")
    print(f"  Unique careers: {stats.get('unique_careers', 0)}")
    print(f"  Feedback types: {stats.get('feedback_types', {})}")
    print()
    
    # Retrain
    result = retrainer.retrain_model(
        min_feedback_samples=50,
        test_size=0.2,
        save_model=True
    )
    
    if result["success"]:
        print("\n🎉 Model retraining successful!")
        print("   Restart your backend server to use the new model.")
    else:
        print(f"\n⚠️  Retraining not completed: {result.get('reason', 'unknown')}")


if __name__ == "__main__":
    main()






