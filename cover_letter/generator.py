import time

from openai import AsyncOpenAI

from .analyzer import JobAnalyzer
from .models import CoverLetterResult, JobAnalysis, RoleType, ValidationResult, Requirements
from .prompt_builder import PromptBuilder


class CoverLetterGenerator:
    """
    Simple cover letter generator.
    """

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize the generator."""
        self.client = openai_client
        self.analyzer = JobAnalyzer(openai_client)
        self.prompt_builder = PromptBuilder()

    async def generate(
        self,
        resume: str,
        job_description: str,
        company_name: str = "",
        hiring_manager: str = "",
        special_requirements: str = "",
    ) -> CoverLetterResult:
        """
        Generate cover letter - simplified version.
        """
        start_time = time.time()

        try:
            # Step 1: Simple job analysis
            job_analysis = await self.analyzer.analyze_job(job_description)

            # Override company name if provided
            if company_name:
                job_analysis.company_name = company_name

            # Step 2: Use hardcoded role
            selected_role = self.prompt_builder.select_optimal_role(job_analysis)

            # Step 3: Build simple prompts
            system_prompt = self.prompt_builder.build_system_prompt(selected_role, {})

            additional_context = {"company_name": company_name}
            user_prompt = self.prompt_builder.build_user_prompt(
                resume, job_description, job_analysis, additional_context
            )

            # Step 4: Generate cover letter
            cover_letter = await self._generate_simple(system_prompt, user_prompt)

            generation_time = time.time() - start_time

            # Simple validation
            validation_result = self._create_simple_validation(cover_letter, job_analysis.keywords)

            # Simple metadata
            metadata = {
                "role_description": "Опытный HR-специалист",
                "word_count": len(cover_letter.split()),
                "keywords_found": sum(
                    1 for kw in job_analysis.keywords if kw.lower() in cover_letter.lower()
                ),
                "total_keywords": len(job_analysis.keywords),
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

        except Exception:
            # Simple fallback
            return await self._simple_fallback(resume, job_description, start_time)

    async def _generate_simple(self, system_prompt: str, user_prompt: str) -> str:
        """Simple generation without complexity."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            return content if content else "Ошибка генерации сопроводительного письма"

        except Exception as e:
            return f"Ошибка при генерации: {str(e)}"

    def _create_simple_validation(self, cover_letter: str, keywords: list) -> ValidationResult:
        """Create simple validation result."""
        word_count = len(cover_letter.split())

        # Simple checks
        length_ok = 200 <= word_count <= 500
        structure_ok = len(cover_letter.split("\n\n")) >= 2  # At least 2 paragraphs

        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw.lower() in cover_letter.lower())
        keyword_ratio = keyword_matches / len(keywords) if keywords else 0

        # Simple score calculation
        score = 0.7  # Base score
        if length_ok:
            score += 0.1
        if structure_ok:
            score += 0.1
        score += min(keyword_ratio * 0.2, 0.2)  # Max 0.2 bonus for keywords

        return ValidationResult(
            is_valid=length_ok and structure_ok,
            score=min(score, 1.0),
            length_ok=length_ok,
            structure_ok=structure_ok,
            has_metrics=False,  # Simplified
            keyword_match=keyword_ratio,
            personalization_score=0.8,  # Simplified
            issues=[],
            suggestions=[],
        )

    async def _simple_fallback(
        self, resume: str, job_description: str, start_time: float
    ) -> CoverLetterResult:
        """Ultra-simple fallback generation."""
        try:
            simple_prompt = """
            Создай короткое сопроводительное письмо на русском языке.
            Используй опыт из резюме и упомяни подходящие навыки для вакансии.
            Длина: 250-350 слов.
            """

            user_prompt = f"Резюме:\n{resume}\n\nВакансия:\n{job_description}"

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": simple_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.5,
            )

            cover_letter = response.choices[0].message.content or "Ошибка генерации"
            generation_time = time.time() - start_time

            # Minimal result
            return CoverLetterResult(
                cover_letter=cover_letter,
                quality_score=0.7,
                validation_result=ValidationResult(
                    is_valid=True,
                    score=0.7,
                    length_ok=True,
                    structure_ok=True,
                    has_metrics=False,
                    keyword_match=0.5,
                    personalization_score=0.5,
                    issues=[],
                    suggestions=[],
                ),
                job_analysis=JobAnalysis(
                    keywords=[],
                    company_name=None,
                    company_size=None,
                    company_culture=None,
                    industry=None,
                    requirements=Requirements(
                        hard_skills=[],
                        soft_skills=[],
                        experience_years=None,
                        education_level=None,
                        certifications=[]
                    ),
                    seniority_level=None,
                    is_technical_role=False,
                    is_creative_role=False,
                ),
                role_used=RoleType.CORPORATE_RECRUITER,
                generation_time=generation_time,
                metadata={"fallback_used": True},
            )

        except Exception as e:
            generation_time = time.time() - start_time
            return CoverLetterResult(
                cover_letter=f"Критическая ошибка: {str(e)}",
                quality_score=0.0,
                validation_result=ValidationResult(
                    is_valid=False,
                    score=0.0,
                    length_ok=False,
                    structure_ok=False,
                    has_metrics=False,
                    keyword_match=0.0,
                    personalization_score=0.0,
                    issues=["Ошибка генерации"],
                    suggestions=[],
                ),
                job_analysis=JobAnalysis(
                    keywords=[],
                    company_name=None,
                    company_size=None,
                    company_culture=None,
                    industry=None,
                    requirements=Requirements(
                        hard_skills=[],
                        soft_skills=[],
                        experience_years=None,
                        education_level=None,
                        certifications=[]
                    ),
                    seniority_level=None,
                    is_technical_role=False,
                    is_creative_role=False,
                ),
                role_used=RoleType.CORPORATE_RECRUITER,
                generation_time=generation_time,
                metadata={"error": str(e)},
            )
