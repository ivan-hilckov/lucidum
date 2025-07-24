"""
Tests for job analyzer.
"""

import pytest
from cover_letter.analyzer import JobAnalyzer
from cover_letter.models import JobAnalysis, Requirements


class TestJobAnalyzer:
    """Test JobAnalyzer functionality."""

    def test_is_technical_role(self, mock_openai_client):
        """Test technical role detection."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Technical descriptions
        tech_descriptions = [
            "Looking for Python developer with machine learning experience",
            "Senior JavaScript developer needed",
            "DevOps engineer with Kubernetes experience",
            "Data scientist position available",
            "Frontend developer with React skills",
        ]

        for desc in tech_descriptions:
            assert analyzer._is_technical_role(desc), f"Should detect '{desc}' as technical"

        # Non-technical descriptions
        non_tech_descriptions = [
            "Marketing manager with communication skills",
            "Sales representative needed",
            "HR specialist position",
            "Project manager for business development",
            "Customer service representative",
        ]

        for desc in non_tech_descriptions:
            assert not analyzer._is_technical_role(desc), f"Should not detect '{desc}' as technical"

    def test_is_creative_role(self, mock_openai_client):
        """Test creative role detection."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Creative descriptions
        creative_descriptions = [
            "Graphic designer with Photoshop skills",
            "UX/UI designer needed",
            "Content writer for marketing",
            "Video editor position",
            "Creative director role",
        ]

        for desc in creative_descriptions:
            assert analyzer._is_creative_role(desc), f"Should detect '{desc}' as creative"

        # Non-creative descriptions
        non_creative_descriptions = [
            "Python developer needed",
            "Financial analyst position",
            "Operations manager role",
            "Sales representative",
        ]

        for desc in non_creative_descriptions:
            assert not analyzer._is_creative_role(desc), f"Should not detect '{desc}' as creative"

    def test_extract_company_name(self, mock_openai_client):
        """Test company name extraction."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Test with company pattern
        job_with_company = "Компания: ТехКорп\nИщем Python разработчика"
        company = analyzer._extract_company_name(job_with_company)
        assert company == "ТехКорп"

        # Test with legal entity
        job_with_legal = "ООО Стартап Инк\nПозиция разработчика"
        company = analyzer._extract_company_name(job_with_legal)
        assert company == "ООО Стартап Инк"

        # Test without company
        job_without_company = "Ищем разработчика Python"
        company = analyzer._extract_company_name(job_without_company)
        assert company is None

    def test_extract_keywords_regex_fallback(self, mock_openai_client):
        """Test regex keyword extraction fallback."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Test with technical terms
        text = "We need Python developer with Django and PostgreSQL knowledge"

        keywords = analyzer._extract_keywords_regex(text)
        assert isinstance(keywords, list)
        assert "python" in keywords
        assert "postgresql" in keywords

    @pytest.mark.asyncio
    async def test_analyze_job_structure(self, mock_openai_client, simple_job_description):
        """Test that analyze_job returns proper structure."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Mock keyword extraction response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Python, Django, PostgreSQL"

        result = await analyzer.analyze_job(simple_job_description)

        # Check structure
        assert isinstance(result, JobAnalysis)
        assert isinstance(result.keywords, list)
        assert isinstance(result.is_technical_role, bool)
        assert isinstance(result.is_creative_role, bool)
        assert isinstance(result.requirements, Requirements)

    @pytest.mark.asyncio
    async def test_extract_keywords_simple(self, mock_openai_client):
        """Test simple keyword extraction."""
        analyzer = JobAnalyzer(mock_openai_client)

        # Mock successful response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Python, Django, PostgreSQL, React"

        result = await analyzer._extract_keywords_simple("test job description")

        assert isinstance(result, list)
        assert len(result) > 0
