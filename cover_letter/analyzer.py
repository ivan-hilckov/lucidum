"""
Simple job analysis functionality.
"""

import re
from typing import List, Optional
from openai import AsyncOpenAI

from .models import JobAnalysis, Requirements


class JobAnalyzer:
    """Simple job analyzer - minimal complexity."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def analyze_job(self, job_description: str) -> JobAnalysis:
        """
        Simple job analysis - extract basic info only.
        """
        # Simple keyword extraction
        keywords = await self._extract_keywords_simple(job_description)

        # Basic company name extraction
        company_name = self._extract_company_name(job_description)

        # Simple role detection
        is_technical = self._is_technical_role(job_description)
        is_creative = self._is_creative_role(job_description)

        return JobAnalysis(
            keywords=keywords,
            company_name=company_name,
            company_size=None,  # Simplified - don't need this
            company_culture=None,  # Simplified - don't need this
            industry=None,  # Simplified - don't need this
            requirements=Requirements([], [], None, None, []),  # Empty requirements
            seniority_level=None,  # Simplified - don't need this
            is_technical_role=is_technical,
            is_creative_role=is_creative,
        )

    async def _extract_keywords_simple(self, job_description: str) -> List[str]:
        """Simple keyword extraction using OpenAI."""
        prompt = f"""
        Извлеки 8-12 ключевых навыков и технологий из описания вакансии.
        Верни только список через запятую, без объяснений.

        Описание вакансии:
        {job_description[:1000]}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                # Parse keywords
                keywords = [kw.strip() for kw in content.split(",")]
                return [kw for kw in keywords if kw and len(kw) > 2][:12]

        except Exception as e:
            print(f"Keyword extraction failed: {e}")

        # Fallback: regex patterns
        return self._extract_keywords_regex(job_description)

    def _extract_keywords_regex(self, job_description: str) -> List[str]:
        """Fallback keyword extraction using regex."""
        keywords = []
        text_lower = job_description.lower()

        # Common patterns
        patterns = [
            r"\b(?:python|javascript|react|vue|angular|django|flask)\b",
            r"\b(?:sql|mysql|postgresql|mongodb|redis)\b",
            r"\b(?:git|docker|aws|azure|kubernetes)\b",
            r"\b(?:html|css|typescript|node\.?js)\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)

        return list(set(keywords))[:8]

    def _extract_company_name(self, job_description: str) -> Optional[str]:
        """Extract company name using simple patterns."""
        lines = job_description.split("\n")

        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Look for "Компания: X" pattern
            if "компания:" in line.lower():
                return line.split(":", 1)[1].strip()
            # Look for company name in common patterns
            if any(word in line.lower() for word in ["ооо", "зао", "оао", "ип"]):
                return line.strip()

        return None

    def _is_technical_role(self, job_description: str) -> bool:
        """Simple technical role detection."""
        technical_keywords = [
            "разработчик",
            "developer",
            "программист",
            "engineer",
            "python",
            "javascript",
            "react",
            "sql",
            "git",
            "api",
            "data scientist",
            "scientist",
            "devops",
            "frontend",
            "backend",
            "machine learning",
        ]

        text_lower = job_description.lower()
        return any(keyword in text_lower for keyword in technical_keywords)

    def _is_creative_role(self, job_description: str) -> bool:
        """Simple creative role detection."""
        creative_keywords = [
            "дизайнер",
            "designer",
            "креативный",
            "creative",
            "ui",
            "ux",
            "графический",
            "маркетинг",
            "content",
            "writer",
            "писатель",
            "редактор",
            "editor",
            "video",
        ]

        text_lower = job_description.lower()
        return any(keyword in text_lower for keyword in creative_keywords)
