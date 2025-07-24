"""
Basic tests for cover letter generation system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from cover_letter.models import (
    RoleType,
    CompanySize,
    CompanyCulture,
    Requirements,
    JobAnalysis,
    ValidationResult,
    CoverLetterResult,
)
from cover_letter.analyzer import JobAnalyzer
from cover_letter.prompt_builder import PromptBuilder
from cover_letter.validator import CoverLetterValidator
from cover_letter.generator import CoverLetterGenerator


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_resume():
    """Sample resume for testing."""
    return """
# Иван Иванов

**Senior Python Developer**

## Опыт работы

**ТехКорп**, Москва
_Senior Python Developer_
_2020 — настоящее время_

- Разработал 5 микросервисов с использованием Django и FastAPI
- Увеличил производительность системы на 40% через оптимизацию запросов
- Руководил командой из 3 разработчиков

## Навыки

- **Технические:** Python, Django, FastAPI, PostgreSQL, Docker
- **Языки:** Русский (родной), Английский (B2)
"""


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
Ищем Senior Python Developer в стартап TechStart.

Требования:
- 3+ года опыта с Python
- Знание Django/FastAPI
- Опыт работы с базами данных
- Английский язык B2+

Мы предлагаем:
- Работу в дружной команде
- Гибкий график
- Конкурентную зарплату

Присылайте резюме и сопроводительное письмо.
"""


class TestJobAnalyzer:
    """Test JobAnalyzer functionality."""

    def test_is_technical_role(self, mock_openai_client):
        """Test technical role detection."""
        analyzer = JobAnalyzer(mock_openai_client)

        tech_description = "Looking for Python developer with Django experience"
        non_tech_description = "Looking for marketing manager with communication skills"

        assert analyzer._is_technical_role(tech_description) == True
        assert analyzer._is_technical_role(non_tech_description) == False

    def test_is_creative_role(self, mock_openai_client):
        """Test creative role detection."""
        analyzer = JobAnalyzer(mock_openai_client)

        creative_description = "Looking for UI/UX designer for creative projects"
        non_creative_description = "Looking for Python developer"

        assert analyzer._is_creative_role(creative_description) == True
        assert analyzer._is_creative_role(non_creative_description) == False

    def test_determine_seniority(self, mock_openai_client):
        """Test seniority level detection."""
        analyzer = JobAnalyzer(mock_openai_client)

        senior_description = "Senior Python Developer position"
        junior_description = "Junior Developer entry level position"
        middle_description = "Middle Developer with 2-3 years experience"

        assert analyzer._determine_seniority(senior_description) == "senior"
        assert analyzer._determine_seniority(junior_description) == "junior"
        assert analyzer._determine_seniority(middle_description) == "middle"


class TestPromptBuilder:
    """Test PromptBuilder functionality."""

    def test_select_optimal_role_technical(self):
        """Test role selection for technical positions."""
        builder = PromptBuilder()

        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TechCorp",
            company_size=CompanySize.MEDIUM,
            company_culture=CompanyCulture.TECHNICAL,
            industry="Technology",
            requirements=Requirements([], [], None, None, []),
            seniority_level="senior",
            is_technical_role=True,
            is_creative_role=False,
        )

        role = builder.select_optimal_role(job_analysis)
        assert role == RoleType.INDUSTRY_SME

    def test_select_optimal_role_junior(self):
        """Test role selection for junior positions."""
        builder = PromptBuilder()

        job_analysis = JobAnalysis(
            keywords=[],
            company_name=None,
            company_size=None,
            company_culture=None,
            industry=None,
            requirements=Requirements([], [], None, None, []),
            seniority_level="junior",
            is_technical_role=False,
            is_creative_role=False,
        )

        role = builder.select_optimal_role(job_analysis)
        assert role == RoleType.GROWTH_MINDSET_COACH

    def test_build_system_prompt(self):
        """Test system prompt building."""
        builder = PromptBuilder()

        context = {"keywords": ["Python", "Django"]}
        prompt = builder.build_system_prompt(RoleType.CORPORATE_RECRUITER, context)

        assert "корпоративный рекрутер" in prompt
        assert "КРИТЕРИИ КАЧЕСТВА" in prompt
        assert "Python, Django" in prompt


