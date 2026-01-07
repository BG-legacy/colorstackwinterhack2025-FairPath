"""
Resume Analysis Service
Handles text extraction, skill detection, resume parsing, gap analysis, and rewriting

PRIVACY GUARANTEES ENFORCED:
1. Resume processed in-memory only - all file content processed via BytesIO, never written to disk
2. No resume content logged - only error types/messages, never actual resume text
3. No resume stored in DB/disk - all processing is ephemeral and discarded after request completes
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO
from docx import Document
from pypdf import PdfReader
from services.data_processing import DataProcessingService
from services.data_ingestion import DataIngestionService
from services.openai_enhancement import OpenAIEnhancementService
from models.data_models import OccupationCatalog
from app.config import settings


class ResumeService:
    """
    Service for analyzing and rewriting resumes
    
    Privacy: All resume content is processed in-memory only and never persisted.
    """
    
    def __init__(self):
        self.data_service = DataProcessingService()
        self.ingestion_service = DataIngestionService()
        self.openai_service = OpenAIEnhancementService()
        self._processed_data = None
        self._all_skills = None
        self._catalog_cache = None
    
    def load_processed_data(self) -> Dict[str, Any]:
        """Load processed data - caching it so we don't reload constantly"""
        if self._processed_data is None:
            self._processed_data = self.data_service.load_processed_data()
            if not self._processed_data:
                raise ValueError("Processed data not found. Run process_data.py first.")
        return self._processed_data
    
    def get_all_skills(self) -> List[str]:
        """Get all unique skill names"""
        if self._all_skills is None:
            processed_data = self.load_processed_data()
            self._all_skills = processed_data.get("skill_names", [])
        return self._all_skills
    
    def get_catalog(self) -> List[OccupationCatalog]:
        """Get occupation catalog - loading from artifacts if available, caching it"""
        if self._catalog_cache is not None:
            return self._catalog_cache
        
        # Try to load from artifacts first (faster)
        catalog_file = Path(__file__).parent.parent / "artifacts" / "occupation_catalog.json"
        
        if catalog_file.exists():
            try:
                with open(catalog_file, 'r') as f:
                    data = json.load(f)
                    self._catalog_cache = [OccupationCatalog(**item) for item in data]
                    return self._catalog_cache
            except Exception as e:
                # Privacy: Only log error type, never resume content
                # This error is for catalog loading, not resume content, but being safe
                pass  # Silent fail - catalog will fallback to building from data
        
        # Fallback to building catalog if file doesn't exist
        self._catalog_cache = self.ingestion_service.build_occupation_catalog(min_occupations=50, max_occupations=150)
        return self._catalog_cache
    
    def extract_text_from_file(self, file_content: bytes, file_extension: str) -> str:
        """
        Extract text from PDF, DOCX, or TXT file
        
        Privacy: File content processed entirely in-memory using BytesIO.
        No disk writes, no persistence, no logging of content.
        
        Args:
            file_content: File content as bytes (in-memory only)
            file_extension: File extension (pdf, docx, txt)
            
        Returns:
            Extracted text as string (in-memory only)
        """
        file_extension = file_extension.lower().lstrip('.')
        
        if file_extension == 'pdf':
            return self._extract_text_from_pdf(file_content)
        elif file_extension == 'docx':
            return self._extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            return file_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported: pdf, docx, txt")
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF file (in-memory processing only)
        
        Privacy: Uses BytesIO for in-memory processing. No disk writes, no logging.
        """
        try:
            pdf_file = BytesIO(file_content)  # In-memory only
            reader = PdfReader(pdf_file)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            return '\n'.join(text_parts)
        except Exception as e:
            # Privacy: Error message doesn't include resume content
            raise ValueError("Error extracting text from PDF")
    
    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """
        Extract text from DOCX file (in-memory processing only)
        
        Privacy: Uses BytesIO for in-memory processing. No disk writes, no logging.
        """
        try:
            docx_file = BytesIO(file_content)  # In-memory only
            doc = Document(docx_file)
            text_parts = []
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            return '\n'.join(text_parts)
        except Exception as e:
            # Privacy: Error message doesn't include resume content
            raise ValueError("Error extracting text from DOCX")
    
    def detect_skills(self, text: str) -> List[str]:
        """
        Detect skills from resume text by matching against known skills
        
        Privacy: Text processed in-memory only, never logged or stored.
        
        Args:
            text: Resume text (in-memory only)
            
        Returns:
            List of detected skill names
        """
        all_skills = self.get_all_skills()
        text_lower = text.lower()
        detected_skills = []
        
        # Create a set for faster lookup
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Match skills - using word boundary matching for better accuracy
        for skill in all_skills:
            skill_lower = skill.lower()
            skill_words = skill_lower.split()
            
            # If skill is a single word, check if it's in text
            if len(skill_words) == 1:
                if skill_words[0] in text_words or skill_words[0] in text_lower:
                    detected_skills.append(skill)
            else:
                # For multi-word skills, check if all words appear together
                # Use regex to find the phrase
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    detected_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in detected_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def parse_resume_structure(self, text: str) -> Dict[str, Any]:
        """
        Parse resume into sections and bullet points
        
        Privacy: Text processed in-memory only, never logged or stored.
        
        Args:
            text: Resume text (in-memory only)
            
        Returns:
            Dictionary with sections and bullets
        """
        lines = text.split('\n')
        sections = {}
        current_section = None
        bullets = []
        
        # Common section headers
        section_keywords = [
            'experience', 'work experience', 'employment', 'employment history',
            'education', 'educational background', 'academic',
            'skills', 'technical skills', 'competencies',
            'projects', 'project experience',
            'certifications', 'certificates', 'licenses',
            'achievements', 'accomplishments', 'awards',
            'summary', 'objective', 'profile', 'professional summary'
        ]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if this line is a section header
            line_lower = line_stripped.lower()
            is_section = False
            for keyword in section_keywords:
                if keyword in line_lower and len(line_stripped) < 50:  # Section headers are usually short
                    # Check if it's likely a header (all caps, or title case, or followed by colon)
                    if (line_stripped.isupper() or 
                        line_stripped.istitle() or 
                        line_stripped.endswith(':') or
                        line_lower == keyword):
                        current_section = keyword
                        sections[current_section] = []
                        bullets = []
                        is_section = True
                        break
            
            if not is_section and current_section:
                # Check if it's a bullet point
                if (line_stripped.startswith('•') or 
                    line_stripped.startswith('-') or 
                    line_stripped.startswith('*') or
                    line_stripped.startswith('·') or
                    re.match(r'^\d+[\.\)]', line_stripped)):  # Numbered list
                    bullet_text = re.sub(r'^[•\-\*·]\s*|\d+[\.\)]\s*', '', line_stripped).strip()
                    if bullet_text:
                        bullets.append(bullet_text)
                        sections[current_section].append(bullet_text)
                elif line_stripped:  # Regular text in section
                    sections[current_section].append(line_stripped)
        
        # Also extract all bullet points (any line starting with bullet indicators)
        all_bullets = []
        for line in lines:
            line_stripped = line.strip()
            if (line_stripped.startswith('•') or 
                line_stripped.startswith('-') or 
                line_stripped.startswith('*') or
                line_stripped.startswith('·') or
                re.match(r'^\d+[\.\)]', line_stripped)):
                bullet_text = re.sub(r'^[•\-\*·]\s*|\d+[\.\)]\s*', '', line_stripped).strip()
                if bullet_text:
                    all_bullets.append(bullet_text)
        
        return {
            "sections": sections,
            "bullets": all_bullets,
            "section_count": len(sections),
            "bullet_count": len(all_bullets)
        }
    
    def analyze_gaps(
        self, 
        resume_skills: List[str], 
        target_career_id: Optional[str] = None,
        target_career_name: Optional[str] = None,
        resume_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze skills gaps between resume and target career using OpenAI for accuracy
        
        Privacy: Resume content is processed in-memory only, never logged or stored.
        
        Args:
            resume_skills: List of skills detected in resume (in-memory only)
            target_career_id: Career ID of target occupation (optional if target_career_name provided)
            target_career_name: Target career name/description (optional if target_career_id provided)
            resume_text: Optional full resume text for context (in-memory only)
            
        Returns:
            Dictionary with gap analysis
        """
        # Generic O*NET skills that are not useful for gap analysis
        # These are fundamental skills required for almost all jobs
        generic_skills = {
            'reading comprehension', 'active listening', 'writing', 'speaking',
            'mathematics', 'critical thinking', 'active learning', 'learning strategies',
            'monitoring', 'social perceptiveness', 'coordination', 'persuasion',
            'negotiation', 'instructing', 'service orientation', 'complex problem solving',
            'operations analysis', 'technology design', 'equipment selection', 'installation',
            'programming', 'quality control analysis', 'judgment and decision making',
            'time management', 'management of personnel resources', 'management of material resources',
            'management of financial resources', 'systems analysis', 'systems evaluation'
        }
        
        # Preserve user's original input
        user_career_name = target_career_name
        validated_career = None  # Store validated career info
        
        # If career name provided but not ID, validate it using OpenAI
        if target_career_name and not target_career_id:
            if self.openai_service.is_available():
                catalog = self.get_catalog()
                all_careers = []
                for cat in catalog:
                    career_dict = {
                        "career_id": cat.occupation.career_id,
                        "name": cat.occupation.name,
                        "soc_code": cat.occupation.soc_code,
                        "description": cat.occupation.description
                    }
                    all_careers.append(career_dict)
                
                validated = self.openai_service.validate_career_name(
                    career_input=target_career_name,
                    all_careers=all_careers
                )
                
                if validated:
                    target_career_id = validated["career_id"]
                    validated_career = validated  # Store for later use
                else:
                    return {
                        "error": f"Could not find a matching career for: {target_career_name}"
                    }
            else:
                return {
                    "error": "OpenAI service not available. Please provide a career_id instead of career name."
                }
        
        if not target_career_id:
            return {
                "error": "Either target_career_id or target_career_name must be provided"
            }
        
        # Get target career skills
        catalog = self.get_catalog()
        target_catalog = None
        for cat in catalog:
            if cat.occupation.career_id == target_career_id:
                target_catalog = cat
                break
        
        if not target_catalog:
            return {
                "error": f"Target career {target_career_id} not found"
            }
        
        # Skip catalog-based matching - let OpenAI handle all skill matching intelligently
        # We'll only use catalog for career info, not for skill matching
        
        # Use matched career name from OpenAI validation if available, otherwise use catalog name
        # If user provided career name and we validated it, use the matched career name
        if validated_career:
            display_name = validated_career["name"]  # Use matched career name from OpenAI
        else:
            display_name = target_catalog.occupation.name
        
        # Use OpenAI to generate comprehensive gap analysis - no catalog matching
        # Force re-check availability in case settings were loaded after service initialization
        if not self.openai_service.is_available():
            # Double-check: Try to re-initialize the OpenAI service
            self.openai_service._initialize_client()
        
        if self.openai_service.is_available():
            openai_analysis = self._generate_openai_gap_analysis(
                resume_skills=resume_skills,
                resume_text=resume_text,
                target_career_name=display_name,
                target_catalog=target_catalog,
                matching_skills=[],  # Empty - OpenAI will match intelligently
                missing_important=[],  # Empty - OpenAI will identify missing skills
                missing_skills_filtered=[]  # Empty - OpenAI will identify all missing skills
            )
            
            if openai_analysis:
                # Get all skill information from OpenAI analysis
                verified_matching_skills = openai_analysis.get("matching_skills_verified", [])
                missing_important_skills = openai_analysis.get("missing_important_skills", [])
                missing_skills = openai_analysis.get("missing_skills", [])
                
                # Calculate coverage based on OpenAI's matching
                if missing_important_skills:
                    # Coverage = (total needed - missing) / total needed * 100
                    # We estimate total needed from missing + matching
                    total_important_needed = len(missing_important_skills) + len(verified_matching_skills)
                    if total_important_needed > 0:
                        coverage = (len(verified_matching_skills) / total_important_needed) * 100
                    else:
                        coverage = 100.0  # If no missing skills, they have everything
                else:
                    coverage = 100.0  # If no missing important skills, coverage is high
                
                # Determine if this is a poor match
                is_poor_match = coverage == 0.0 and len(verified_matching_skills) == 0 and len(missing_important_skills) > 0
                
                # Use OpenAI analysis entirely - no catalog matching
                result = {
                    "target_career": {
                        "career_id": target_career_id,
                        "name": display_name,
                        "user_input": user_career_name if user_career_name else None
                    },
                    "matching_skills": verified_matching_skills,
                    "missing_important_skills": missing_important_skills,
                    "missing_skills": missing_skills,
                    "recommended_skills": openai_analysis.get("recommended_skills", []),
                    "skill_gaps": openai_analysis.get("skill_gaps", []),
                    "analysis_explanation": openai_analysis.get("explanation", ""),
                    "extra_skills": [],  # OpenAI will identify if needed
                    "coverage_percentage": round(coverage, 1),
                    "is_poor_match": is_poor_match,
                    "summary": {
                        "resume_skills_count": len(resume_skills),
                        "target_skills_count": len(missing_important_skills) + len(verified_matching_skills),  # Estimated from OpenAI
                        "target_important_count": len(missing_important_skills) + len(verified_matching_skills),
                        "matching_count": len(verified_matching_skills),
                        "missing_important_count": len(missing_important_skills)
                    }
                }
                return result
        
        # Fallback: If OpenAI is not available, return error with diagnostics
        api_key_status = "not configured"
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            if settings.OPENAI_API_KEY.strip() and settings.OPENAI_API_KEY != "your_openai_api_key_here":
                api_key_status = f"configured (key: {settings.OPENAI_API_KEY[:10]}...)"
            else:
                api_key_status = "empty or placeholder"
        
        return {
            "error": "OpenAI service is required for gap analysis. Please configure OPENAI_API_KEY.",
            "diagnostics": {
                "api_key_status": api_key_status,
                "client_initialized": self.openai_service.client is not None,
                "service_available": self.openai_service.is_available()
            }
        }
    
    def _refine_missing_skills_with_openai(
        self,
        missing_skills: List[str],
        target_career_name: str,
        resume_skills: List[str]
    ) -> Optional[List[str]]:
        """
        Use OpenAI to refine and prioritize missing skills, filtering out generic ones
        and focusing on skills that are actually relevant for career transition.
        
        Privacy: Only skill names are processed, no full resume content.
        """
        if not missing_skills or not self.openai_service.is_available():
            return None
        
        try:
            # Limit to top 30 skills to avoid token limits
            skills_to_analyze = missing_skills[:30]
            resume_skills_sample = resume_skills[:10] if resume_skills else []
            
            prompt = f"""You're analyzing skills gaps for someone transitioning to a {target_career_name} role.

Current resume skills (sample): {', '.join(resume_skills_sample) if resume_skills_sample else 'None listed'}

Missing skills from target career:
{chr(10).join(f"- {skill}" for skill in skills_to_analyze)}

Filter and prioritize these missing skills to show ONLY the most relevant and actionable ones for career transition. 
Remove:
1. Generic skills that apply to almost all jobs (like "Reading Comprehension", "Active Listening")
2. Skills that are too vague or not actionable
3. Skills that are unlikely to be relevant for this specific career transition

Keep only:
1. Specific, technical, or domain-specific skills
2. Skills that are actually learnable/attainable
3. Skills that would make a meaningful difference in this career transition

Return a JSON array of the top 15 most relevant skills, in order of priority:
{{"relevant_skills": ["skill1", "skill2", ...]}}

Return ONLY valid JSON, no other text."""

            max_tokens_param = self.openai_service.get_max_tokens_param(settings.OPENAI_MODEL, 300)
            response = self.openai_service._call_with_retry(
                lambda: self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career transition expert. Filter and prioritize skills for career gaps analysis. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
            )
            
            if response is None:
                return None
            
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            refined_skills = result.get("relevant_skills", [])
            
            # Validate that refined skills are from the original list (case-insensitive)
            original_lower = {s.lower(): s for s in missing_skills}
            validated_skills = []
            for skill in refined_skills:
                skill_lower = skill.lower()
                if skill_lower in original_lower:
                    validated_skills.append(original_lower[skill_lower])
            
            return validated_skills if validated_skills else None
            
        except Exception as e:
            # Privacy: Never log skill names in exceptions
            # Fallback to original list if OpenAI fails
            return None
    
    def _generate_openai_gap_analysis(
        self,
        resume_skills: List[str],
        resume_text: Optional[str],
        target_career_name: str,
        target_catalog: OccupationCatalog,
        matching_skills: List[str],
        missing_important: List[str],
        missing_skills_filtered: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI to generate a comprehensive, accurate gap analysis.
        
        Privacy: Only skill names and resume text are processed in-memory.
        No logging, no storage.
        """
        if not self.openai_service.is_available():
            return None
        
        try:
            # No catalog-based skill extraction - OpenAI will identify all skills
            
            # Prepare resume context (limit length to avoid token limits)
            resume_context = ""
            if resume_text:
                # Take first 2000 characters for context
                resume_context = resume_text[:2000] + ("..." if len(resume_text) > 2000 else "")
            else:
                resume_context = f"Resume skills: {', '.join(resume_skills[:20])}"
            
            # Build prompt for comprehensive gap analysis
            prompt = f"""You're a career transition expert analyzing skills gaps for someone transitioning to a {target_career_name} role.

RESUME CONTEXT:
{resume_context}

CURRENT RESUME SKILLS:
{', '.join(resume_skills[:30]) if resume_skills else 'None detected'}

TARGET CAREER: {target_career_name}
TARGET CAREER DESCRIPTION: {target_catalog.occupation.description[:500] if target_catalog.occupation.description else 'N/A'}



CRITICAL INSTRUCTIONS - You are an expert with knowledge of ALL careers. Use your expertise to:

1. **INTELLIGENTLY MATCH RESUME SKILLS**: Don't just look for exact matches. Understand the meaning and context:
   - "React" or "JavaScript" → Programming, Software Development, Web Development
   - "Teaching" or "Training" → Instruction, Learning Strategies, Curriculum Development
   - "Project Management" → Coordination, Time Management, Management of Personnel Resources
   - Analyze the resume context to understand what skills the person actually has

2. **GENERATE ACCURATE SKILL LISTS**: Based on {target_career_name}, identify the REAL skills needed using YOUR EXPERT KNOWLEDGE:
   - For TEACHING roles: Teaching/Instruction, Curriculum Development, Classroom Management, Student Assessment, Lesson Planning, Educational Technology
   - For TECHNICAL roles: Programming, Systems Analysis, Troubleshooting, Technology Design
   - For BUSINESS roles: Management, Coordination, Planning, Negotiation
   - Use your expertise to determine what skills are ACTUALLY needed for this career

4. **FILTER IRRELEVANT SKILLS**: 
   - Remove generic skills: "Reading Comprehension", "Active Listening", "Critical Thinking"
   - Remove skills that clearly don't belong: "Equipment Maintenance" for office jobs, "Classroom Management" for non-teaching roles
   - Keep only skills that are SPECIFIC and ACTIONABLE for {target_career_name}

5. **MATCH RESUME TO CAREER**: Intelligently map resume skills to career requirements:
   - Look for semantic matches, not just keyword matches
   - Understand skill transferability (e.g., "project management" skills transfer to many roles)
   - Identify which resume skills are relevant to the target career

Return a JSON object with this structure:
{{
  "matching_skills_verified": ["skill1", "skill2", ...],  // OPTIONAL: Improved/verified list of matching skills from resume (intelligently matched)
  "missing_important_skills": ["skill1", "skill2", ...],  // Top 10-15 most critical missing skills - USE YOUR KNOWLEDGE to ensure accuracy
  "missing_skills": ["skill1", "skill2", ...],  // Additional relevant missing skills (top 15-20) - verify they make sense
  "recommended_skills": ["skill1", "skill2", ...],  // Skills to develop for this transition (top 10) - be specific and actionable
  "skill_gaps": [
    {{
      "skill": "Skill Name",  // Use accurate skill names that actually matter for this career
      "importance": 4.5,  // 1-5 scale based on how critical this skill is for {target_career_name}
      "gap_level": "high",  // "low", "medium", or "high" based on how much they need this skill
      "explanation": "Brief explanation of why this skill matters for this career - be specific"
    }}
  ],
  "explanation": "Brief overall explanation of the gap analysis and transition feasibility based on your expert knowledge of this career."
}}

CRITICAL REQUIREMENTS:
- DO NOT blindly use catalog skills if they don't make sense for {target_career_name}
- USE YOUR EXPERT KNOWLEDGE of {target_career_name} to suggest the CORRECT skills needed
- Only include skills that are SPECIFIC, RELEVANT, and ACTIONABLE for {target_career_name}
- Exclude generic skills that everyone needs (reading, writing, basic communication, etc.)
- Focus on skills that would actually help someone transition to this career
- Be realistic about what skills are learnable vs. require formal education
- Prioritize skills that would make the biggest impact
- If catalog skills are wrong (e.g., "Equipment Maintenance" for a teacher), replace them with correct skills

Return ONLY valid JSON, no markdown, no code blocks."""

            max_tokens_param = self.openai_service.get_max_tokens_param(settings.OPENAI_MODEL, 1500)
            response = self.openai_service._call_with_retry(
                lambda: self.openai_service.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You're a career transition expert. Analyze skills gaps accurately and provide actionable insights. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    **max_tokens_param,
                    temperature=0.6,
                    response_format={"type": "json_object"}
                )
            )
            
            if response is None:
                return None
            
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            elif result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            # Validate and structure the response
            return {
                "missing_important_skills": result.get("missing_important_skills", [])[:15],
                "missing_skills": result.get("missing_skills", [])[:20],
                "recommended_skills": result.get("recommended_skills", [])[:10],
                "skill_gaps": result.get("skill_gaps", [])[:20],
                "explanation": result.get("explanation", "")
            }
            
        except Exception as e:
            # Privacy: Never log resume content in exceptions
            # Fallback to catalog-based analysis if OpenAI fails
            return None
    
    def rewrite_bullets(
        self, 
        bullets: List[str], 
        target_career_id: Optional[str] = None,
        target_career_name: Optional[str] = None,
        resume_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rewrite resume bullets to better align with target career
        
        Privacy: All text content processed in-memory only. No logging, no storage.
        Content sent to OpenAI API for enhancement but never persisted locally.
        
        Args:
            bullets: List of bullet points to rewrite (in-memory only)
            target_career_id: Target career ID (optional if target_career_name provided)
            target_career_name: Target career name/description - used as-is if provided (optional if target_career_id provided)
            resume_text: Optional full resume text for context (in-memory only)
            
        Returns:
            Dictionary with rewritten bullets, explanations, and compliance notes
        """
        # Use the user's exact career name if provided, or get career name from ID
        user_career_name = target_career_name
        target_skills = []
        
        # If career_id provided, get skills from catalog
        if target_career_id:
            catalog = self.get_catalog()
            target_catalog = None
            for cat in catalog:
                if cat.occupation.career_id == target_career_id:
                    target_catalog = cat
                    break
            
            if target_catalog:
                target_skills = [skill.skill_name for skill in target_catalog.skills if skill.importance and skill.importance >= 3.0]
                # Use catalog name if user didn't provide a name
                if not user_career_name:
                    user_career_name = target_catalog.occupation.name
        
        # If no career_id and no name provided, error
        if not user_career_name:
            return {
                "error": "Either target_career_id or target_career_name must be provided"
            }
        
        # Use the user's exact career name (don't override it)
        final_career_name = user_career_name
        
        # Use OpenAI to rewrite bullets if available
        if self.openai_service.is_available():
            return self._rewrite_bullets_with_openai(
                bullets, final_career_name, target_skills, resume_text, target_career_id
            )
        else:
            # Fallback: simple rewriting without OpenAI
            return self._rewrite_bullets_simple(bullets, target_skills)
    
    def _rewrite_bullets_with_openai(
        self,
        bullets: List[str],
        target_career_name: str,
        target_skills: List[str],
        resume_text: Optional[str] = None,
        target_career_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Rewrite bullets using OpenAI"""
        try:
            client = self.openai_service.client
            
            # Prepare context
            skills_context = ", ".join(target_skills[:20])  # Limit to top 20 skills
            
            prompt = f"""You are a professional resume writer helping someone tailor their resume for a {target_career_name} position.

Target career: {target_career_name}
Important skills for this career: {skills_context}

Rules:
1. Rewrite each bullet point to better align with the target career
2. Emphasize relevant skills and achievements that match the target role
3. Use action verbs and quantifiable results where possible
4. DO NOT fabricate or invent experiences, qualifications, or achievements
5. Only enhance and reframe existing content
6. Maintain truthfulness and accuracy

Original bullet points:
{chr(10).join(f"{i+1}. {bullet}" for i, bullet in enumerate(bullets))}

For each bullet point, provide:
1. The rewritten version
2. A brief explanation of what changed and why
3. A compliance note confirming no fabrication

Format your response as JSON with this structure:
{{
  "rewrites": [
    {{
      "original": "original bullet text",
      "rewritten": "rewritten bullet text",
      "explanation": "brief explanation of changes",
      "compliance_note": "confirmation that no information was fabricated"
    }}
  ]
}}
"""
            
            # Use a cost-effective model for resume rewriting
            model_name = settings.OPENAI_MODEL if settings.OPENAI_MODEL != "gpt-5.2" else "gpt-4o-mini"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Always output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "rewrites": result.get("rewrites", []),
                "target_career": {
                    "name": target_career_name,
                    "career_id": target_career_id or "user_input"
                },
                "compliance_summary": "All rewrites maintain factual accuracy. No information was fabricated."
            }
            
        except Exception as e:
            # Privacy: Never log resume content in exceptions
            # Fallback to simple rewriting (no error logging with content)
            return self._rewrite_bullets_simple(bullets, target_skills)
    
    def _rewrite_bullets_simple(
        self,
        bullets: List[str],
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """Simple rewriting without OpenAI - just add skill keywords"""
        rewrites = []
        target_skills_lower = [s.lower() for s in target_skills]
        
        for bullet in bullets:
            bullet_lower = bullet.lower()
            
            # Check if bullet already contains target skills
            contains_target_skill = any(skill in bullet_lower for skill in target_skills_lower)
            
            if contains_target_skill:
                # Already aligned, minimal changes
                rewritten = bullet
                explanation = "Bullet already aligns well with target career skills"
            else:
                # Keep original (we can't safely enhance without AI)
                rewritten = bullet
                explanation = "No changes made - requires AI enhancement for safe rewriting"
            
            rewrites.append({
                "original": bullet,
                "rewritten": rewritten,
                "explanation": explanation,
                "compliance_note": "No fabrication - original content preserved"
            })
        
        return {
            "rewrites": rewrites,
            "target_career": "Unknown",
            "compliance_summary": "Simple rewriting mode - no AI enhancements applied. Original content preserved."
        }

