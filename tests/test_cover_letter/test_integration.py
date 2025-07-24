"""
Integration tests for complete cover letter generation pipeline.
"""

import pytest
from cover_letter import CoverLetterGenerator, CoverLetterResult, ValidationResult, JobAnalysis


class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_end_to_end_generation(
        self, mock_openai_client, mock_response_builder, sample_resume, sample_job_description
    ):
        """Test complete cover letter generation pipeline."""
        # Set up mock responses for full pipeline
        responses = mock_response_builder.create_analysis_responses() + [
            mock_response_builder.create_cover_letter_response()
        ]
        mock_openai_client.chat.completions.create.side_effect = responses

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(sample_resume, sample_job_description)

        # Verify complete result structure
        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 200
        assert result.quality_score >= 0.0
        assert result.quality_score <= 1.0
        assert isinstance(result.validation_result, ValidationResult)
        assert isinstance(result.job_analysis, JobAnalysis)
        assert result.generation_time > 0
        assert isinstance(result.metadata, dict)

        # Verify content quality
        assert "TechStart" in result.cover_letter
        assert "Python" in result.cover_letter
        assert result.validation_result.is_valid

    @pytest.mark.asyncio
    async def test_simple_generation(
        self, mock_openai_client, simple_resume, simple_job_description
    ):
        """Test generation with simple inputs."""
        # Mock simple response
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Python, Django, разработчик"

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
        # Mock keyword extraction
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Python, Django"

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(
            simple_resume, simple_job_description, company_name="CustomCorp"
        )

        assert isinstance(result, CoverLetterResult)
        assert result.job_analysis.company_name == "CustomCorp"

    @pytest.mark.asyncio
    async def test_fallback_on_error(
        self, mock_openai_client, simple_resume, simple_job_description
    ):
        """Test fallback generation when main generation fails."""

        # First calls fail, last call succeeds (fallback)
        def side_effect(*args, **kwargs):
            if side_effect.call_count < 2:
                side_effect.call_count += 1
                raise Exception("API Error")
            else:
                response = mock_openai_client.chat.completions.create.return_value
                response.choices[
                    0
                ].message.content = "Простое сопроводительное письмо для fallback тестирования."
                return response

        side_effect.call_count = 0
        mock_openai_client.chat.completions.create.side_effect = side_effect

        generator = CoverLetterGenerator(mock_openai_client)
        result = await generator.generate(simple_resume, simple_job_description)

        assert isinstance(result, CoverLetterResult)
        assert len(result.cover_letter) > 20
        # Should indicate fallback was used
        assert result.metadata.get("fallback_used", False) or result.quality_score < 0.7

    @pytest.mark.asyncio
    async def test_different_job_types(self, mock_openai_client):
        """Test generation with different types of job descriptions."""
        # Technical job
        tech_resume = "# Dev\nPython developer"
        tech_job = "Looking for Python developer with React experience"

        # Creative job
        creative_resume = "# Designer\nGraphic designer"
        creative_job = "Looking for UX/UI designer with Figma skills"

        # Mock responses
        mock_openai_client.chat.completions.create.return_value.choices[
            0
        ].message.content = "Test response"

        generator = CoverLetterGenerator(mock_openai_client)

        # Test technical job
        tech_result = await generator.generate(tech_resume, tech_job)
        assert isinstance(tech_result, CoverLetterResult)
        assert tech_result.job_analysis.is_technical_role

        # Test creative job
        creative_result = await generator.generate(creative_resume, creative_job)
        assert isinstance(creative_result, CoverLetterResult)
        assert creative_result.job_analysis.is_creative_role

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
