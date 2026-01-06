"""
OpenAI enhancement service - uses GPT to improve recommendations
I'm using OpenAI to add better explanations and refine the ML results
This makes the recommendations more accurate and easier to understand
"""
import json
import time
from typing import Dict, List, Optional, Any, Callable
from openai import OpenAI, APITimeoutError, APIError
from app.config import settings


class OpenAIEnhancementService:
    """
    Uses OpenAI to enhance career recommendations
    Adds better explanations and can refine the ranking
    
    Includes timeout and retry logic for reliability
    """
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                # Initialize client - timeout handled via httpx.Timeout or in retry logic
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.client is not None
    
    @staticmethod
    def get_max_tokens_param(model: str, max_tokens: int) -> Dict[str, int]:
        """
        Get the correct parameter name for max tokens based on the model.
        gpt-5.2 uses max_completion_tokens, other models use max_tokens.
        Returns a dict with the correct parameter name and value.
        """
        if model.startswith("gpt-5"):
            return {"max_completion_tokens": max_tokens}
        else:
            return {"max_tokens": max_tokens}
    
    def _call_with_retry(self, api_call: Callable) -> Any:
        """
        Call OpenAI API with retry logic and exponential backoff
        Returns the response or None if all retries fail
        """
        if not self.is_available():
            return None
        
        max_retries = settings.OPENAI_MAX_RETRIES
        delay = settings.OPENAI_RETRY_DELAY
        
        for attempt in range(max_retries + 1):
            try:
                return api_call()
            except (APITimeoutError, APIError, TimeoutError) as e:
                if attempt < max_retries:
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    print(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {wait_time:.1f}s: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"OpenAI API call failed after {max_retries + 1} attempts: {e}")
                    return None
            except Exception as e:
                # For other exceptions, don't retry
                print(f"OpenAI API call failed with non-retryable error: {e}")
                return None
        
        return None
    
    def enhance_recommendation_explanation(
        self,
        career_name: str,
        user_skills: List[str],
        user_interests: Optional[Dict[str, float]] = None,
        match_score: float = 0.0,
        top_skills: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Use OpenAI to create a better explanation for why this career was recommended
        Makes it more natural and easier to understand
        """
        if not self.is_available():
            return {
                "enhanced_explanation": None,
                "why_this_career": None,
                "next_steps": None
            }
        
        try:
            # Build context for OpenAI
            skills_text = ", ".join(user_skills[:5]) if user_skills else "various skills"
            interests_text = ""
            if user_interests:
                top_interests = sorted(user_interests.items(), key=lambda x: x[1], reverse=True)[:3]
                interests_text = f"Interests: {', '.join([f'{k} ({v})' for k, v in top_interests])}"
            
            top_skills_text = ""
            if top_skills:
                skill_names = [s.get('skill', '') for s in top_skills[:3]]
                top_skills_text = f"Key matching skills: {', '.join(skill_names)}"
            
            prompt = f"""You're helping someone understand why a career was recommended to them.

Career: {career_name}
Match Score: {match_score:.1%}
User Skills: {skills_text}
{interests_text}
{top_skills_text}

Create a brief, friendly explanation (2-3 sentences) explaining:
1. Why this career matches their skills/interests
2. What makes it a good fit
3. One practical next step they could take

Keep it casual and encouraging, like you're talking to a friend."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 200)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a helpful career advisor. Give friendly, practical advice."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7
                )
            )
            
            if response is None:
                return {
                    "enhanced_explanation": None,
                    "why_this_career": None,
                    "next_steps": None
                }
            
            explanation = response.choices[0].message.content.strip()
            
            return {
                "enhanced_explanation": explanation,
                "why_this_career": explanation.split('.')[0] + '.' if '.' in explanation else explanation,
                "next_steps": explanation.split('.')[-1].strip() if '.' in explanation else None
            }
            
        except Exception as e:
            print(f"OpenAI enhancement failed: {e}")
            return {
                "enhanced_explanation": None,
                "why_this_career": None,
                "next_steps": None
            }
    
    def refine_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use OpenAI to potentially re-rank or refine recommendations
        Can catch edge cases the ML model might miss
        """
        if not self.is_available() or len(recommendations) == 0:
            return recommendations
        
        try:
            # Build context
            top_3 = recommendations[:3]
            careers_list = "\n".join([
                f"{i+1}. {r['name']} (score: {r['score']:.1%})"
                for i, r in enumerate(top_3)
            ])
            
            user_skills = user_profile.get('skills', [])
            skills_text = ", ".join(user_skills[:5]) if user_skills else "various skills"
            
            prompt = f"""I have ML model recommendations for a user. Review if the order makes sense.

