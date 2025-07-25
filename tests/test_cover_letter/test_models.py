"""
Tests for cover letter models.
"""

from cover_letter.models import (
    JobAnalysis,
    CoverLetterResult,
)


class TestJobAnalysis:
    """Test JobAnalysis model."""

    def test_create_job_analysis(self):
        """Test JobAnalysis model creation."""
        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TechCorp",
        )

        assert job_analysis.keywords == ["Python", "Django"]
        assert job_analysis.company_name == "TechCorp"

    def test_job_analysis_with_none_company(self):
        """Test JobAnalysis with None company name."""
        job_analysis = JobAnalysis(
            keywords=["Python"],
            company_name=None,
        )

        assert job_analysis.keywords == ["Python"]
        assert job_analysis.company_name is None

    def test_job_analysis_default_company(self):
        """Test JobAnalysis with default company name."""
        job_analysis = JobAnalysis(keywords=["Python"])

        assert job_analysis.keywords == ["Python"]
        assert job_analysis.company_name is None


class TestCoverLetterResult:
    """Test CoverLetterResult model."""

    def test_cover_letter_result(self):
        """Test CoverLetterResult creation."""
        result = CoverLetterResult(
            cover_letter="Test cover letter content",
            quality_score=0.85,
            keywords_found=5,
            generation_time=1.5,
            metadata={"test": "value"},
        )

        assert result.cover_letter == "Test cover letter content"
        assert result.quality_score == 0.85
        assert result.keywords_found == 5
        assert result.generation_time == 1.5
        assert result.metadata == {"test": "value"}

    def test_cover_letter_result_with_empty_metadata(self):
        """Test CoverLetterResult with empty metadata."""
        result = CoverLetterResult(
            cover_letter="Short letter",
            quality_score=0.5,
            keywords_found=0,
            generation_time=0.8,
            metadata={},
        )

        assert result.cover_letter == "Short letter"
        assert result.quality_score == 0.5
        assert result.keywords_found == 0
        assert result.generation_time == 0.8
        assert result.metadata == {}
