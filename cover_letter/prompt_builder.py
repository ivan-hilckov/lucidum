"""
Prompt building functionality for cover letter generation.
"""

from typing import Dict, Any, Optional
from .models import JobAnalysis, RoleType
from .roles import RoleDefinitions


class PromptBuilder:
    """Builds prompts for cover letter generation based on job analysis."""

    def __init__(self):
        self.role_definitions = RoleDefinitions()

    def select_optimal_role(self, job_analysis: JobAnalysis) -> RoleType:
        """
        Select role - always return CORPORATE_RECRUITER for simplicity in this implementation.
        """
        # Always use CORPORATE_RECRUITER - simple and reliable
        return RoleType.CORPORATE_RECRUITER

    def build_system_prompt(self, role_type: RoleType, context: Dict[str, Any]) -> str:
        """
        Build system prompt using role definitions.
        """
        # Get role-specific prompt
        base_prompt = RoleDefinitions.get_role_prompt(role_type)

        # Add keywords if provided
        if "keywords" in context and context["keywords"]:
            keywords_text = ", ".join(context["keywords"])
            keywords_section = f"\nКлючевые навыки: {keywords_text}\n"
            base_prompt += keywords_section
        else:
            base_prompt += "\nКлючевые навыки: \n"

        return base_prompt

    def build_user_prompt(
        self,
        resume: str,
        job_description: str,
        job_analysis: JobAnalysis,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build simple user prompt.
        """
        additional_context = additional_context or {}

        # Simple structure
        prompt_parts = [
            "РЕЗЮМЕ КАНДИДАТА:",
            resume,
            "",
            "ОПИСАНИЕ ВАКАНСИИ:",
            job_description,
        ]

        # Add company name if provided
        if job_analysis.company_name or additional_context.get("company_name"):
            company = job_analysis.company_name or additional_context.get("company_name")
            prompt_parts.extend(["", f"НАЗВАНИЕ КОМПАНИИ: {company}"])

        return "\n".join(prompt_parts)

    def get_role_temperature(self, role_type: RoleType) -> float:
        """Get temperature from role definitions."""
        return RoleDefinitions.get_role_temperature(role_type)

    def get_role_description(self, role_type: RoleType) -> str:
        """Get role description from role definitions."""
        return RoleDefinitions.get_role_description(role_type)
