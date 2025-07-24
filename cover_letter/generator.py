"""
Main cover letter generator that orchestrates all components.
"""

import time
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from .models import CoverLetterResult, JobAnalysis, ValidationResult, RoleType
from .analyzer import JobAnalyzer
from .prompt_builder import PromptBuilder
from .validator import CoverLetterValidator


class CoverLetterGenerator:
    """
    Main class for generating high-quality cover letters.

    Orchestrates job analysis, role selection, prompt building,
    generation, and validation.
    """

    def __init__(self, openai_client: AsyncOpenAI):
        """
        Initialize the cover letter generator.

        Args:
            openai_client: OpenAI API client instance
        """
        self.client = openai_client
        self.analyzer = JobAnalyzer(openai_client)
        self.prompt_builder = PromptBuilder()
        self.validator = CoverLetterValidator(openai_client)

    async def generate(
        self,
        resume: str,
        job_description: str,
        company_name: str = "",
        hiring_manager: str = "",
        special_requirements: str = "",
    ) -> CoverLetterResult:
        """
        Generate a high-quality cover letter.

        Args:
            resume: User's resume in markdown format
            job_description: Job posting description
            company_name: Optional company name override
            hiring_manager: Optional hiring manager name
            special_requirements: Optional special requirements or notes

        Returns:
            CoverLetterResult with generated letter and metadata
        """
        start_time = time.time()

        try:
            # Step 1: Analyze the job description
            job_analysis = await self.analyzer.analyze_job(job_description)

            # Override company name if provided
            if company_name:
                job_analysis.company_name = company_name

            # Step 2: Select optimal role and build prompts
            selected_role = self.prompt_builder.select_optimal_role(job_analysis)

            context = {"keywords": job_analysis.keywords, "industry": job_analysis.industry}

            system_prompt = self.prompt_builder.build_system_prompt(selected_role, context)

            additional_context = {
                "company_name": company_name,
                "hiring_manager": hiring_manager,
                "special_requirements": special_requirements,
            }

            user_prompt = self.prompt_builder.build_user_prompt(
                resume, job_description, job_analysis, additional_context
            )

            # Step 3: Generate cover letter
            cover_letter = await self._generate_with_role(system_prompt, user_prompt, selected_role)

            # Step 4: Validate and potentially improve
            validation_result = await self.validator.validate_cover_letter(
                cover_letter, job_analysis.keywords, job_analysis.company_name or company_name
            )

            # Step 5: Attempt improvement if quality is low
            if not validation_result.is_valid and validation_result.score < 0.6:
                cover_letter = await self._attempt_improvement(
                    system_prompt, user_prompt, selected_role, validation_result
                )

                # Re-validate improved version
                validation_result = await self.validator.validate_cover_letter(
                    cover_letter, job_analysis.keywords, job_analysis.company_name or company_name
                )

            generation_time = time.time() - start_time

            # Prepare metadata
            metadata = {
                "role_description": self.prompt_builder.get_role_description(selected_role),
                "keywords_found": len(
                    [kw for kw in job_analysis.keywords if kw.lower() in cover_letter.lower()]
                ),
                "total_keywords": len(job_analysis.keywords),
                "word_count": len(cover_letter.split()),
                "improvement_attempted": validation_result.score < 0.6,
            }

            return CoverLetterResult(
                cover_letter=cover_letter,
                quality_score=validation_result.score,
                validation_result=validation_result,
                job_analysis=job_analysis,
                role_used=selected_role,
                generation_time=generation_time,
                metadata=metadata,
            )

        except Exception as e:
            # Fallback to simple generation if advanced pipeline fails
            print(f"Advanced generation failed: {e}")
            return await self._fallback_generation(resume, job_description, start_time)

    async def _generate_with_role(
        self, system_prompt: str, user_prompt: str, role_type: RoleType
    ) -> str:
        """
        Generate cover letter using the selected role and prompts.

        Args:
            system_prompt: Complete system prompt for the role
            user_prompt: User prompt with structured data
            role_type: Selected role type for temperature setting

        Returns:
            Generated cover letter text
        """
        temperature = self.prompt_builder.get_role_temperature(role_type)

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=800,  # Enough for ~400 words
            temperature=temperature,
        )

        content = response.choices[0].message.content
        return content if content else "Ошибка: Пустой ответ от OpenAI"

    async def _attempt_improvement(
        self,
        system_prompt: str,
        user_prompt: str,
        role_type: RoleType,
        validation_result: ValidationResult,
    ) -> str:
        """
        Attempt to improve the cover letter based on validation feedback.

        Args:
            system_prompt: Original system prompt
            user_prompt: Original user prompt
            role_type: Role type used
            validation_result: Validation result with issues

        Returns:
            Improved cover letter text
        """
        improvement_prompt = f"""
        {system_prompt}
        
        ВАЖНО: Предыдущая версия имела следующие проблемы:
        {", ".join(validation_result.issues)}
        
        Рекомендации по улучшению:
        {", ".join(validation_result.suggestions)}
        
        Создай улучшенную версию, исправив эти проблемы.
        """

        try:
            return await self._generate_with_role(improvement_prompt, user_prompt, role_type)
        except Exception as e:
            print(f"Improvement attempt failed: {e}")
            # Return original if improvement fails
            return await self._generate_with_role(system_prompt, user_prompt, role_type)

    async def _fallback_generation(
        self, resume: str, job_description: str, start_time: float
    ) -> CoverLetterResult:
        """
        Fallback to simple generation if advanced pipeline fails.

        Args:
            resume: User's resume
            job_description: Job description
            start_time: Generation start time

        Returns:
            Basic CoverLetterResult
        """
        try:
            # Simple prompt similar to original
            simple_prompt = """
            Ты - профессиональный писатель сопроводительных писем. 
            Создай краткое, релевантное сопроводительное письмо на русском языке.
            Основывайся строго на реальном опыте и навыках из резюме.
            
            Длина: 250-400 слов
            Структура: введение, основная часть с достижениями, заключение
            Включи минимум 2 количественных показателя
            """

            user_prompt = f"""
            Резюме:
            {resume}
            
            Описание вакансии:
            {job_description}
            """

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": simple_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=800,
                temperature=0.5,
            )

            cover_letter = response.choices[0].message.content or "Ошибка генерации"
            generation_time = time.time() - start_time

            # Create minimal validation result
            validation_result = ValidationResult(
                is_valid=True,
                score=0.7,  # Assume reasonable quality
                length_ok=True,
                structure_ok=True,
                has_metrics=False,
                keyword_match=0.5,
                personalization_score=0.5,
                issues=[],
                suggestions=[],
            )

            # Create minimal job analysis
            job_analysis = JobAnalysis(
                keywords=[],
                company_name=None,
                company_size=None,
                company_culture=None,
                industry=None,
                requirements=None,
                seniority_level=None,
                is_technical_role=False,
                is_creative_role=False,
            )

            return CoverLetterResult(
                cover_letter=cover_letter,
                quality_score=0.7,
                validation_result=validation_result,
                job_analysis=job_analysis,
                role_used=RoleType.CORPORATE_RECRUITER,
                generation_time=generation_time,
                metadata={"fallback_used": True},
            )

        except Exception as e:
            generation_time = time.time() - start_time

            # Final fallback
            error_result = CoverLetterResult(
                cover_letter=f"Ошибка генерации сопроводительного письма: {str(e)}",
                quality_score=0.0,
                validation_result=ValidationResult(
                    is_valid=False,
                    score=0.0,
                    length_ok=False,
                    structure_ok=False,
                    has_metrics=False,
                    keyword_match=0.0,
                    personalization_score=0.0,
                    issues=["Критическая ошибка генерации"],
                    suggestions=[],
                ),
                job_analysis=JobAnalysis(
                    keywords=[],
                    company_name=None,
                    company_size=None,
                    company_culture=None,
                    industry=None,
                    requirements=None,
                    seniority_level=None,
                    is_technical_role=False,
                    is_creative_role=False,
                ),
                role_used=RoleType.CORPORATE_RECRUITER,
                generation_time=generation_time,
                metadata={"error": str(e)},
            )

            return error_result
