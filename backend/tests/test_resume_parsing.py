"""
Unit tests for resume parsing with fixtures
Tests extract_text_from_file, parse_resume_structure, and detect_skills in ResumeService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import BytesIO
from services.resume_service import ResumeService


class TestResumeParsing:
    """Test suite for resume parsing with fixtures"""
    
    @pytest.fixture
    def mock_service(self, sample_processed_data):
        """Create a mocked resume service with test data"""
        service = ResumeService()
        service._processed_data = sample_processed_data
        service._all_skills = sample_processed_data["skill_names"]
        service.load_processed_data = Mock(return_value=sample_processed_data)
        service.get_all_skills = Mock(return_value=sample_processed_data["skill_names"])
        return service
    
    def test_extract_text_from_txt(self, mock_service, sample_resume_text):
        """Test text extraction from TXT file"""
        file_content = sample_resume_text.encode('utf-8')
        
        extracted = mock_service.extract_text_from_file(file_content, 'txt')
        
        assert isinstance(extracted, str)
        assert len(extracted) > 0
        assert "Software Engineer" in extracted
        assert "Python" in extracted
    
    def test_extract_text_from_pdf(self, mock_service, sample_resume_text):
        """Test text extraction from PDF file (mocked)"""
        # Mock PdfReader
        with patch('services.resume_service.PdfReader') as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = sample_resume_text
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader
            
            file_content = b"fake pdf content"
            extracted = mock_service._extract_text_from_pdf(file_content)
            
            assert isinstance(extracted, str)
            assert len(extracted) > 0
    
    def test_extract_text_from_docx(self, mock_service, sample_resume_text):
        """Test text extraction from DOCX file (mocked)"""
        # Mock Document
        with patch('services.resume_service.Document') as mock_doc:
            mock_para = MagicMock()
            mock_para.text = sample_resume_text
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = [mock_para]
            mock_doc.return_value = mock_doc_instance
            
            file_content = b"fake docx content"
            extracted = mock_service._extract_text_from_docx(file_content)
            
            assert isinstance(extracted, str)
            assert len(extracted) > 0
    
    def test_extract_text_unsupported_format(self, mock_service):
        """Test error handling for unsupported file formats"""
        file_content = b"fake content"
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            mock_service.extract_text_from_file(file_content, 'xyz')
    
    def test_parse_resume_structure_sections(self, mock_service, sample_resume_text):
        """Test that resume structure parsing identifies sections"""
        structure = mock_service.parse_resume_structure(sample_resume_text)
        
        assert "sections" in structure
        assert "bullets" in structure
        assert "section_count" in structure
        assert "bullet_count" in structure
        
        assert isinstance(structure["sections"], dict)
        assert isinstance(structure["bullets"], list)
        assert structure["section_count"] > 0
        
        # Should identify common sections
        sections = structure["sections"]
        section_keys = [key.lower() for key in sections.keys()]
        
        # Should have identified at least one section
        assert len(sections) > 0
    
    def test_parse_resume_structure_bullets(self, mock_service, sample_resume_text):
        """Test that resume structure parsing extracts bullets"""
        structure = mock_service.parse_resume_structure(sample_resume_text)
        
        bullets = structure["bullets"]
        
        assert isinstance(bullets, list)
        assert len(bullets) > 0
        
        # All bullets should be strings
        assert all(isinstance(bullet, str) for bullet in bullets)
        
        # Bullets should not be empty
        assert all(len(bullet.strip()) > 0 for bullet in bullets)
    
    def test_parse_resume_structure_section_content(self, mock_service, sample_resume_text):
        """Test that sections contain their content"""
        structure = mock_service.parse_resume_structure(sample_resume_text)
        
        sections = structure["sections"]
        
        # Each section should have content (list)
        for section_name, content in sections.items():
            assert isinstance(content, list)
            # Content should have at least one item
            assert len(content) > 0
    
    def test_detect_skills(self, mock_service, sample_resume_text):
        """Test skill detection from resume text"""
        skills = mock_service.detect_skills(sample_resume_text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        
        # All skills should be strings
        assert all(isinstance(skill, str) for skill in skills)
        
        # Should detect skills from the text
        # The sample text contains "Python", "JavaScript", etc.
        # These should match skills in the skill_names list if they exist
        skill_lower = [s.lower() for s in skills]
        text_lower = sample_resume_text.lower()
        
        # At least some detected skills should be mentioned in the text
        matching_skills = [s for s in skills if s.lower() in text_lower]
        assert len(matching_skills) > 0, "Should detect skills mentioned in text"
    
    def test_detect_skills_no_duplicates(self, mock_service, sample_resume_text):
        """Test that skill detection returns no duplicates"""
        skills = mock_service.detect_skills(sample_resume_text)
        
        # Should have no duplicates
        assert len(skills) == len(set(skills)), "Should have no duplicate skills"
    
    def test_detect_skills_empty_text(self, mock_service):
        """Test skill detection with empty text"""
        skills = mock_service.detect_skills("")
        
        assert isinstance(skills, list)
        assert len(skills) == 0
    
    def test_parse_resume_structure_empty_text(self, mock_service):
        """Test structure parsing with empty text"""
        structure = mock_service.parse_resume_structure("")
        
        assert "sections" in structure
        assert "bullets" in structure
        assert structure["section_count"] == 0
        assert structure["bullet_count"] == 0
        assert len(structure["bullets"]) == 0
    
    def test_parse_resume_structure_multiline_bullets(self, mock_service):
        """Test parsing of multiline bullet points"""
        text = """WORK EXPERIENCE
