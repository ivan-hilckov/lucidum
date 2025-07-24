"""
Job analysis functionality for extracting key information from job descriptions.
"""

import re
from typing import List, Optional
from openai import AsyncOpenAI

from .models import JobAnalysis, Requirements, CompanySize, CompanyCulture


class JobAnalyzer:
    """Analyzes job descriptions to extract key information."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def analyze_job(self, job_description: str) -> JobAnalysis:
        """
        Analyze job description and extract all relevant information.

        Args:
            job_description: The job description text

        Returns:
            JobAnalysis object with extracted information
        """
        # Extract basic information in parallel
        keywords = await self._extract_keywords(job_description)
        company_info = await self._analyze_company_info(job_description)
        requirements = await self._extract_requirements(job_description)

        # Determine role characteristics
        is_technical = self._is_technical_role(job_description)
        is_creative = self._is_creative_role(job_description)
        seniority = self._determine_seniority(job_description)

        return JobAnalysis(
            keywords=keywords,
            company_name=company_info.get("name"),
            company_size=company_info.get("size"),
            company_culture=company_info.get("culture"),
            industry=company_info.get("industry"),
            requirements=requirements,
            seniority_level=seniority,
            is_technical_role=is_technical,
            is_creative_role=is_creative,
        )

    async def _extract_keywords(self, job_description: str) -> List[str]:
        """Extract ATS keywords from job description."""
        prompt = f"""
        Проанализируй описание вакансии и извлеки ключевые слова для ATS-систем.
        
        Верни 10-15 наиболее важных ключевых слов и фраз, которые должны быть в сопроводительном письме.
        Включи: технические навыки, soft skills, инструменты, методологии, требования.
        
        Формат ответа: просто список слов через запятую, без нумерации и пояснений.
        
        Описание вакансии:
        {job_description}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                # Parse keywords from response
                keywords = [kw.strip() for kw in content.split(",")]
                return [kw for kw in keywords if kw and len(kw) > 2][:15]

        except Exception as e:
            print(f"Error extracting keywords: {e}")

        # Fallback: simple regex extraction
        return self._extract_keywords_regex(job_description)

    def _extract_keywords_regex(self, job_description: str) -> List[str]:
        """Fallback keyword extraction using regex patterns."""
        keywords = []

        # Common technical terms
        tech_patterns = [
            r"\b(?:Python|Java|JavaScript|React|Angular|Vue|Django|Flask)\b",
            r"\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis)\b",
            r"\b(?:AWS|Azure|GCP|Docker|Kubernetes)\b",
            r"\b(?:Git|CI/CD|DevOps|Agile|Scrum)\b",
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            keywords.extend(matches)

        # Clean and deduplicate
        keywords = list(set([kw.lower() for kw in keywords]))
        return keywords[:10]

    async def _analyze_company_info(self, job_description: str) -> dict:
        """Analyze company information from job description."""
        prompt = f"""
        Проанализируй описание вакансии и определи информацию о компании.
        
        Верни JSON с полями:
        - "name": название компании (если упомянуто)
        - "size": размер (startup/small/medium/large/enterprise)
        - "culture": культура (formal/casual/creative/technical/mission_driven)
        - "industry": отрасль
        
        Если информация не ясна, используй null.
        
        Описание вакансии:
        {job_description[:1000]}...
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                import json

                try:
                    info = json.loads(content)
                    # Convert strings to enums
                    if info.get("size"):
                        info["size"] = CompanySize(info["size"])
                    if info.get("culture"):
                        info["culture"] = CompanyCulture(info["culture"])
                    return info
                except (json.JSONDecodeError, ValueError):
                    pass

        except Exception as e:
            print(f"Error analyzing company info: {e}")

        return {}

    async def _extract_requirements(self, job_description: str) -> Requirements:
        """Extract job requirements from description."""
        prompt = f"""
        Проанализируй описание вакансии и извлеки требования.
        
        Верни JSON с полями:
        - "hard_skills": список технических навыков
        - "soft_skills": список soft skills
        - "experience_years": количество лет опыта (число или null)
        - "education_level": уровень образования
        - "certifications": список сертификаций
        
        Описание вакансии:
        {job_description[:1500]}...
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1,
            )

            content = response.choices[0].message.content
            if content:
                import json

                try:
                    req_data = json.loads(content)
                    return Requirements(
                        hard_skills=req_data.get("hard_skills", []),
                        soft_skills=req_data.get("soft_skills", []),
                        experience_years=req_data.get("experience_years"),
                        education_level=req_data.get("education_level"),
                        certifications=req_data.get("certifications", []),
                    )
                except (json.JSONDecodeError, ValueError):
                    pass

        except Exception as e:
            print(f"Error extracting requirements: {e}")

        # Fallback empty requirements
        return Requirements(
            hard_skills=[],
            soft_skills=[],
            experience_years=None,
            education_level=None,
            certifications=[],
        )

    def _is_technical_role(self, job_description: str) -> bool:
        """Determine if this is a technical role."""
        technical_keywords = [
            "developer",
            "engineer",
            "programmer",
            "architect",
            "devops",
            "python",
            "java",
            "javascript",
            "sql",
            "api",
            "database",
            "git",
            "coding",
            "software",
            "technical",
            "разработчик",
        ]

        text_lower = job_description.lower()
        return any(keyword in text_lower for keyword in technical_keywords)

    def _is_creative_role(self, job_description: str) -> bool:
        """Determine if this is a creative role."""
        creative_keywords = [
            "designer",
            "creative",
            "artist",
            "content",
            "marketing",
            "brand",
            "visual",
            "graphic",
            "ui",
            "ux",
            "креативный",
        ]

        text_lower = job_description.lower()
        return any(keyword in text_lower for keyword in creative_keywords)

    def _determine_seniority(self, job_description: str) -> Optional[str]:
        """Determine seniority level from job description."""
        text_lower = job_description.lower()

        if any(
            word in text_lower for word in ["senior", "lead", "principal", "ведущий", "старший"]
        ):
            return "senior"
        elif any(word in text_lower for word in ["junior", "entry", "начинающий", "младший"]):
            return "junior"
        elif any(word in text_lower for word in ["middle", "mid", "средний"]):
            return "middle"

        return None
