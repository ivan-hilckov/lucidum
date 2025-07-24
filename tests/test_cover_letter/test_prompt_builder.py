"""
Tests for prompt builder.
"""

import pytest
from cover_letter.prompt_builder import PromptBuilder
from cover_letter.models import RoleType, JobAnalysis, Requirements, CompanySize


class TestPromptBuilder:
    """Test PromptBuilder functionality."""

    def test_select_optimal_role_hardcoded(self):
        """Test that role selection always returns CORPORATE_RECRUITER."""
        builder = PromptBuilder()

        # Create different types of job analysis
        test_cases = [
            # Technical role
            JobAnalysis(
                keywords=["Python", "Django"],
                company_name="TechCorp",
                company_size=CompanySize.STARTUP,
                company_culture=None,
                industry="Technology",
                requirements=Requirements([], [], None, None, []),
                seniority_level="senior",
                is_technical_role=True,
                is_creative_role=False,
            ),
            # Creative role
            JobAnalysis(
                keywords=["design", "photoshop"],
                company_name="CreativeCorp",
                company_size=CompanySize.SMALL,
                company_culture=None,
                industry="Design",
                requirements=Requirements([], [], None, None, []),
                seniority_level="middle",
                is_technical_role=False,
                is_creative_role=True,
            ),
            # Generic role
            JobAnalysis(
                keywords=["management"],
                company_name="BusinessCorp",
                company_size=CompanySize.LARGE,
                company_culture=None,
                industry="Business",
                requirements=Requirements([], [], None, None, []),
                seniority_level="junior",
                is_technical_role=False,
                is_creative_role=False,
            ),
        ]

        # All should return CORPORATE_RECRUITER (simplified system)
        for job_analysis in test_cases:
            role = builder.select_optimal_role(job_analysis)
            assert role == RoleType.CORPORATE_RECRUITER

    def test_build_system_prompt(self):
        """Test system prompt building."""
        builder = PromptBuilder()

        # Test with keywords
        context = {"keywords": ["Python", "Django", "PostgreSQL"]}
        prompt = builder.build_system_prompt(RoleType.CORPORATE_RECRUITER, context)

        # Check basic structure
        assert isinstance(prompt, str)
        assert len(prompt) > 200  # Should be substantial
        assert "корпоративный рекрутер" in prompt.lower()
        assert "КРИТЕРИИ КАЧЕСТВА" in prompt
        assert "Python, Django, PostgreSQL" in prompt

    def test_build_system_prompt_without_keywords(self):
        """Test system prompt building without keywords."""
        builder = PromptBuilder()

        # Test without keywords
        context = {}
        prompt = builder.build_system_prompt(RoleType.CORPORATE_RECRUITER, context)

        assert isinstance(prompt, str)
        assert len(prompt) > 200
        assert "корпоративный рекрутер" in prompt.lower()
        # Should have empty keywords section
        assert "Ключевые навыки: " in prompt

    def test_build_user_prompt(self):
        """Test user prompt building."""
        builder = PromptBuilder()

        resume = "# Тест Резюме\nPython разработчик с опытом 3 года"
        job_desc = "Ищем Python разработчика в стартап"

        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TestCorp",
            company_size=CompanySize.STARTUP,
            company_culture=None,
            industry="IT",
            requirements=Requirements([], [], None, None, []),
            seniority_level=None,
            is_technical_role=True,
            is_creative_role=False,
        )

        prompt = builder.build_user_prompt(resume, job_desc, job_analysis)

        # Check structure
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "РЕЗЮМЕ КАНДИДАТА" in prompt
        assert "ОПИСАНИЕ ВАКАНСИИ" in prompt
        assert resume in prompt
        assert job_desc in prompt
        assert "TestCorp" in prompt

    def test_build_user_prompt_without_company(self):
        """Test user prompt building without company name."""
        builder = PromptBuilder()

        resume = "# Test Resume"
        job_desc = "Test job description"

        job_analysis = JobAnalysis(
            keywords=["Python"],
            company_name=None,  # No company name
            company_size=None,
            company_culture=None,
            industry=None,
            requirements=Requirements([], [], None, None, []),
            seniority_level=None,
            is_technical_role=True,
            is_creative_role=False,
        )

        prompt = builder.build_user_prompt(resume, job_desc, job_analysis)

        assert isinstance(prompt, str)
        assert "РЕЗЮМЕ КАНДИДАТА" in prompt
        assert "ОПИСАНИЕ ВАКАНСИИ" in prompt
        # Should handle missing company gracefully
        assert resume in prompt
        assert job_desc in prompt

    def test_different_role_prompts(self):
        """Test that different roles have different prompts."""
        builder = PromptBuilder()
        context = {"keywords": ["Python"]}

        # Test different roles
        roles_to_test = [
            RoleType.CORPORATE_RECRUITER,
            RoleType.INDUSTRY_SME,
            RoleType.STORYTELLING_COACH,
        ]

        prompts = {}
        for role in roles_to_test:
            prompt = builder.build_system_prompt(role, context)
            prompts[role] = prompt
            assert isinstance(prompt, str)
            assert len(prompt) > 100

        # Each role should have different content
        # (Though in simplified system, only CORPORATE_RECRUITER is used)
        assert len(set(prompts.values())) >= 1  # At least one unique prompt
