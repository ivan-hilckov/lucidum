"""
Cover letter validation functionality based on quality criteria.
"""

import re
from typing import List
from openai import AsyncOpenAI

from .models import ValidationResult


class CoverLetterValidator:
    """Validates cover letters against quality criteria."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def validate_cover_letter(
        self, cover_letter: str, keywords: List[str] = None, company_name: str = None
    ) -> ValidationResult:
        """
        Comprehensive validation of cover letter quality.

        Args:
            cover_letter: The generated cover letter text
            keywords: Expected keywords from job analysis
            company_name: Company name for personalization check

        Returns:
            ValidationResult with detailed analysis
        """
        keywords = keywords or []

        # Perform all validation checks
        length_ok = self._check_length(cover_letter)
        structure_ok = self._check_structure(cover_letter)
        has_metrics = self._check_metrics(cover_letter)
        keyword_match = self._check_keywords(cover_letter, keywords)
        personalization_score = self._check_personalization(cover_letter, company_name)

        # Collect issues and suggestions
        issues = []
        suggestions = []

        if not length_ok:
            issues.append("Неподходящая длина (должно быть 250-400 слов)")
            suggestions.append("Отредактируйте до рекомендуемой длины")

        if not structure_ok:
            issues.append("Недостаточно абзацев для хорошей структуры")
            suggestions.append("Разделите на 3-5 абзацев")

        if not has_metrics:
            issues.append("Отсутствуют количественные достижения")
            suggestions.append("Добавьте минимум 2 метрики или цифры")

        if keyword_match < 0.3:
            issues.append("Мало ключевых слов из вакансии")
            suggestions.append("Включите больше релевантных терминов")

        if personalization_score < 0.5:
            issues.append("Недостаточная персонализация")
            suggestions.append("Упомяните конкретную компанию и позицию")

        # Calculate overall score (0.0 to 1.0)
        score_components = [
            1.0 if length_ok else 0.0,
            1.0 if structure_ok else 0.0,
            1.0 if has_metrics else 0.0,
            keyword_match,
            personalization_score,
        ]

        overall_score = sum(score_components) / len(score_components)
        is_valid = overall_score >= 0.7  # 70% threshold

        return ValidationResult(
            is_valid=is_valid,
            score=overall_score,
            length_ok=length_ok,
            structure_ok=structure_ok,
            has_metrics=has_metrics,
            keyword_match=keyword_match,
            personalization_score=personalization_score,
            issues=issues,
            suggestions=suggestions,
        )

    def _check_length(self, text: str) -> bool:
        """Check if text length is within recommended range."""
        words = len(text.split())
        return 250 <= words <= 400

    def _check_structure(self, text: str) -> bool:
        """Check if text has appropriate paragraph structure."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return 3 <= len(paragraphs) <= 5

    def _check_metrics(self, text: str) -> bool:
        """Check for presence of quantifiable achievements."""
        # Look for numbers, percentages, timeframes
        metrics_patterns = [
            r"\d+%",  # percentages
            r"\d+\s*(млн|тыс|лет|год|месяц)",  # numbers with units
            r"\d+\s*(million|thousand|years?|months?)",  # English units
            r"\$\d+",  # money
            r"\d+[.,]\d*",  # decimal numbers
            r"\d+\+",  # numbers with +
            r"на\s+\d+%",  # "на X%"
            r"в\s+\d+\s+раз",  # "в X раз"
        ]

        metrics_found = 0
        for pattern in metrics_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics_found += len(matches)

        return metrics_found >= 2

    def _check_keywords(self, text: str, keywords: List[str]) -> float:
        """Check what percentage of keywords are present."""
        if not keywords:
            return 1.0  # No keywords to check

        text_lower = text.lower()
        found_keywords = 0

        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords += 1

        return found_keywords / len(keywords)

    def _check_personalization(self, text: str, company_name: str = None) -> float:
        """Check level of personalization in the cover letter."""
        personalization_score = 0.0

        # Check for company name mention
        if company_name and company_name.lower() in text.lower():
            personalization_score += 0.5

        # Check for specific role/position mentions
        position_keywords = [
            "позиция",
            "должность",
            "роль",
            "вакансия",
            "position",
            "role",
            "job",
            "opportunity",
        ]

        text_lower = text.lower()
        if any(keyword in text_lower for keyword in position_keywords):
            personalization_score += 0.3

        # Check for specific industry/domain terms
        specific_terms = [
            "компания",
            "организация",
            "команда",
            "проект",
            "company",
            "organization",
            "team",
            "project",
        ]

        if any(term in text_lower for term in specific_terms):
            personalization_score += 0.2

        return min(personalization_score, 1.0)

    async def assess_quality_with_llm(self, cover_letter: str) -> dict:
        """
        Use LLM to assess cover letter quality more comprehensively.

        Args:
            cover_letter: The cover letter text to assess

        Returns:
            Dictionary with quality assessment and recommendations
        """
        prompt = f"""
        Оцени качество сопроводительного письма по критериям:
        
        1. Структура (введение, основная часть, заключение)
        2. Персонализация (упоминание компании/позиции)
        3. Конкретные достижения с метриками
        4. Профессиональный тон
        5. Отсутствие клише и банальностей
        6. Призыв к действию
        
        Верни JSON с полями:
        - "score": общий балл от 1 до 10
        - "strengths": список сильных сторон
        - "weaknesses": список слабых сторон  
        - "recommendations": рекомендации по улучшению
        
        Сопроводительное письмо:
        {cover_letter}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                import json

                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            print(f"Error in LLM quality assessment: {e}")

        # Fallback assessment
        return {
            "score": 7,
            "strengths": ["Базовая структура присутствует"],
            "weaknesses": ["Автоматическая оценка недоступна"],
            "recommendations": ["Проверьте вручную по критериям качества"],
        }
