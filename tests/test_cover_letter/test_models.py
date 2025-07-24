"""
Tests for cover letter models.
"""

import pytest
from cover_letter.models import (
    RoleType,
    CompanySize,
    Requirements,
    JobAnalysis,
    CoverLetterResult,
    ValidationResult,
)


class TestRoleType:
    """Test RoleType enum."""

    def test_all_role_types_exist(self):
        """Test all role types are defined."""
        expected_roles = [
            "CORPORATE_RECRUITER",
            "STORYTELLING_COACH",
            "ATS_SPECIALIST",
            "HIRING_MANAGER_PEER",
            "INDUSTRY_SME",
            "GROWTH_MINDSET_COACH",
            "PERSUASIVE_COPYWRITER",
        ]

        for role_name in expected_roles:
            assert hasattr(RoleType, role_name)

    def test_role_values(self):
        """Test role enum values."""
        assert RoleType.CORPORATE_RECRUITER.value == "corporate_recruiter"
        assert RoleType.STORYTELLING_COACH.value == "storytelling_coach"


class TestRequirements:
    """Test Requirements model."""

    def test_create_requirements(self):
        """Test Requirements model creation."""
        requirements = Requirements(
            hard_skills=["Python", "Django"],
            soft_skills=["Communication", "Teamwork"],
            experience_years=3,
            education_level="Bachelor",
            certifications=["AWS"],
        )

        assert requirements.hard_skills == ["Python", "Django"]
        assert requirements.soft_skills == ["Communication", "Teamwork"]
        assert requirements.experience_years == 3
        assert requirements.education_level == "Bachelor"
        assert requirements.certifications == ["AWS"]

    def test_requirements_with_none_values(self):
        """Test Requirements with None values."""
        requirements = Requirements(
            hard_skills=[],
            soft_skills=[],
            experience_years=None,
            education_level=None,
            certifications=[],
        )

        assert requirements.hard_skills == []
        assert requirements.experience_years is None
        assert requirements.education_level is None


class TestJobAnalysis:
    """Test JobAnalysis model."""

    def test_create_job_analysis(self):
        """Test JobAnalysis model creation."""
        requirements = Requirements(
            hard_skills=["Python"],
            soft_skills=["Communication"],
            experience_years=2,
            education_level=None,
            certifications=[],
        )

        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TechCorp",
            company_size=CompanySize.STARTUP,
            company_culture=None,
            industry="IT",
            requirements=requirements,
            seniority_level="middle",
            is_technical_role=True,
            is_creative_role=False,
        )

        assert job_analysis.keywords == ["Python", "Django"]
        assert job_analysis.company_name == "TechCorp"
        assert job_analysis.company_size == CompanySize.STARTUP
        assert job_analysis.industry == "IT"
        assert job_analysis.seniority_level == "middle"
        assert job_analysis.is_technical_role is True
        assert job_analysis.is_creative_role is False
        assert job_analysis.requirements == requirements


class TestValidationResult:
    """Test ValidationResult model."""

    def test_valid_result(self):
        """Test valid ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            score=0.85,
            length_ok=True,
            structure_ok=True,
            has_metrics=True,
            keyword_match=0.8,
            personalization_score=0.9,
            issues=[],
            suggestions=[],
        )

        assert result.is_valid is True
        assert result.length_ok is True
        assert result.structure_ok is True
        assert result.has_metrics is True
        assert result.keyword_match == 0.8
        assert result.personalization_score == 0.9
        assert result.issues == []

    def test_invalid_result_with_issues(self):
        """Test invalid ValidationResult with issues."""
        result = ValidationResult(
            is_valid=False,
            score=0.4,
            length_ok=False,
            structure_ok=True,
            has_metrics=False,
            keyword_match=0.3,
            personalization_score=0.5,
            issues=["Too short", "No metrics"],
            suggestions=["Add more content", "Include specific metrics"],
        )

        assert result.is_valid is False
        assert result.length_ok is False
        assert result.has_metrics is False
        assert result.issues == ["Too short", "No metrics"]


class TestCoverLetterResult:
    """Test CoverLetterResult model."""

    def test_cover_letter_result(self):
        """Test CoverLetterResult creation."""
        validation_result = ValidationResult(
            is_valid=True,
            score=0.85,
            length_ok=True,
            structure_ok=True,
            has_metrics=True,
            keyword_match=0.8,
            personalization_score=0.9,
            issues=[],
            suggestions=[],
        )

        job_analysis = JobAnalysis(
            keywords=["Python"],
            company_name="TechCorp",
            company_size=None,
            company_culture=None,
            industry=None,
            requirements=Requirements([], [], None, None, []),
            seniority_level=None,
            is_technical_role=True,
            is_creative_role=False,
        )

        result = CoverLetterResult(
            cover_letter="Test cover letter content",
            quality_score=0.85,
            role_used=RoleType.CORPORATE_RECRUITER,
            generation_time=1.5,
            validation_result=validation_result,
            job_analysis=job_analysis,
            metadata={"test": "value"},
        )

        assert result.cover_letter == "Test cover letter content"
        assert result.quality_score == 0.85
        assert result.role_used == RoleType.CORPORATE_RECRUITER
        assert result.generation_time == 1.5
        assert result.validation_result == validation_result
        assert result.job_analysis == job_analysis
        assert result.metadata == {"test": "value"}
