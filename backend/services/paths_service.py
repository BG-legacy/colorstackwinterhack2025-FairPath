"""
Education Paths Service
Generates education pathways for careers with cost, time, pros, and tradeoffs
"""
import json
from typing import Dict, List, Optional, Any
from services.data_processing import DataProcessingService
from services.openai_enhancement import OpenAIEnhancementService
from app.config import settings


class PathsService:
    """
    Service for generating education pathways for careers
    Returns 3-5 pathways with cost range, time range, pros, and tradeoffs
    """
    
    def __init__(self):
        self.data_service = DataProcessingService()
        self.openai_service = OpenAIEnhancementService()
        self._processed_data = None
    
    def load_processed_data(self) -> Dict[str, Any]:
        """Load processed data - caching it so we don't reload constantly"""
        if self._processed_data is None:
            self._processed_data = self.data_service.load_processed_data()
            if not self._processed_data:
                raise ValueError("Processed data not found. Run process_data.py first.")
        return self._processed_data
    
    def get_occupation_data(self, career_id: str) -> Optional[Dict[str, Any]]:
        """Get all processed data for a specific occupation"""
        processed_data = self.load_processed_data()
        
        for occ in processed_data["occupations"]:
            if occ["career_id"] == career_id:
                return occ
        
        return None
    
    def generate_education_paths(
        self,
        career_name: str,
        career_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate 3-5 education pathways for a career
        Returns pathways with cost range, time range, pros, and tradeoffs
        """
        if not self.openai_service.is_available():
            return {
                "pathways": [],
                "available": False,
                "message": "OpenAI service not available. Set OPENAI_API_KEY to enable pathway generation."
            }
        
        try:
            # Build context about the career
            context_parts = [f"Career: {career_name}"]
            
            if career_data:
                # Add relevant career information
                education = career_data.get('education_data', {})
                if education.get('education_level'):
                    context_parts.append(f"Typical Education: {education.get('education_level')}")
                if education.get('typical_entry_education'):
                    context_parts.append(f"Entry Education: {education.get('typical_entry_education')}")
                
                outlook = career_data.get('outlook_features', {})
                if outlook.get('median_wage_2024'):
                    context_parts.append(f"Median Wage: ${outlook.get('median_wage_2024'):,.0f}")
                if outlook.get('growth_rate'):
                    context_parts.append(f"Growth Rate: {outlook.get('growth_rate'):.1f}%")
            
            context = "\n".join(context_parts)
            
            prompt = f"""You're an education and career pathway expert. For this career, recommend 3-5 distinct education pathways:

{context}

Provide 3-5 pathways in this exact JSON format:
{{
  "pathways": [
    {{
      "name": "Pathway Name (e.g., 'Traditional 4-Year Degree', 'Bootcamp + Experience', 'Associate + Certifications')",
      "cost_range": {{
        "min": 10000,
        "max": 50000,
        "currency": "USD",
        "description": "Brief description of cost factors"
      }},
      "time_range": {{
        "min_months": 12,
        "max_months": 48,
        "description": "Brief description of time commitment"
      }},
      "pros": [
        "Pro point 1",
        "Pro point 2",
        "Pro point 3"
      ],
      "tradeoffs": [
        "Tradeoff 1",
        "Tradeoff 2"
      ],
      "description": "Brief overview of this pathway"
    }}
  ]
}}

Guidelines:
- Provide 3-5 distinct pathways (e.g., traditional degree, bootcamp, apprenticeship, associate degree, self-taught with certs)
- Cost ranges should be realistic (include tuition, fees, materials, opportunity cost if significant)
- Time ranges should be realistic (including any prerequisites, part-time vs full-time options)
- Pros should highlight the advantages (speed, cost, recognition, flexibility, etc.)
- Tradeoffs should be honest about downsides (recognition, depth, time, cost, etc.)
- Be specific and realistic - actual numbers matter

Return ONLY valid JSON, no other text."""
            
            # Get the correct max tokens parameter based on model
            max_tokens_param = self.openai_service.get_max_tokens_param(settings.OPENAI_MODEL, 2000)
            
            # Try with json_object format first, fallback to regular if not supported
            try:
                response = self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're an education and career pathway expert. Provide accurate, realistic education pathway recommendations in JSON format only."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
            except Exception as e:
                # Fallback if json_object format not supported
                print(f"JSON object format not supported, using regular format: {e}")
                response = self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're an education and career pathway expert. Provide accurate, realistic education pathway recommendations in JSON format only. Return ONLY valid JSON, no markdown, no code blocks."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7
                )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                
                # Ensure we have the right structure
                pathways_data = {
                    "pathways": result.get("pathways", []),
                    "available": True
                }
                
                # Validate we have 3-5 pathways
                if len(pathways_data["pathways"]) < 3:
                    pathways_data["available"] = False
                    pathways_data["message"] = "Generated fewer than 3 pathways"
                elif len(pathways_data["pathways"]) > 5:
                    pathways_data["pathways"] = pathways_data["pathways"][:5]
                
                return pathways_data
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse pathways JSON: {e}")
                print(f"Response was: {result_text}")
                return {
                    "pathways": [],
                    "available": False,
                    "error": "Failed to parse response"
                }
            
        except Exception as e:
            print(f"OpenAI pathways generation failed: {e}")
            return {
                "pathways": [],
                "available": False,
                "error": str(e)
            }
    
    def get_education_paths(self, career_id: str) -> Dict[str, Any]:
        """
        Main method - get education pathways for a career
        """
        occ_data = self.get_occupation_data(career_id)
        
        if not occ_data:
            return {
                "error": f"Occupation with career_id {career_id} not found"
            }
        
        # Generate pathways using OpenAI
        pathways_result = self.generate_education_paths(
            career_name=occ_data.get("name"),
            career_data=occ_data
        )
        
        if "error" in pathways_result:
            return pathways_result
        
        return {
            "career": {
                "career_id": career_id,
                "name": occ_data.get("name"),
                "soc_code": occ_data.get("soc_code")
            },
            "pathways": pathways_result.get("pathways", []),
            "available": pathways_result.get("available", False)
        }