User Skills: {skills_text}
User Interests: {user_profile.get('interests', {})}

Top Recommendations:
{careers_list}

Quickly review: Does this ranking make logical sense? If yes, just say "ORDER_OK". 
If the order should change, suggest the better order (just numbers like "2,1,3").

Keep response very short."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 50)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career matching expert. Be concise."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.3
                )
            )
            
            if response is None:
                return recommendations
            
            result = response.choices[0].message.content.strip()
            
            # If OpenAI suggests reordering, apply it
            if result != "ORDER_OK" and "," in result:
                try:
                    new_order = [int(x.strip()) - 1 for x in result.split(",")]
                    if len(new_order) == len(top_3) and all(0 <= i < len(recommendations) for i in new_order):
                        # Reorder top 3
                        reordered = [recommendations[i] for i in new_order]
                        return reordered + recommendations[3:]
                except:
                    pass  # If parsing fails, just return original
            
            return recommendations
            
        except Exception as e:
            print(f"OpenAI refinement failed: {e}")
            return recommendations
    
    def suggest_additional_careers(
        self,
        user_profile: Dict[str, Any],
        existing_recommendations: List[Dict[str, Any]],
        all_careers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use OpenAI to suggest additional careers that might be a better fit
        based on user data, even if ML model didn't rank them highly
        """
        if not self.is_available():
            return []
        
        try:
            user_skills = user_profile.get('skills', [])
            user_interests = user_profile.get('interests', {})
            user_values = user_profile.get('values', {})
            constraints = user_profile.get('constraints', {})
            
            skills_text = ", ".join(user_skills[:8]) if user_skills else "various skills"
            interests_text = ", ".join([f"{k} ({v})" for k, v in list(user_interests.items())[:3]]) if user_interests else ""
            
            existing_names = [r['name'] for r in existing_recommendations[:5]]
            existing_text = ", ".join(existing_names)
            
            # Get list of all career names (limited to avoid token limits)
            all_career_names = [c.get('name', '') for c in all_careers[:50]]  # Limit to 50 for token efficiency
            careers_text = ", ".join(all_career_names[:30])  # Show first 30
            
            prompt = f"""I have ML model recommendations for a user, but I want to check if there are better career matches.

User Profile:
- Skills: {skills_text}
- Interests: {interests_text}
- Values: {user_values if user_values else 'Not specified'}
- Constraints: {constraints if constraints else 'None'}

Current ML Recommendations:
{existing_text}

Available Careers (sample):
{careers_text}

Based on the user's profile, suggest 1-2 additional careers that might be a GREAT fit but weren't in the ML top results. 
Consider:
- Skills alignment
- Interest match
- Career transition paths
- Realistic opportunities

Respond with ONLY career names, one per line. If no better matches, say "NONE".
Be specific with career titles."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 100)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career matching expert. Suggest careers that genuinely fit the user profile."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.5
                )
            )
            
            if response is None:
                return []
            
            result = response.choices[0].message.content.strip()
            
            if "NONE" in result.upper() or not result:
                return []
            
            # Parse suggested career names
            suggested_careers = []
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            for line in lines[:2]:  # Max 2 suggestions
                # Try to find matching career in our database
                for career in all_careers:
                    career_name = career.get('name', '')
                    # Fuzzy match - check if suggested name is similar to career name
                    if line.lower() in career_name.lower() or career_name.lower() in line.lower():
                        # Create a recommendation entry for this career
                        suggested_careers.append({
                            "career_id": career.get('career_id', ''),
                            "name": career_name,
                            "soc_code": career.get('soc_code', ''),
                            "score": 0.85,  # Give it a high score since OpenAI suggested it
                            "confidence": "High",
                            "explanation": {
                                "method": "openai_suggestion",
                                "why_points": [f"OpenAI suggested this based on your profile - it might be a great fit!"]
                            },
                            "outlook": career.get('outlook_features', {}),
                            "education": career.get('education_data', {}),
                            "openai_suggested": True
                        })
                        break
            
            return suggested_careers
            
        except Exception as e:
            print(f"OpenAI career suggestion failed: {e}")
            return []
    
    def generate_career_recommendations(
        self,
        user_profile: Dict[str, Any],
        all_careers: List[Dict[str, Any]],
        min_recommendations: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate career recommendations using OpenAI when ML matches are not good enough.
        This is used as a fallback when ML model scores are too low.
        """
        if not self.is_available():
            return []
        
        try:
            user_skills = user_profile.get('skills', [])
            user_interests = user_profile.get('interests', {})
            user_values = user_profile.get('values', {})
            constraints = user_profile.get('constraints', {})
            
            skills_text = ", ".join(user_skills[:10]) if user_skills else "various skills"
            interests_text = ", ".join([f"{k} ({v:.1f})" for k, v in list(user_interests.items())[:6]]) if user_interests else "Not specified"
            values_text = ", ".join([f"{k} ({v:.1f})" for k, v in list(user_values.items())[:6]]) if user_values else "Not specified"
            
            # Get list of all career names (limited to avoid token limits)
            all_career_names = [c.get('name', '') for c in all_careers[:100]]  # Limit to 100 for token efficiency
            careers_text = ", ".join(all_career_names[:50])  # Show first 50
            
            constraints_text = ""
            if constraints:
                constraint_parts = []
                if constraints.get('min_wage'):
                    constraint_parts.append(f"Minimum wage: ${constraints.get('min_wage'):,.0f}/year")
                if constraints.get('remote_preferred'):
                    constraint_parts.append("Remote work preferred")
                if constraints.get('max_education_level') is not None:
                    edu_levels = ["No formal education", "High school", "Some college", "Bachelor's degree", "Master's degree", "Doctorate"]
                    constraint_parts.append(f"Max education: {edu_levels[min(constraints.get('max_education_level', 5), 5)]}")
                constraints_text = ", ".join(constraint_parts) if constraint_parts else "None"
            else:
                constraints_text = "None"
            
            prompt = f"""You're a career advisor helping someone find the best career matches based on their profile.

User Profile:
- Skills: {skills_text}
- Interests (RIASEC): {interests_text}
- Work Values: {values_text}
- Constraints: {constraints_text}

Available Careers (sample from database):
{careers_text}

Based on the user's profile, recommend exactly {min_recommendations} careers that would be a GREAT fit. Consider:
1. Skills alignment - careers that use their skills
2. Interest match - careers that match their RIASEC interests
3. Values alignment - careers that align with their work values
4. Constraints - respect their constraints (wage, remote, education level)
5. Realistic opportunities - careers that are actually attainable

Respond with ONLY career names, one per line, exactly {min_recommendations} careers.
Be specific with career titles - use the exact names from the list above when possible.
If a career name is close but not exact, use the closest match from the list."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 200)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career matching expert. Recommend careers that genuinely fit the user profile based on skills, interests, values, and constraints."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.6
                )
            )
            
            if response is None:
                return []
            
            result = response.choices[0].message.content.strip()
            
            if not result:
                return []
            
            # Parse suggested career names
            suggested_careers = []
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            for line in lines[:min_recommendations]:
                # Remove numbering if present (e.g., "1. Career Name" -> "Career Name")
                career_name = line.lstrip('0123456789.-) ').strip()
                
                # Try to find matching career in our database
                best_match = None
                best_match_score = 0
                
                for career in all_careers:
                    career_name_db = career.get('name', '')
                    # Fuzzy match - check if suggested name is similar to career name
                    if career_name.lower() == career_name_db.lower():
                        best_match = career
                        best_match_score = 1.0
                        break
                    elif career_name.lower() in career_name_db.lower() or career_name_db.lower() in career_name.lower():
                        # Partial match - calculate similarity
                        similarity = len(set(career_name.lower().split()) & set(career_name_db.lower().split())) / max(len(career_name.split()), len(career_name_db.split()))
                        if similarity > best_match_score:
                            best_match = career
                            best_match_score = similarity
                
                if best_match and best_match_score > 0.3:  # Only add if we have a reasonable match
                    # Create a recommendation entry for this career
                    suggested_careers.append({
                        "career_id": best_match.get('career_id', ''),
                        "name": best_match.get('name', ''),
                        "soc_code": best_match.get('soc_code', ''),
                        "score": 0.75,  # Give it a good score since OpenAI suggested it
                        "confidence": "High",
                        "explanation": {
                            "method": "openai_generated",
                            "confidence": "High",
                            "why_points": [f"OpenAI recommended this career based on your skills, interests, and values - it appears to be a strong match for your profile!"]
                        },
                        "outlook": best_match.get('outlook_features', {}),
                        "education": best_match.get('education_data', {}),
                        "openai_generated": True
                    })
            
            return suggested_careers
            
        except Exception as e:
            print(f"OpenAI career recommendation generation failed: {e}")
            return []
    
    def search_careers(
        self,
        search_query: str,
        all_careers: List[Dict[str, Any]],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Use OpenAI to search for careers based on a detailed search query.
        This helps users find careers even if they don't know the exact name.
        Can handle descriptions, skills, industries, job functions, etc.
        """
        if not self.is_available() or not search_query.strip():
            return []
        
        try:
            # Get list of all career names and descriptions (limited to avoid token limits)
            career_list = []
            for career in all_careers[:200]:  # Limit to 200 for token efficiency
                career_info = {
                    "name": career.get('name', ''),
                    "soc_code": career.get('soc_code', ''),
                    "career_id": career.get('career_id', '')
                }
                # Add description if available
                if 'description' in career:
                    career_info["description"] = career.get('description', '')[:200]  # Limit description length
                career_list.append(career_info)
            
            # Create a formatted list for the prompt
            careers_text = "\n".join([
                f"- {c['name']} (SOC: {c['soc_code']}, ID: {c['career_id']})"
                + (f" - {c.get('description', '')[:150]}" if c.get('description') else "")
                for c in career_list[:100]  # Show first 100 in prompt
            ])
            
            prompt = f"""You're helping someone find a career. They've entered: "{search_query}"

IMPORTANT: Prioritize EXACT or VERY CLOSE name matches. Only suggest alternatives if no close match exists.

Available Careers (sample from database):
{careers_text}

Find careers that match. Priority order:
1. EXACT name match (case-insensitive)
2. Very close name match (contains the search term or vice versa, e.g., "software engineer" matches "Software Engineers")
3. Partial match where the search term words appear in the career name
4. Only if none of the above, consider related careers

Return up to {max_results} careers. For each match, provide:
- The exact career name from the list above
- A brief explanation of why it matches (1 sentence)

Format your response as:
CAREER_NAME|EXPLANATION
(one per line)

If no good matches, respond with "NO_MATCHES"."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 500)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career search assistant. Help users find careers by matching their search query to available careers. Be thorough and consider various interpretations of the query."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.5
                )
            )
            
            if response is None:
                return []
            
            result = response.choices[0].message.content.strip()
            
            if "NO_MATCHES" in result.upper() or not result:
                return []
            
            # Parse the response
            matched_careers = []
            lines = [line.strip() for line in result.split('\n') if line.strip() and '|' in line]
            
            for line in lines[:max_results]:
                try:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        career_name = parts[0].strip()
                        explanation = parts[1].strip()
                        
                        # Find the career in our database
                        best_match = None
                        best_match_score = 0
                        
                        for career in all_careers:
                            career_name_db = career.get('name', '')
                            # Try exact match first
                            if career_name.lower() == career_name_db.lower():
                                best_match = career
                                best_match_score = 1.0
                                break
                            # Try partial match
                            elif career_name.lower() in career_name_db.lower() or career_name_db.lower() in career_name.lower():
                                similarity = len(set(career_name.lower().split()) & set(career_name_db.lower().split())) / max(len(career_name.split()), len(career_name_db.split()))
                                if similarity > best_match_score:
                                    best_match = career
                                    best_match_score = similarity
                        
                        if best_match and best_match_score > 0.2:  # Only add if we have a reasonable match
                            matched_careers.append({
                                "career_id": best_match.get('career_id', ''),
                                "name": best_match.get('name', ''),
                                "soc_code": best_match.get('soc_code', ''),
                                "match_explanation": explanation,
                                "match_score": best_match_score
                            })
                except Exception as e:
                    print(f"Error parsing career search result line: {e}")
                    continue
            
            # Sort by match score
            matched_careers.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            return matched_careers[:max_results]
            
        except Exception as e:
            print(f"OpenAI career search failed: {e}")
            return []
    
    def generate_career_summary(self, career_name: str, career_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a friendly summary of a career using OpenAI
        Makes it more engaging than just data
        """
        if not self.is_available():
            return None
        
        try:
            outlook = career_data.get('outlook', {})
            wage = outlook.get('median_wage_2024', 0)
            growth = outlook.get('percent_change', 0)
            
            prompt = f"""Create a brief, friendly 2-sentence summary of this career:

Career: {career_name}
Median Wage: ${wage:,.0f}/year
Growth: {growth:+.1f}%

Make it casual and encouraging."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 100)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a friendly career advisor."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.7
                )
            )
            
            if response is None:
                return None
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI summary generation failed: {e}")
            return None
    
    def validate_career_name(
        self,
        career_input: str,
        all_careers: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate and normalize a career name/description using OpenAI.
        Returns the best matching career from the database, or None if no good match.
        
        Args:
            career_input: User's input (can be job title, description, etc.)
            all_careers: List of all available careers from database
            
        Returns:
            Dictionary with career_id, name, soc_code, and match_explanation, or None
        """
        if not self.is_available() or not career_input.strip():
            return None
        
        try:
            # Get list of all career names (limited to avoid token limits)
            career_list = []
            for career in all_careers[:200]:  # Limit to 200 for token efficiency
                career_info = {
                    "name": career.get('name', ''),
                    "soc_code": career.get('soc_code', ''),
                    "career_id": career.get('career_id', '')
                }
                # Add description if available
                if 'description' in career:
                    career_info["description"] = career.get('description', '')[:200]
                career_list.append(career_info)
            
            # Create a formatted list for the prompt
            careers_text = "\n".join([
                f"- {c['name']} (SOC: {c['soc_code']}, ID: {c['career_id']})"
                + (f" - {c.get('description', '')[:150]}" if c.get('description') else "")
                for c in career_list[:100]  # Show first 100 in prompt
            ])
            
            prompt = f"""You're helping someone find a career. They've entered: "{career_input}"

IMPORTANT: Find the BEST SINGLE match. Priority order:
1. EXACT name match (case-insensitive)
2. Very close name match (contains the search term or vice versa, e.g., "software engineer" matches "Software Engineers")
3. Partial match where the search term words appear in the career name
4. Only if none of the above, consider the most related career

Available Careers (sample from database):
{careers_text}

Find the single best matching career. Return ONLY the exact career name from the list above.

Format your response as:
CAREER_NAME|BRIEF_EXPLANATION

If no good match exists, respond with "NO_MATCH"."""

            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 200)
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career search assistant. Find the single best matching career from the provided list. Be precise and match the exact career name."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.3  # Lower temperature for more precise matching
                )
            )
            
            if response is None:
                return None
            
            result = response.choices[0].message.content.strip()
            
            if "NO_MATCH" in result.upper() or not result:
                return None
            
            # Parse the response
            if '|' in result:
                parts = result.split('|', 1)
                career_name = parts[0].strip()
                explanation = parts[1].strip() if len(parts) > 1 else "Matched career"
            else:
                career_name = result.strip()
                explanation = "Matched career"
            
            # Find the career in our database
            best_match = None
            best_match_score = 0
            
            for career in all_careers:
                career_name_db = career.get('name', '')
                # Try exact match first
                if career_name.lower() == career_name_db.lower():
                    best_match = career
                    best_match_score = 1.0
                    break
                # Try partial match
                elif career_name.lower() in career_name_db.lower() or career_name_db.lower() in career_name.lower():
                    similarity = len(set(career_name.lower().split()) & set(career_name_db.lower().split())) / max(len(career_name.split()), len(career_name_db.split()))
                    if similarity > best_match_score:
                        best_match = career
                        best_match_score = similarity
            
            if best_match and best_match_score > 0.2:  # Only return if we have a reasonable match
                return {
                    "career_id": best_match.get('career_id', ''),
                    "name": best_match.get('name', ''),
                    "soc_code": best_match.get('soc_code', ''),
                    "match_explanation": explanation,
                    "match_score": best_match_score
                }
            
            return None
            
        except Exception as e:
            print(f"OpenAI career validation failed: {e}")
            return None
    
    def get_career_certifications(
        self,
        career_name: str,
        career_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get certifications that matter for a career using OpenAI
        Returns 3 certifications categorized as:
        - Entry-level certs (✅)
        - Career-advancing certs (🚀)
        - Optional/overhyped certs (⚠️)
        """
        if not self.is_available():
            return {
                "entry_level": [],
                "career_advancing": [],
                "optional_overhyped": [],
                "available": False
            }
        
        try:
            # Build context about the career
            context_parts = [f"Career: {career_name}"]
            
            if career_data:
                # Add relevant career information
                education = career_data.get('education_data', {})
                if education.get('education_level'):
                    context_parts.append(f"Typical Education: {education.get('education_level')}")
                
                outlook = career_data.get('outlook_features', {})
                if outlook.get('growth_rate'):
                    context_parts.append(f"Growth Rate: {outlook.get('growth_rate'):.1f}%")
            
            context = "\n".join(context_parts)
            
            prompt = f"""You're a career certification expert. For this career, recommend exactly 3 certifications that matter:

{context}

Provide exactly 3 certifications in this exact JSON format:
{{
  "entry_level": [
    {{
      "name": "Certification Name",
      "description": "Brief description of why this matters for entry-level",
      "provider": "Issuing organization"
    }}
  ],
  "career_advancing": [
    {{
      "name": "Certification Name",
      "description": "Brief description of how this advances career",
      "provider": "Issuing organization"
    }}
  ],
  "optional_overhyped": [
    {{
      "name": "Certification Name",
      "description": "Brief description of the certification",
      "rationale": "Brief explanation of why this is optional/overhyped - be specific about the tradeoffs",
      "provider": "Issuing organization"
    }}
  ]
}}

Guidelines:
- Entry-level: Certifications that help you get your first job in this field
- Career-advancing: Certifications that help you move up or specialize (mid-to-senior level)
- Optional/overhyped: Certifications that are nice-to-have but not essential, or are overhyped in the industry. The rationale should clearly explain why it's optional/overhyped with specific tradeoffs.

Be specific with certification names and providers. Return ONLY valid JSON, no other text."""

            # Get the correct max tokens parameter based on model
            max_tokens_param = self.get_max_tokens_param(settings.OPENAI_MODEL, 500)
            
            # Try with json_object format first, fallback to regular if not supported
            response = self._call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career certification expert. Provide accurate, specific certification recommendations in JSON format only."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
            )
            
            if response is None:
                # Try fallback without json_object format
                response = self._call_with_retry(
                    lambda: self.client.chat.completions.create(
                        model=settings.OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": "You're a career certification expert. Provide accurate, specific certification recommendations in JSON format only. Return ONLY valid JSON, no markdown, no code blocks."},
                            {"role": "user", "content": prompt}
                        ],
                        **max_tokens_param,
                        temperature=0.5
                    )
                )
            
            if response is None:
                raise Exception("OpenAI API call failed after retries")
            
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
                certifications = {
                    "entry_level": result.get("entry_level", []),
                    "career_advancing": result.get("career_advancing", []),
                    "optional_overhyped": result.get("optional_overhyped", []),
                    "available": True
                }
                
                # Validate we have exactly 1 in each category (arrays should contain 1 item each)
                if len(certifications["entry_level"]) != 1:
                    certifications["entry_level"] = certifications["entry_level"][:1] if certifications["entry_level"] else []
                if len(certifications["career_advancing"]) != 1:
                    certifications["career_advancing"] = certifications["career_advancing"][:1] if certifications["career_advancing"] else []
                if len(certifications["optional_overhyped"]) != 1:
                    certifications["optional_overhyped"] = certifications["optional_overhyped"][:1] if certifications["optional_overhyped"] else []
                
                return certifications
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse certifications JSON: {e}")
                print(f"Response was: {result_text}")
                return {
                    "entry_level": [],
                    "career_advancing": [],
                    "optional_overhyped": [],
                    "available": False,
                    "error": "Failed to parse response"
                }
            
        except Exception as e:
            print(f"OpenAI certifications generation failed: {e}")
            return {
                "entry_level": [],
                "career_advancing": [],
                "optional_overhyped": [],
                "available": False,
                "error": str(e)
            }

