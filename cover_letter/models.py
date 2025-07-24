"""
Data models for cover letter generation system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class RoleType(Enum):
    """Available role types for cover letter generation."""

    CORPORATE_RECRUITER = "corporate_recruiter"
    STORYTELLING_COACH = "storytelling_coach"
    ATS_SPECIALIST = "ats_specialist"
    HIRING_MANAGER_PEER = "hiring_manager_peer"
    INDUSTRY_SME = "industry_sme"
    GROWTH_MINDSET_COACH = "growth_mindset_coach"
    PERSUASIVE_COPYWRITER = "persuasive_copywriter"


class CompanySize(Enum):
    """Company size categories."""

    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class CompanyCulture(Enum):
    """Company culture types."""

    FORMAL = "formal"
    CASUAL = "casual"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    MISSION_DRIVEN = "mission_driven"


@dataclass
class Requirements:
    """Job requirements extracted from description."""

    hard_skills: List[str]
    soft_skills: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    certifications: List[str]


@dataclass
class JobAnalysis:
    """Complete job analysis result."""

    keywords: List[str]
    company_name: Optional[str]
    company_size: Optional[CompanySize]
    company_culture: Optional[CompanyCulture]
    industry: Optional[str]
    requirements: Requirements
    seniority_level: Optional[str]
    is_technical_role: bool
    is_creative_role: bool


@dataclass
class ValidationResult:
    """Result of cover letter validation."""

    is_valid: bool
    score: float  # 0.0 to 1.0
    length_ok: bool
    structure_ok: bool
    has_metrics: bool
    keyword_match: float
    personalization_score: float
    issues: List[str]
    suggestions: List[str]


@dataclass
class CoverLetterResult:
    """Final result of cover letter generation."""

    cover_letter: str
    quality_score: float
    validation_result: ValidationResult
    job_analysis: JobAnalysis
    role_used: RoleType
    generation_time: float
    metadata: Dict[str, Any]
