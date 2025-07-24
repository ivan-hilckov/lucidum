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
        Select role - hardcoded to CORPORATE_RECRUITER for simplicity.
        """
        # Always use CORPORATE_RECRUITER - simple and reliable
        return RoleType.CORPORATE_RECRUITER

    def build_system_prompt(self, role_type: RoleType, context: Dict[str, Any]) -> str:
        """
        Build simple system prompt.
        """
        # Simple, effective prompt
        prompt = """
Ты - опытный HR-специалист, который пишет сопроводительные письма для отклика на вакансии.

Создай профессиональное сопроводительное письмо на русском языке.

ТРЕБОВАНИЯ:
- Длина: 250-350 слов
- Структура: Приветствие + 2 абзаца с достижениями + Заключение
- Включи 2-3 конкретных достижения с цифрами из резюме
- Используй навыки из описания вакансии
- Тон: уверенный, профессиональный

ИЗБЕГАЙ:
- Общих фраз
- Повторения резюме
- Лишних эмоций
- Упоминания зарплаты
        """

        return prompt

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
        """Get temperature - always 0.3 for consistency."""
        return 0.3

    def get_role_description(self, role_type: RoleType) -> str:
        """Get role description."""
        return "Опытный HR-специалист"
