"""
Simple cover letter generation system.
"""

from .generator import CoverLetterGenerator
from .models import CoverLetterResult, JobAnalysis, RoleType, ValidationResult

__all__ = [
    "CoverLetterGenerator",
    "CoverLetterResult",
    "JobAnalysis",
    "RoleType",
    "ValidationResult",
]
