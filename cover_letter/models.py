"""
Data models for cover letter generation system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobAnalysis(BaseModel):
    """Simplified job analysis result."""

    keywords: List[str] = Field(
        default_factory=list, description="Extracted keywords from job description"
    )
    company_name: Optional[str] = Field(default=None, description="Company name if found")


class CoverLetterResult(BaseModel):
    """Result of cover letter generation."""

    cover_letter: str = Field(description="Generated cover letter content")
    quality_score: float = Field(ge=0.0, le=1.0, description="Quality score from 0.0 to 1.0")
    keywords_found: int = Field(ge=0, description="Number of keywords found in cover letter")
    generation_time: float = Field(ge=0.0, description="Time taken to generate in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
