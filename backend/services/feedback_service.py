"""
Feedback Service
Collects user feedback to improve career recommendations
Supports model retraining and personalized career lists
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd


class FeedbackService:
    """
    Collects and manages user feedback on career recommendations
    Used for model retraining and improving match quality
    """
    
    def __init__(self, feedback_dir: str = "artifacts/feedback"):
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.feedback_dir / "career_feedback.jsonl"
        self.user_careers_file = self.feedback_dir / "user_selected_careers.json"
        self.global_careers_file = self.feedback_dir / "popular_careers.json"
    
    def record_feedback(
        self,
        user_id: Optional[str],
        user_profile: Dict[str, Any],
        career_id: str,
        career_name: str,
        soc_code: str,
        feedback_type: str,
        predicted_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record user feedback on a career recommendation
        
        Args:
            user_id: User identifier (optional, can be anonymous)
            user_profile: {
                "skills": [...],
                "interests": {...},
                "values": {...},
                "constraints": {...}
            }
            career_id: Career identifier
            career_name: Career name
            soc_code: SOC code
            feedback_type: "selected", "liked", "disliked", "applied", "hired"
            predicted_score: What score the model gave (0.0-1.0)
            metadata: Additional info (time_to_decision, ranking_position, etc.)
            
        Returns:
            True if recorded successfully
        """
        try:
            feedback_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id or "anonymous",
                "user_profile": user_profile,
                "career_id": career_id,
                "career_name": career_name,
                "soc_code": soc_code,
                "feedback_type": feedback_type,
                "predicted_score": predicted_score,
                "actual_label": self._feedback_to_label(feedback_type),
                "metadata": metadata or {}
            }
            
            # Append to JSONL file (one JSON per line)
            with open(self.feedback_file, "a") as f:
                f.write(json.dumps(feedback_entry) + "\n")
            
            # Update user-specific career list
            if user_id and feedback_type in ["selected", "hired"]:
                self._add_to_user_careers(user_id, career_name, soc_code, feedback_type)
            
            # Update global popular careers
            if feedback_type in ["selected", "liked", "hired"]:
                self._update_popular_careers(career_name, soc_code, feedback_type)
            
            print(f"Recorded feedback: {feedback_type} for {career_name} (user: {user_id or 'anonymous'})")
            return True
            
        except Exception as e:
            print(f"Failed to record feedback: {e}")
            return False
    
    def _feedback_to_label(self, feedback_type: str) -> float:
        """
        Convert feedback type to numerical label for training
        
        Returns:
            1.0 for positive feedback
            0.0 for negative feedback
            0.5 for neutral/partial feedback
        """
        positive = ["selected", "liked", "applied", "hired"]
        negative = ["disliked", "rejected"]
        
        if feedback_type in positive:
            return 1.0
        elif feedback_type in negative:
            return 0.0
        else:
            return 0.5
    
    def _add_to_user_careers(self, user_id: str, career_name: str, soc_code: str, feedback_type: str):
        """Add career to user's personal career list"""
        try:
            # Load existing user careers
            if self.user_careers_file.exists():
                with open(self.user_careers_file, "r") as f:
                    user_careers = json.load(f)
            else:
                user_careers = {}
            
            # Add to user's list
            if user_id not in user_careers:
                user_careers[user_id] = []
            
            # Check if already exists
            existing = [c for c in user_careers[user_id] if c["soc_code"] == soc_code]
            if not existing:
                user_careers[user_id].append({
                    "career_name": career_name,
                    "soc_code": soc_code,
                    "feedback_type": feedback_type,
                    "added_date": datetime.utcnow().isoformat()
                })
            
            # Save
            with open(self.user_careers_file, "w") as f:
                json.dump(user_careers, f, indent=2)
                
        except Exception as e:
            print(f"Failed to update user careers: {e}")
    
    def _update_popular_careers(self, career_name: str, soc_code: str, feedback_type: str):
        """Update global popular careers list"""
        try:
            # Load existing popular careers
            if self.global_careers_file.exists():
                with open(self.global_careers_file, "r") as f:
                    popular = json.load(f)
            else:
                popular = {}
            
            # Update count
            key = f"{soc_code}|{career_name}"
            if key not in popular:
                popular[key] = {
                    "career_name": career_name,
                    "soc_code": soc_code,
                    "total_selections": 0,
                    "total_likes": 0,
                    "total_hires": 0
                }
            
            if feedback_type == "selected":
                popular[key]["total_selections"] += 1
            elif feedback_type == "liked":
                popular[key]["total_likes"] += 1
            elif feedback_type == "hired":
                popular[key]["total_hires"] += 1
            
            # Save
            with open(self.global_careers_file, "w") as f:
                json.dump(popular, f, indent=2)
                
        except Exception as e:
            print(f"Failed to update popular careers: {e}")
    
    def get_user_careers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get careers selected by a specific user"""
        try:
            if self.user_careers_file.exists():
                with open(self.user_careers_file, "r") as f:
                    user_careers = json.load(f)
                return user_careers.get(user_id, [])
        except Exception as e:
            print(f"Failed to get user careers: {e}")
        return []
    
    def get_popular_careers(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Get globally popular careers based on user feedback"""
        try:
            if self.global_careers_file.exists():
                with open(self.global_careers_file, "r") as f:
                    popular = json.load(f)
                
                # Convert to list and sort by total selections
                careers = list(popular.values())
                careers.sort(
                    key=lambda x: (
                        x.get("total_hires", 0) * 3 +  # Weight hires heavily
                        x.get("total_selections", 0) * 2 +  # Weight selections
                        x.get("total_likes", 0)  # Weight likes
                    ),
                    reverse=True
                )
                return careers[:top_n]
        except Exception as e:
            print(f"Failed to get popular careers: {e}")
        return []
    
    def get_training_data(self) -> Optional[pd.DataFrame]:
        """
        Load all feedback data for model retraining
        
        Returns:
            DataFrame with columns:
            - skills, interests, values, constraints (features)
            - career_id, predicted_score, actual_label (labels)
        """
        try:
            if not self.feedback_file.exists():
                print("No feedback data available yet")
                return None
            
            # Read JSONL file
            feedback_data = []
            with open(self.feedback_file, "r") as f:
                for line in f:
                    if line.strip():
                        feedback_data.append(json.loads(line))
            
            if not feedback_data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(feedback_data)
            print(f"Loaded {len(df)} feedback records for training")
            return df
            
        except Exception as e:
            print(f"Failed to load training data: {e}")
            return None
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get statistics about collected feedback"""
        try:
            df = self.get_training_data()
            if df is None or len(df) == 0:
                return {
                    "total_feedback": 0,
                    "unique_users": 0,
                    "unique_careers": 0,
                    "feedback_types": {}
                }
            
            stats = {
                "total_feedback": len(df),
                "unique_users": df["user_id"].nunique(),
                "unique_careers": df["career_id"].nunique(),
                "feedback_types": df["feedback_type"].value_counts().to_dict(),
                "avg_predicted_score": df["predicted_score"].mean(),
                "popular_careers": df["career_name"].value_counts().head(10).to_dict()
            }
            return stats
            
        except Exception as e:
            print(f"Failed to get feedback stats: {e}")
            return {}
    
    def clear_feedback(self, before_date: Optional[str] = None):
        """
        Clear feedback data (for testing or privacy)
        
        Args:
            before_date: ISO date string, clear feedback before this date
        """
        if before_date:
            # TODO: Implement date-based filtering
            print(f"Clearing feedback before {before_date}")
        else:
            # Clear all
            if self.feedback_file.exists():
                os.remove(self.feedback_file)
            print("Cleared all feedback data")




