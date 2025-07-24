"""
Prompt building functionality for cover letter generation.
"""

from typing import Dict, Any
from .models import JobAnalysis, RoleType, CompanySize, CompanyCulture
from .roles import RoleDefinitions


class PromptBuilder:
    """Builds prompts for cover letter generation based on job analysis."""

    def __init__(self):
        self.role_definitions = RoleDefinitions()

    def select_optimal_role(self, job_analysis: JobAnalysis) -> RoleType:
        """
        Select the most appropriate role based on job analysis.

        Args:
            job_analysis: Analysis of the job description

        Returns:
            Most suitable RoleType for this job
        """
        # Rule-based role selection logic

        # For entry-level positions
        if job_analysis.seniority_level == "junior":
            return RoleType.GROWTH_MINDSET_COACH

        # For technical roles
        if job_analysis.is_technical_role:
            return RoleType.INDUSTRY_SME

        # For creative roles
        if job_analysis.is_creative_role:
            return RoleType.STORYTELLING_COACH

        # For sales/marketing roles
        if job_analysis.industry and any(
            word in job_analysis.industry.lower() for word in ["sales", "marketing", "продаж"]
        ):
            return RoleType.PERSUASIVE_COPYWRITER

        # For large enterprises (ATS-heavy)
        if job_analysis.company_size in [CompanySize.LARGE, CompanySize.ENTERPRISE]:
            return RoleType.ATS_SPECIALIST

        # For startups and small companies
        if job_analysis.company_size in [CompanySize.STARTUP, CompanySize.SMALL]:
            return RoleType.HIRING_MANAGER_PEER

        # For creative/mission-driven cultures
        if job_analysis.company_culture in [CompanyCulture.CREATIVE, CompanyCulture.MISSION_DRIVEN]:
            return RoleType.STORYTELLING_COACH

        # Default fallback
        return RoleType.CORPORATE_RECRUITER

    def build_system_prompt(self, role_type: RoleType, context: Dict[str, Any]) -> str:
        """
        Build system prompt for the selected role.

        Args:
            role_type: Selected role type
            context: Additional context for prompt customization

        Returns:
            Complete system prompt string
        """
        base_prompt = self.role_definitions.get_role_prompt(role_type)

        # Add universal quality criteria
        quality_criteria = """
        
КРИТЕРИИ КАЧЕСТВА:
- Длина: 250-400 слов
- Структура: Введение, основная часть (достижения), культурное соответствие, заключение  
- Персонализация: упоминание компании и конкретной позиции
- Метрики: минимум 2 количественных достижения
- Тон: профессиональный, уверенный, но не агрессивный

ИЗБЕГАЙ:
- Повторения информации из резюме
- Общих фраз типа "командный игрок"
- Упоминания зарплатных ожиданий
- Негативных комментариев о предыдущих работодателях

САМОПРОВЕРКА ПЕРЕД ОТВЕТОМ:
- Правильно ли указано название компании?
- Есть ли конкретные метрики?
- Использованы ли ключевые слова?
- Соответствует ли длина требованиям?
        """

        # Customize prompt with context
        if context.get("keywords"):
            keywords_text = f"\nКЛЮЧЕВЫЕ СЛОВА ДЛЯ ATS: {', '.join(context['keywords'])}"
            base_prompt += keywords_text

        if context.get("industry") and role_type == RoleType.INDUSTRY_SME:
            base_prompt = base_prompt.replace("{INDUSTRY}", context["industry"])

        return base_prompt + quality_criteria

    def build_user_prompt(
        self,
        resume: str,
        job_description: str,
        job_analysis: JobAnalysis,
        additional_context: Dict[str, Any] = None,
    ) -> str:
        """
        Build user prompt with structured information.

        Args:
            resume: User's resume content
            job_description: Job description text
            job_analysis: Analysis of the job
            additional_context: Additional context (company name, hiring manager, etc.)

        Returns:
            Complete user prompt string
        """
        additional_context = additional_context or {}

        prompt_parts = [
            "ИНФОРМАЦИЯ О КАНДИДАТЕ:",
            resume,
            "",
            "ОПИСАНИЕ ВАКАНСИИ:",
            job_description,
        ]

        # Add structured context
        if job_analysis.company_name or additional_context.get("company_name"):
            company = job_analysis.company_name or additional_context.get("company_name")
            prompt_parts.extend(["", f"КОМПАНИЯ: {company}"])

        if job_analysis.keywords:
            prompt_parts.extend(
                ["", f"КЛЮЧЕВЫЕ НАВЫКИ ИЗ ВАКАНСИИ: {', '.join(job_analysis.keywords)}"]
            )

        if job_analysis.industry:
            prompt_parts.extend(["", f"ТИП ИНДУСТРИИ: {job_analysis.industry}"])

        if job_analysis.company_culture:
            prompt_parts.extend(["", f"КУЛЬТУРА КОМПАНИИ: {job_analysis.company_culture.value}"])

        # Add additional context if provided
        if additional_context:
            prompt_parts.append("")
            prompt_parts.append("ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:")

            if additional_context.get("hiring_manager"):
                prompt_parts.append(f"- Имя рекрутера: {additional_context['hiring_manager']}")

            if job_analysis.company_size:
                prompt_parts.append(f"- Размер компании: {job_analysis.company_size.value}")

            if job_analysis.seniority_level:
                prompt_parts.append(f"- Уровень позиции: {job_analysis.seniority_level}")

            if additional_context.get("special_requirements"):
                prompt_parts.append(
                    f"- Особенности вакансии: {additional_context['special_requirements']}"
                )

        return "\n".join(prompt_parts)

    def get_role_temperature(self, role_type: RoleType) -> float:
        """Get the recommended temperature for the role."""
        return self.role_definitions.get_role_temperature(role_type)

    def get_role_description(self, role_type: RoleType) -> str:
        """Get human-readable description of the role."""
        return self.role_definitions.get_role_description(role_type)
