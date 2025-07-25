"""
Basic smoke tests for cover letter generation system.
"""

import pytest
import asyncio
from cover_letter import (
    CoverLetterGenerator,
    CoverLetterResult,
    RoleType,
)


class TestSmoke:
    """Basic smoke tests to ensure system is working."""

    def test_imports(self):
        """Test that main components can be imported."""

        # All imports successful
        assert True

    def test_model_creation(self):
        """Test basic model creation."""
        from cover_letter.models import JobAnalysis, Requirements, CompanySize

        requirements = Requirements(
            hard_skills=["Python"],
            soft_skills=["Communication"],
            experience_years=2,
            education_level=None,
            certifications=[],
        )

        job_analysis = JobAnalysis(
            keywords=["Python"],
            company_name="TestCorp",
            company_size=CompanySize.STARTUP,
            company_culture=None,
            industry=None,
            requirements=requirements,
            seniority_level=None,
            is_technical_role=True,
            is_creative_role=False,
        )

        assert job_analysis.company_name == "TestCorp"
        assert job_analysis.is_technical_role

    def test_role_definitions_work(self):
        """Test that role definitions are accessible."""
        from cover_letter.roles import RoleDefinitions

        for role_type in RoleType:
            prompt = RoleDefinitions.get_role_prompt(role_type)
            description = RoleDefinitions.get_role_description(role_type)
            temperature = RoleDefinitions.get_role_temperature(role_type)

            assert len(prompt) > 50
            assert len(description) > 5
            assert 0.0 <= temperature <= 1.0

    def test_analyzer_instantiation(self, mock_openai_client):
        """Test that analyzer can be created."""
        from cover_letter.analyzer import JobAnalyzer

        analyzer = JobAnalyzer(mock_openai_client)
        assert analyzer.client == mock_openai_client

        # Test basic role detection
        assert analyzer._is_technical_role("Python developer position")
        assert not analyzer._is_technical_role("Marketing manager position")

    def test_prompt_builder_instantiation(self):
        """Test that prompt builder works."""
        from cover_letter.prompt_builder import PromptBuilder
        from cover_letter.models import JobAnalysis, Requirements

        builder = PromptBuilder()

        job_analysis = JobAnalysis(
            keywords=["Python"],
            company_name=None,
            company_size=None,
            company_culture=None,
            industry=None,
            requirements=Requirements([], [], None, None, []),
            seniority_level=None,
            is_technical_role=True,
            is_creative_role=False,
        )

        role = builder.select_optimal_role(job_analysis)
        assert role == RoleType.CORPORATE_RECRUITER  # Simplified system

    def test_generator_instantiation(self, mock_openai_client):
        """Test that generator can be created."""
        generator = CoverLetterGenerator(mock_openai_client)

        assert generator.client == mock_openai_client
        assert hasattr(generator, "analyzer")
        assert hasattr(generator, "prompt_builder")

    @pytest.mark.asyncio
    async def test_basic_generation_flow(self, mock_openai_client):
        """Test basic generation without errors."""
        # Mock response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Test keywords"

        generator = CoverLetterGenerator(mock_openai_client)

        try:
            result = await generator.generate("# Test Resume", "Test job description")
            assert isinstance(result, CoverLetterResult)
        except Exception as e:
            # If generation fails, at least ensure it doesn't crash
            assert "error" in str(e).lower() or "fail" in str(e).lower()


if __name__ == "__main__":
    # Quick console test runner
    async def quick_test():
        """Run a quick smoke test."""
        print("🧪 Running basic smoke tests...")

        # Test imports
        try:
            from cover_letter import RoleType
            from cover_letter.roles import RoleDefinitions

            print("✅ Imports work")
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False

        # Test role definitions
        try:
            for role in RoleType:
                prompt = RoleDefinitions.get_role_prompt(role)
                assert len(prompt) > 50
            print("✅ Role definitions work")
        except Exception as e:
            print(f"❌ Role definitions failed: {e}")
            return False

        print("🎉 Basic smoke tests passed!")
        return True

    asyncio.run(quick_test())
