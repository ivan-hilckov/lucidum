"""
Integration tests for complete cover letter generation pipeline.
"""

import pytest
from cover_letter import CoverLetterGenerator, CoverLetterResult


class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_end_to_end_generation(
        self, mock_openai_client, mock_response_builder, sample_resume, sample_job_description
    ):
        """Test complete cover letter generation pipeline."""
        # Set up mock responses for simplified pipeline (only 2 calls)
        responses = [
            # Keywords extraction
            mock_response_builder.create_response(
                "Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes, команда, архитектура, микросервисы, CI/CD, backend, fintech"
            ),
            # Cover letter generation
            mock_response_builder.create_cover_letter_response(),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(sample_resume, sample_job_description)

        # Verify complete result structure
        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 200
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0
        assert result.generation_time > 0
        assert isinstance(result.metadata, dict)
        assert isinstance(result.keywords_found, int)

        # Verify content quality
        assert "TechStart" in result.cover_letter
        assert "Python" in result.cover_letter

    @pytest.mark.asyncio
    async def test_simple_generation(
        self, mock_openai_client, simple_resume, simple_job_description
    ):
        """Test generation with simple inputs."""
        # Mock responses for both calls
        from unittest.mock import Mock

        response1 = Mock()
        response1.choices = [Mock()]
        response1.choices[0].message = Mock()
        response1.choices[0].message.content = "Python, Django, разработчик"

        response2 = Mock()
        response2.choices = [Mock()]
        response2.choices[0].message = Mock()
        response2.choices[0].message.content = """Уважаемая команда!

Меня заинтересовала позиция Python Developer в вашей компании. С опытом коммерческой разработки на Python, я уверен, что мой профиль подходит для ваших задач.

В ТехКорп я разработал несколько сервисов на Django, увеличив производительность на 30%. Работал с PostgreSQL и Redis, что напрямую соответствует вашим требованиям.

Готов обсудить возможности сотрудничества.

С уважением"""

        mock_openai_client.chat.completions.create.side_effect = [response1, response2]

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(simple_resume, simple_job_description)

        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 50
        assert result.quality_score >= 0.0

    @pytest.mark.asyncio
    async def test_generation_with_company_name(
        self, mock_openai_client, simple_resume, simple_job_description
    ):
        """Test generation with explicit company name."""
        # Mock successful responses to avoid fallback
        from unittest.mock import Mock

        response1 = Mock()
        response1.choices = [Mock()]
        response1.choices[0].message = Mock()
        response1.choices[0].message.content = "Python, Django, стартап, разработчик"

        response2 = Mock()
        response2.choices = [Mock()]
        response2.choices[0].message = Mock()
        response2.choices[0].message.content = """Уважаемая команда CustomCorp!

Меня заинтересовала позиция в вашей компании. С опытом разработки на Python и Django, я готов присоединиться к команде и вносить значимый вклад в развитие ваших проектов.

Мой опыт работы включает разработку веб-приложений, работу с базами данных и создание эффективных решений для бизнес-задач. В текущей компании я увеличил производительность на тридцать процентов.

С уважением"""

        mock_openai_client.chat.completions.create.side_effect = [response1, response2]

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(
            simple_resume, simple_job_description, company_name="CustomCorp"
        )

        assert isinstance(result, CoverLetterResult)
        # Check that CustomCorp is mentioned in the letter
        assert "CustomCorp" in result.cover_letter

    @pytest.mark.asyncio
    async def test_fallback_on_error(
        self, mock_openai_client, simple_resume, simple_job_description
    ):
        """Test fallback generation when main generation fails."""

        # All main generation calls fail, only fallback succeeds
        def side_effect(*args, **kwargs):
            # Check if this is a fallback call (contains "короткое сопроводительное письмо")
            if len(args) > 0 and hasattr(args[0], "get"):
                # This is kwargs call
                messages = args[0].get("messages", [])
            elif "messages" in kwargs:
                messages = kwargs["messages"]
            else:
                messages = []

            # Check if this is fallback call
            is_fallback_call = any(
                "профессиональное сопроводительное письмо" in str(msg.get("content", ""))
                for msg in messages
            )

            if is_fallback_call:
                # Fallback call succeeds
                response = mock_openai_client.chat.completions.create.return_value
                response.choices[
                    0
                ].message.content = "Простое сопроводительное письмо для fallback тестирования. Это достаточно длинное письмо с более чем пятьюдесятью словами чтобы пройти проверку минимальной длины контента который генерируется системой."
                return response
            else:
                # All other calls fail
                raise Exception("API Error")

        mock_openai_client.chat.completions.create.side_effect = side_effect

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(simple_resume, simple_job_description)

        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 20
        # Should indicate fallback was used
        assert result.metadata.get("fallback_used", False)

    @pytest.mark.asyncio
    async def test_different_job_types(self, mock_openai_client):
        """Test generation with different types of job descriptions."""
        # Technical job
        tech_resume = "# Dev\nPython developer"
        tech_job = "Looking for Python developer with React experience"

        from unittest.mock import Mock

        # Mock responses for technical job - successful generation
        tech_response1 = Mock()
        tech_response1.choices = [Mock()]
        tech_response1.choices[0].message = Mock()
        tech_response1.choices[
            0
        ].message.content = "Python, React, JavaScript, developer, programming"

        tech_response2 = Mock()
        tech_response2.choices = [Mock()]
        tech_response2.choices[0].message = Mock()
        tech_response2.choices[0].message.content = """Dear Hiring Team,

I am interested in the Python developer position. With experience in Python and React development, I believe I can contribute effectively to your technical team and help deliver high-quality software solutions.

My background includes web application development, API design, and frontend frameworks integration. I have worked on multiple projects involving modern JavaScript frameworks and backend systems.

Best regards"""

        generator = CoverLetterGenerator(mock_openai_client)

        # Test technical job
        mock_openai_client.chat.completions.create.side_effect = [tech_response1, tech_response2]
        tech_result = await generator.generate(tech_resume, tech_job)
        assert isinstance(tech_result, CoverLetterResult)
        # Check that generation was successful
        assert tech_result.keywords_found > 0

    @pytest.mark.asyncio
    async def test_performance_metrics(
        self, mock_openai_client, sample_resume, sample_job_description
    ):
        """Test that generation completes in reasonable time."""
        # Fast mock response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Quick response"

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(sample_resume, sample_job_description)

        # Should complete quickly with mocked responses
        assert result.generation_time < 10.0  # Very generous for mocked test
        assert result.generation_time > 0.0

    @pytest.mark.asyncio
    async def test_empty_inputs_handling(self, mock_openai_client):
        """Test handling of edge cases with empty inputs."""
        # Mock response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Minimal response"

        generator = CoverLetterGenerator(mock_openai_client)

        # Test with minimal inputs
        result = await generator.generate("# Minimal", "Job position")
        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 10

    @pytest.mark.asyncio
    async def test_quality_score_calculation(
        self, mock_openai_client, sample_resume, sample_job_description
    ):
        """Test that quality scores are calculated reasonably."""
        # Mock good response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Python, Django, качественный"

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(sample_resume, sample_job_description)

        # Quality score should be reasonable
        assert 0.0 <= result.quality_score <= 1.0
        assert isinstance(result.quality_score, float)
