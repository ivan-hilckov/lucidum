"""
Cover Letter Generation Package for Lucidum Bot.

This package provides advanced cover letter generation capabilities
with analysis, validation, and role-based prompting.
"""

from .generator import CoverLetterGenerator
from .models import CoverLetterResult, JobAnalysis, ValidationResult

__all__ = ["CoverLetterGenerator", "CoverLetterResult", "JobAnalysis", "ValidationResult"]
