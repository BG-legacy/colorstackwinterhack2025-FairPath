"""
Career Switch Intelligence Model
I'm analyzing career transitions by comparing skill vectors between occupations
This helps figure out what skills transfer, what needs learning, and how hard the switch would be
"""
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from services.data_processing import DataProcessingService
from services.openai_enhancement import OpenAIEnhancementService
from sklearn.metrics.pairwise import cosine_similarity


class CareerSwitchService:
    """
    Analyzes career transitions - skill overlap, transfer maps, difficulty, time estimates
    I'm keeping this pretty straightforward, just comparing what skills you have vs what you need
    """
    
    def __init__(self):
        self.data_service = DataProcessingService()
        self._processed_data = None
        self._occupation_skill_vectors = None
        self.openai_service = OpenAIEnhancementService()
    
    def load_processed_data(self) -> Dict[str, Any]:
        """Load processed data - caching it so I don't reload constantly"""
        if self._processed_data is None:
            self._processed_data = self.data_service.load_processed_data()
            if not self._processed_data:
                raise ValueError("Processed data not found. Run process_data.py first.")
        return self._processed_data
    
    def get_occupation_skill_vector(self, career_id: str) -> Optional[np.ndarray]:
        """Get the skill vector for a specific occupation"""
        processed_data = self.load_processed_data()
        
        for occ in processed_data["occupations"]:
            if occ["career_id"] == career_id:
                skill_vec = occ["skill_vector"]["combined"]
                return np.array(skill_vec)
        
        return None
    
    def compute_skill_overlap(
        self,
        source_career_id: str,
        target_career_id: str
    ) -> Dict[str, Any]:
        """
        Compute skill overlap percentage between two occupations
        I'm using cosine similarity on the skill vectors to get a percentage
        Also breaking down which skills transfer directly vs need learning
        """
        source_vec = self.get_occupation_skill_vector(source_career_id)
        target_vec = self.get_occupation_skill_vector(target_career_id)
        
        if source_vec is None or target_vec is None:
            return {
                "overlap_percentage": 0.0,
                "error": "One or both occupations not found"
            }
        
        # Cosine similarity gives us overlap - ranges from 0 to 1
        similarity = cosine_similarity(
            source_vec.reshape(1, -1),
            target_vec.reshape(1, -1)
        )[0][0]
        
        # Convert to percentage
        overlap_pct = float(similarity * 100)
        
        # Get skill names for detailed breakdown
        processed_data = self.load_processed_data()
        all_skills = processed_data["skill_names"]
        
        # Find skills that are important in both (transfers directly)
        # Skills that are important in target but not source (needs learning)
        # Skills that are nice to have but not critical (optional)
        transfers_directly = []
        needs_learning = []
        optional_skills = []
        
        # Thresholds - these are kind of arbitrary but seem reasonable
        # If both have skill > 0.3, it transfers directly
        # If target has > 0.4 and source < 0.2, needs learning
        # If target has 0.2-0.4, it's optional
        transfer_threshold = 0.3
        learning_threshold = 0.4
        optional_max = 0.4
        
        for i, skill_name in enumerate(all_skills):
            source_val = source_vec[i]
            target_val = target_vec[i]
            
            # Skip if target doesn't need this skill
            if target_val < 0.1:
                continue
            
            # Transfers directly - both occupations value this skill
            if source_val >= transfer_threshold and target_val >= transfer_threshold:
                transfers_directly.append({
                    "skill": skill_name,
                    "source_level": float(source_val),
                    "target_level": float(target_val)
                })
            # Needs learning - target needs it but source doesn't have it
            elif target_val >= learning_threshold and source_val < 0.2:
                needs_learning.append({
                    "skill": skill_name,
                    "source_level": float(source_val),
                    "target_level": float(target_val),
                    "gap": float(target_val - source_val)
                })
            # Optional - target has it but not critical
            elif target_val >= 0.2 and target_val < optional_max:
                optional_skills.append({
                    "skill": skill_name,
                    "source_level": float(source_val),
                    "target_level": float(target_val)
                })
        
        # Sort by importance
        transfers_directly.sort(key=lambda x: x["target_level"], reverse=True)
        needs_learning.sort(key=lambda x: x["gap"], reverse=True)
        optional_skills.sort(key=lambda x: x["target_level"], reverse=True)
        
        return {
            "overlap_percentage": overlap_pct,
            "transfers_directly": transfers_directly[:20],  # Top 20
            "needs_learning": needs_learning[:20],  # Top 20
            "optional_skills": optional_skills[:15],  # Top 15
            "num_transferable": len(transfers_directly),
            "num_to_learn": len(needs_learning),
            "num_optional": len(optional_skills)
        }
    
    def classify_difficulty(
        self,
        overlap_pct: float,
        num_to_learn: int,
        num_transferable: int
    ) -> str:
        """
        Classify transition difficulty as Low, Medium, or High
        I'm using a simple heuristic based on overlap and number of skills to learn
        Could be more sophisticated but this works for now
        """
        # High overlap (>70%) and few skills to learn = Low difficulty
        if overlap_pct >= 70 and num_to_learn <= 5:
            return "Low"
        
        # Low overlap (<40%) or lots of skills to learn (>15) = High difficulty
        if overlap_pct < 40 or num_to_learn > 15:
            return "High"
        
        # Everything else is Medium
        # Also if overlap is decent but still need to learn a bunch
        if overlap_pct >= 50 and num_to_learn <= 10:
            return "Medium"
        
        # Default to Medium if I'm not sure
        return "Medium"
    
    def estimate_transition_time(
        self,
        difficulty: str,
        num_to_learn: int,
        overlap_pct: float
    ) -> Dict[str, Any]:
        """
        Estimate transition time range - not absolute, just a rough guide
        I'm being conservative here, real transitions can vary a lot
        """
        # Base time in months - these are rough estimates
        if difficulty == "Low":
            base_months_min = 3
            base_months_max = 6
        elif difficulty == "Medium":
            base_months_min = 6
            base_months_max = 12
        else:  # High
            base_months_min = 12
            base_months_max = 24
        
        # Adjust based on number of skills to learn
        # Each skill adds roughly 0.5-1 month depending on complexity
        skill_adjustment = num_to_learn * 0.5
        
        # Adjust based on overlap - lower overlap means more time
        overlap_adjustment = (100 - overlap_pct) / 20  # Roughly 0-3 months
        
        min_months = int(base_months_min + skill_adjustment + overlap_adjustment)
        max_months = int(base_months_max + (skill_adjustment * 1.5) + (overlap_adjustment * 1.5))
        
        # Cap it at reasonable limits
        min_months = min(min_months, 36)
        max_months = min(max_months, 48)
        
        return {
            "min_months": min_months,
            "max_months": max_months,
            "range": f"{min_months}-{max_months} months",
            "note": "These are rough estimates. Actual time depends on learning pace, available resources, and job market conditions."
        }
    
    def assess_success_factors(
        self,
        source_career_id: str,
        target_career_id: str,
        overlap_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess success and risk factors for the transition
        I'm looking at skill gaps, education requirements, and market factors
        Trying to be realistic about what could go right or wrong
        """
        processed_data = self.load_processed_data()
        
        # Get occupation data
        source_occ = next(
            (occ for occ in processed_data["occupations"] if occ["career_id"] == source_career_id),
            None
        )
        target_occ = next(
            (occ for occ in processed_data["occupations"] if occ["career_id"] == target_career_id),
            None
        )
        
        if not source_occ or not target_occ:
            return {"error": "Occupation data not found"}
        
        success_factors = []
        risk_factors = []
        
        # Skill overlap analysis
        overlap_pct = overlap_data["overlap_percentage"]
        if overlap_pct >= 60:
            success_factors.append({
                "factor": "High skill overlap",
                "description": f"About {overlap_pct:.1f}% of your current skills transfer directly. This gives you a solid foundation.",
                "impact": "positive"
            })
        elif overlap_pct < 30:
            risk_factors.append({
                "factor": "Low skill overlap",
                "description": f"Only {overlap_pct:.1f}% skill overlap means you'll need to learn many new skills. This increases transition time and risk.",
                "impact": "negative"
            })
        
        # Number of skills to learn
        num_to_learn = overlap_data["num_to_learn"]
        if num_to_learn <= 5:
            success_factors.append({
                "factor": "Manageable learning curve",
                "description": f"Only {num_to_learn} critical skills need to be learned. This is a reasonable amount to tackle.",
                "impact": "positive"
            })
        elif num_to_learn > 15:
            risk_factors.append({
                "factor": "Steep learning curve",
                "description": f"You'll need to learn {num_to_learn} new skills. This requires significant time and effort investment.",
                "impact": "negative"
            })
        
        # Education level comparison
        source_ed = source_occ.get("education_data", {}).get("education_level")
        target_ed = target_occ.get("education_data", {}).get("education_level")
        
        if source_ed and target_ed:
            ed_levels = {
                "high_school": 0,
                "some_college": 1,
                "associates": 2,
                "bachelors": 3,
                "masters": 4,
                "professional": 4.5,
                "doctoral": 5
            }
            source_level = ed_levels.get(source_ed, 2.5)
            target_level = ed_levels.get(target_ed, 2.5)
            
            if target_level > source_level + 1:
                risk_factors.append({
                    "factor": "Education gap",
                    "description": f"Target career typically requires {target_ed} education, while your current role requires {source_ed}. You may need additional education or certifications.",
                    "impact": "negative"
                })
            elif target_level <= source_level:
                success_factors.append({
                    "factor": "Education requirements met",
                    "description": f"Your current education level ({source_ed}) meets or exceeds the target requirement ({target_ed}).",
                    "impact": "positive"
                })
        
        # Market outlook
        target_outlook = target_occ.get("outlook_features", {})
        growth_rate = target_outlook.get("growth_rate", 0)
        
        if growth_rate > 10:
            success_factors.append({
                "factor": "Strong market growth",
                "description": f"Target career is growing at {growth_rate:.1f}% annually. This means more job opportunities and potentially better job security.",
                "impact": "positive"
            })
        elif growth_rate < -5:
            risk_factors.append({
                "factor": "Declining market",
                "description": f"Target career is declining at {abs(growth_rate):.1f}% annually. This could mean fewer opportunities and increased competition.",
                "impact": "negative"
            })
        
        # Wage comparison
        source_wage = source_occ.get("outlook_features", {}).get("median_wage_2024")
        target_wage = target_outlook.get("median_wage_2024")
        
        if source_wage and target_wage:
            wage_change = ((target_wage - source_wage) / source_wage) * 100
            if wage_change > 20:
                success_factors.append({
                    "factor": "Potential wage increase",
                    "description": f"Target career has median wage ${target_wage:,.0f} vs your current ${source_wage:,.0f}. This represents a {wage_change:.1f}% increase.",
                    "impact": "positive"
                })
            elif wage_change < -10:
                risk_factors.append({
                    "factor": "Potential wage decrease",
                    "description": f"Target career has median wage ${target_wage:,.0f} vs your current ${source_wage:,.0f}. This represents a {abs(wage_change):.1f}% decrease.",
                    "impact": "negative"
                })
        
        # Overall assessment
        num_success = len(success_factors)
        num_risks = len(risk_factors)
        
        if num_success > num_risks * 1.5:
            overall_assessment = "Favorable transition with more positive factors than risks"
        elif num_risks > num_success * 1.5:
            overall_assessment = "Challenging transition with significant risks to consider"
        else:
            overall_assessment = "Moderate transition with balanced factors"
        
        return {
            "success_factors": success_factors,
            "risk_factors": risk_factors,
            "overall_assessment": overall_assessment,
            "num_success_factors": num_success,
            "num_risk_factors": num_risks
        }
    
    def analyze_career_switch(
        self,
        source_career_id: str,
        target_career_id: str
    ) -> Dict[str, Any]:
        """
        Main method - analyze a career switch from source to target
        Returns everything: overlap, transfer map, difficulty, time estimate, success/risk factors
        """
        # Get skill overlap and transfer map
        overlap_data = self.compute_skill_overlap(source_career_id, target_career_id)
        
        if "error" in overlap_data:
            return overlap_data
        
        # Classify difficulty
        difficulty = self.classify_difficulty(
            overlap_data["overlap_percentage"],
            overlap_data["num_to_learn"],
            overlap_data["num_transferable"]
        )
        
        # Estimate transition time
        time_estimate = self.estimate_transition_time(
            difficulty,
            overlap_data["num_to_learn"],
            overlap_data["overlap_percentage"]
        )
        
        # Assess success and risk factors
        success_risk = self.assess_success_factors(
            source_career_id,
            target_career_id,
            overlap_data
        )
        
        # Get occupation names for display
        processed_data = self.load_processed_data()
        source_occ = next(
            (occ for occ in processed_data["occupations"] if occ["career_id"] == source_career_id),
            None
        )
        target_occ = next(
            (occ for occ in processed_data["occupations"] if occ["career_id"] == target_career_id),
            None
        )
        
        # Get certifications for the target career using OpenAI
        certifications = self.openai_service.get_career_certifications(
            career_name=target_occ["name"] if target_occ else target_career_id,
            career_data=target_occ
        )
        
        return {
            "source_career": {
                "career_id": source_career_id,
                "name": source_occ["name"] if source_occ else source_career_id
            },
            "target_career": {
                "career_id": target_career_id,
                "name": target_occ["name"] if target_occ else target_career_id
            },
            "skill_overlap": {
                "percentage": overlap_data["overlap_percentage"],
                "transferable_skills_count": overlap_data["num_transferable"],
                "skills_to_learn_count": overlap_data["num_to_learn"],
                "optional_skills_count": overlap_data["num_optional"]
            },
            "transfer_map": {
                "transfers_directly": overlap_data["transfers_directly"],
                "needs_learning": overlap_data["needs_learning"],
                "optional_skills": overlap_data["optional_skills"]
            },
            "difficulty": difficulty,
            "transition_time": time_estimate,
            "success_risk_assessment": success_risk,
            "certifications": certifications
        }
    
    def analyze_career_switch_by_name(
        self,
        source_career_name: str,
        target_career_name: str
    ) -> Dict[str, Any]:
        """
        Analyze a career switch using career names directly (no database lookup).
        Uses OpenAI to generate the analysis based on the career names.
        """
        if not self.openai_service.is_available():
            return {
                "error": "OpenAI service is not available. Please configure OPENAI_API_KEY."
            }
        
        try:
            # Use OpenAI to generate career switch analysis
            prompt = f"""Analyze a career switch transition from "{source_career_name}" to "{target_career_name}".

Provide a comprehensive analysis in JSON format with the following structure:
{{
  "overlap_percentage": <number between 0-100>,
  "difficulty": "<Low|Medium|High>",
  "transition_time_range": {{
    "min_months": <number>,
    "max_months": <number>,
    "range": "<min>-<max> months",
    "note": "<brief note>"
  }},
  "skill_translation_map": {{
    "transfers_directly": [
      {{"skill": "<skill name>", "source_level": <0-1>, "target_level": <0-1>}}
    ],
    "needs_learning": [
      {{"skill": "<skill name>", "source_level": <0-1>, "target_level": <0-1>, "gap": <0-1>}}
    ],
    "optional_skills": [
      {{"skill": "<skill name>", "source_level": <0-1>, "target_level": <0-1>}}
    ]
  }},
  "success_factors": [
    {{"factor": "<factor name>", "description": "<description>", "impact": "positive"}}
  ],
  "risk_factors": [
    {{"factor": "<factor name>", "description": "<description>", "impact": "negative"}}
  ],
  "overall_assessment": "<2-3 sentence overall assessment>"
}}

Guidelines:
- overlap_percentage: Estimate how much of the source career's skills transfer to the target (0-100)
- difficulty: Low (high overlap, few new skills), Medium (moderate overlap), High (low overlap, many new skills)
- transition_time_range: Realistic time estimate in months based on difficulty and skills to learn
- skill_translation_map: List 5-10 key skills in each category (transfers_directly, needs_learning, optional_skills)
- success_factors: 3-5 positive factors that would help the transition
- risk_factors: 2-4 challenges or risks to consider
- Be realistic and specific based on the actual careers mentioned

Return ONLY valid JSON, no other text."""

            from app.config import settings
            import json
            
            # Get the correct max tokens parameter based on model
            max_tokens_param = self.openai_service.get_max_tokens_param(settings.OPENAI_MODEL, 2000)
            
            # Try with json_object format first (if model supports it)
            try:
                response = self.openai_service._call_with_retry(
                    lambda: self.openai_service.client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "You're a career transition expert. Provide detailed, realistic career switch analysis in JSON format only."},
                            {"role": "user", "content": prompt}
                        ],
                        **max_tokens_param,
                        temperature=0.5,
                        response_format={"type": "json_object"}
                    )
                )
            except Exception as e:
                print(f"JSON object format not supported, trying without: {e}")
                response = None
            
            # If that fails, try without json_object format
            if response is None or (hasattr(response, 'choices') and len(response.choices) > 0 and not response.choices[0].message.content):
                response = self.openai_service._call_with_retry(
                    lambda: self.openai_service.client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "You're a career transition expert. Provide detailed, realistic career switch analysis in JSON format only. Return ONLY valid JSON, no markdown, no code blocks."},
                            {"role": "user", "content": prompt}
                        ],
                        **max_tokens_param,
                        temperature=0.5
                    )
                )
            
            if response is None:
                return {"error": "Failed to generate analysis with OpenAI"}
            
            # Get the content from response
            if not hasattr(response, 'choices') or len(response.choices) == 0:
                return {"error": "OpenAI response has no choices"}
            
            result_text = response.choices[0].message.content
            if not result_text:
                return {"error": "OpenAI response is empty"}
            
            result_text = result_text.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            if not result_text:
                return {"error": "OpenAI response is empty after cleaning"}
            
            try:
                analysis = json.loads(result_text)
                
                # Ensure all required fields exist
                return {
                    "overlap_percentage": analysis.get("overlap_percentage", 50),
                    "difficulty": analysis.get("difficulty", "Medium"),
                    "transition_time_range": analysis.get("transition_time_range", {
                        "min_months": 6,
                        "max_months": 12,
                        "range": "6-12 months",
                        "note": "Estimated transition time"
                    }),
                    "skill_translation_map": analysis.get("skill_translation_map", {
                        "transfers_directly": [],
                        "needs_learning": [],
                        "optional_skills": []
                    }),
                    "success_factors": analysis.get("success_factors", []),
                    "risk_factors": analysis.get("risk_factors", []),
                    "overall_assessment": analysis.get("overall_assessment", "Career switch analysis completed."),
                    "source_career": {
                        "career_id": f"custom_{source_career_name.lower().replace(' ', '_')}",
                        "name": source_career_name
                    },
                    "target_career": {
                        "career_id": f"custom_{target_career_name.lower().replace(' ', '_')}",
                        "name": target_career_name
                    }
                }
            except json.JSONDecodeError as e:
                print(f"Failed to parse OpenAI response: {e}")
                print(f"Response was: {result_text[:500]}")  # Print first 500 chars
                return {"error": f"Failed to parse analysis response: {str(e)}"}
                
        except Exception as e:
            import traceback
            print(f"OpenAI career switch analysis failed: {e}")
            print(traceback.format_exc())
            return {"error": f"Failed to analyze career switch: {str(e)}"}