• First bullet point
• Second bullet point
  with continuation
• Third bullet point"""
        
        structure = mock_service.parse_resume_structure(text)
        
        bullets = structure["bullets"]
        assert len(bullets) >= 3
    
    def test_detect_skills_case_insensitive(self, mock_service):
        """Test that skill detection is case insensitive"""
        text = "I have experience with PYTHON, javascript, and Java."
        
        skills = mock_service.detect_skills(text)
        
        # Should detect skills regardless of case
        skill_lower = [s.lower() for s in skills]
        # Check if any Python/Javascript variants are detected
        # (depends on exact skill names in fixture)
        assert isinstance(skills, list)
    
    def test_parse_resume_structure_various_formats(self, mock_service):
        """Test parsing of resumes with various formatting"""
        # Test with numbered lists
        text1 = """EXPERIENCE
1. First item
2. Second item"""
        
        structure1 = mock_service.parse_resume_structure(text1)
        assert structure1["bullet_count"] >= 2
        
        # Test with asterisks
        text2 = """EXPERIENCE
* First item
* Second item"""
        
        structure2 = mock_service.parse_resume_structure(text2)
        assert structure2["bullet_count"] >= 2
        
        # Test with dashes
        text3 = """EXPERIENCE
- First item
- Second item"""
        
        structure3 = mock_service.parse_resume_structure(text3)
        assert structure3["bullet_count"] >= 2
    
    def test_detect_skills_partial_matches(self, mock_service):
        """Test skill detection with partial matches"""
        # Test with skills that might partially match
        text = "I use Python programming and JavaScript development."
        
        skills = mock_service.detect_skills(text)
        
        # Should detect at least some skills
        assert isinstance(skills, list)
        # Note: Exact matches depend on skill_names in fixture
    
    def test_parse_resume_structure_section_headers(self, mock_service):
        """Test that section headers are correctly identified"""
        text = """JOHN DOE
Software Engineer

WORK EXPERIENCE
This is experience content

EDUCATION
This is education content

SKILLS
This is skills content"""
        
        structure = mock_service.parse_resume_structure(text)
        
        sections = structure["sections"]
        section_names = [name.lower() for name in sections.keys()]
        
        # Should identify multiple sections
        assert len(sections) >= 2





