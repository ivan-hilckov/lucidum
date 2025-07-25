"""
Simple cover letter generation system.
"""

from .generator import CoverLetterGenerator
from .models import CoverLetterResult, JobAnalysis

__all__ = [
    "CoverLetterGenerator",
    "CoverLetterResult",
    "JobAnalysis",
]