class TestCoverLetterValidator:
    """Test CoverLetterValidator functionality."""

    def test_check_length(self, mock_openai_client):
        """Test length validation."""
        validator = CoverLetterValidator(mock_openai_client)

        short_text = "Короткий текст"
        good_text = " ".join(["Слово"] * 300)  # ~300 words
        long_text = " ".join(["Слово"] * 500)  # ~500 words

        assert validator._check_length(short_text) == False
        assert validator._check_length(good_text) == True
        assert validator._check_length(long_text) == False

    def test_check_structure(self, mock_openai_client):
        """Test structure validation."""
        validator = CoverLetterValidator(mock_openai_client)

        bad_structure = "Один абзац без разделения"
        good_structure = "Первый абзац\n\nВторой абзац\n\nТретий абзац"

        assert validator._check_structure(bad_structure) == False
        assert validator._check_structure(good_structure) == True

    def test_check_metrics(self, mock_openai_client):
        """Test metrics detection."""
        validator = CoverLetterValidator(mock_openai_client)

        no_metrics = "Работал разработчиком без конкретных цифр"
        with_metrics = "Увеличил производительность на 40% за 2 года"

        assert validator._check_metrics(no_metrics) == False
        assert validator._check_metrics(with_metrics) == True

    def test_check_keywords(self, mock_openai_client):
        """Test keyword matching."""
        validator = CoverLetterValidator(mock_openai_client)

        text = "Я использую Python и Django для разработки"
        keywords = ["Python", "Django", "React"]

        match_ratio = validator._check_keywords(text, keywords)
        assert match_ratio == 2 / 3  # 2 out of 3 keywords found


class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_end_to_end_generation(
        self, mock_openai_client, sample_resume, sample_job_description
    ):
        """Test complete cover letter generation pipeline."""
        # Mock responses
        mock_openai_client.chat.completions.create.return_value = Mock()
        mock_openai_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Python, Django, PostgreSQL"))
        ]

        # Mock different responses for different calls
        responses = [
            Mock(message=Mock(content="Python, Django, PostgreSQL")),  # Keywords
            Mock(
                message=Mock(
                    content='{"name": "TechStart", "size": "startup", "culture": "casual", "industry": "technology"}'
                )
            ),  # Company info
            Mock(
                message=Mock(
                    content='{"hard_skills": ["Python"], "soft_skills": ["teamwork"], "experience_years": 3, "education_level": null, "certifications": []}'
                )
            ),  # Requirements
            Mock(
                message=Mock(
                    content="Уважаемые коллеги!\n\nМеня заинтересовала позиция Senior Python Developer в вашей компании. Имею 3+ года опыта разработки с Python и Django. Увеличил производительность системы на 40% в предыдущей компании.\n\nМой опыт с микросервисами и командной работой поможет вашей команде достичь новых высот.\n\nБуду рад обсудить возможности сотрудничества.\n\nС уважением,\nИван Иванов"
                )
            ),  # Cover letter
        ]

        mock_openai_client.chat.completions.create.side_effect = responses

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(sample_resume, sample_job_description)

        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 100
        assert result.quality_score >= 0.0
        assert isinstance(result.validation_result, ValidationResult)


if __name__ == "__main__":
    # Run a quick smoke test
    import sys
    import os

    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

    async def smoke_test():
        """Quick smoke test without external dependencies."""
        print("🧪 Running smoke tests...")

        # Test model creation
        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TestCorp",
            company_size=CompanySize.STARTUP,
            company_culture=CompanyCulture.TECHNICAL,
            industry="Technology",
            requirements=Requirements(["Python"], ["communication"], 3, "Bachelor", []),
            seniority_level="senior",
            is_technical_role=True,
            is_creative_role=False,
        )
        print("✅ JobAnalysis model works")

        # Test prompt builder
        builder = PromptBuilder()
        role = builder.select_optimal_role(job_analysis)
        print(f"✅ Role selection works: {role}")

        # Test role definitions
        from cover_letter.roles import RoleDefinitions

        prompt = RoleDefinitions.get_role_prompt(RoleType.CORPORATE_RECRUITER)
        assert len(prompt) > 100
        print("✅ Role definitions work")

        print("🎉 All smoke tests passed!")

    asyncio.run(smoke_test())
