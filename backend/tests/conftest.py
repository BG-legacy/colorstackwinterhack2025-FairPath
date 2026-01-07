"""
Pytest configuration and fixtures for tests
"""
import pytest
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import json
from io import BytesIO


@pytest.fixture
def sample_processed_data() -> Dict[str, Any]:
    """Sample processed data structure for testing"""
    return {
        "version": "1.0.0",
        "skill_names": [
            "Writing", "Speaking", "Critical Thinking", "Active Learning",
            "Mathematics", "Science", "Complex Problem Solving", "Judgment and Decision Making",
            "Time Management", "Social Perceptiveness"
        ],
        "occupations": [
            {
                "career_id": "test_engineer_001",
                "name": "Software Engineer",
                "soc_code": "15-1132.00",
                "skill_vector": {
                    "combined": [0.8, 0.6, 0.9, 0.7, 0.8, 0.5, 0.9, 0.7, 0.6, 0.4] * 2 + [0.0, 0.0, 0.0] + [0.75, 0.0, 0.8]
                },
                "outlook_features": {
                    "growth_rate": 15.5,
                    "employment_2024": 1000000,
                    "employment_2034": 1155000,
                    "annual_openings": 100000,
                    "median_wage_2024": 120000,
                    "stability_score": 0.8
                },
                "education_data": {
                    "education_level": "bachelors"
                }
            },
            {
                "career_id": "test_writer_001",
                "name": "Technical Writer",
                "soc_code": "27-3042.00",
                "skill_vector": {
                    "combined": [0.9, 0.9, 0.8, 0.6, 0.3, 0.2, 0.5, 0.6, 0.7, 0.6] * 2 + [0.0, 0.0, 0.0] + [0.7, 0.0, 0.75]
                },
                "outlook_features": {
                    "growth_rate": 8.5,
                    "employment_2024": 50000,
                    "employment_2034": 54250,
                    "annual_openings": 5000,
                    "median_wage_2024": 75000,
                    "stability_score": 0.7
                },
                "education_data": {
                    "education_level": "bachelors"
                }
            },
            {
                "career_id": "test_manager_001",
                "name": "Project Manager",
                "soc_code": "11-9199.00",
                "skill_vector": {
                    "combined": [0.7, 0.9, 0.8, 0.6, 0.4, 0.3, 0.7, 0.9, 0.9, 0.8] * 2 + [0.0, 0.0, 0.0] + [0.8, 0.0, 0.8]
                },
                "outlook_features": {
                    "growth_rate": 10.0,
                    "employment_2024": 750000,
                    "employment_2034": 825000,
                    "annual_openings": 75000,
                    "median_wage_2024": 95000,
                    "stability_score": 0.75
                },
                "education_data": {
                    "education_level": "bachelors"
                }
            }
        ]
    }


@pytest.fixture
def sample_resume_text() -> str:
    """Sample resume text for testing"""
    return """John Doe
Software Engineer
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.

WORK EXPERIENCE
Senior Software Engineer | Tech Company Inc. | 2020 - Present
• Developed scalable web applications using Python and React
• Led a team of 5 engineers to deliver high-quality software
• Implemented CI/CD pipelines reducing deployment time by 50%
• Designed and implemented RESTful APIs

Software Engineer | Startup Corp | 2018 - 2020
• Built full-stack applications using JavaScript and Node.js
• Collaborated with cross-functional teams on agile projects
• Participated in code reviews and technical discussions

EDUCATION
Bachelor of Science in Computer Science | University | 2018

SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Java
• Frameworks: React, Node.js, Django, Flask
• Tools: Git, Docker, Kubernetes, AWS
• Databases: PostgreSQL, MongoDB
"""


@pytest.fixture
def sample_resume_pdf_bytes(sample_resume_text: str) -> bytes:
    """Sample resume as PDF bytes (simplified for testing)"""
    # In real tests, you'd use a proper PDF library
    # For testing, we'll use text format since PDF parsing is complex
    return sample_resume_text.encode('utf-8')


@pytest.fixture
def sample_resume_docx_bytes(sample_resume_text: str) -> bytes:
    """Sample resume as DOCX bytes (simplified for testing)"""
    # In real tests, you'd use python-docx to create proper DOCX
    # For testing, we'll use text format
    return sample_resume_text.encode('utf-8')


@pytest.fixture
def sample_user_skills() -> List[str]:
    """Sample user skills for testing"""
    return ["Writing", "Speaking", "Critical Thinking", "Mathematics"]


@pytest.fixture
def sample_user_interests() -> Dict[str, float]:
    """Sample user interests (RIASEC) for testing"""
    return {
        "Realistic": 5.0,
        "Investigative": 7.0,
        "Artistic": 4.0,
        "Social": 3.0,
        "Enterprising": 6.0,
        "Conventional": 4.0
    }


@pytest.fixture
def sample_work_values() -> Dict[str, float]:
    """Sample work values for testing"""
    return {
        "Achievement": 6.0,
        "Working Conditions": 5.0,
        "Recognition": 4.0,
        "Relationships": 5.0,
        "Support": 5.0,
        "Independence": 7.0
    }


@pytest.fixture
def sample_constraints() -> Dict[str, Any]:
    """Sample constraints for testing"""
    return {
        "min_wage": 80000,
        "remote_preferred": True,
        "max_education_level": 3
    }







