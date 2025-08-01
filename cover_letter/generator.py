"""
Simplified cover letter generator with all functionality combined.
"""

import logging
import re
import time
from typing import List, Optional

from openai import AsyncOpenAI, OpenAIError

from .models import CoverLetterResult, JobAnalysis
from .prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    COVER_LETTER_MAX_TOKENS,
    COVER_LETTER_TEMPERATURE,
    DEFAULT_MODEL,
    JOB_DESCRIPTION_PREVIEW_LIMIT,
    KEYWORD_EXTRACTION_MAX_TOKENS,
    KEYWORD_EXTRACTION_PROMPT,
    KEYWORD_EXTRACTION_TEMPERATURE,
    MINIMUM_COVER_LETTER_WORDS,
    TECH_SKILL_PATTERNS,
    FALLBACK_SYSTEM_PROMPT,
    FALLBACK_MAX_TOKENS,
    FALLBACK_TEMPERATURE,
)

# Configure logging
logger = logging.getLogger(__name__)


class CoverLetterGenerationError(Exception):
    """Error during cover letter generation."""

    pass


class CoverLetterGenerator:
    """
    Simplified cover letter generator with all functionality combined.
    """

    def __init__(self, openai_client: AsyncOpenAI):
        """Initialize the generator."""
        self.client = openai_client

    async def analyze_job_only(
        self,
        job_description: str,
        custom_keyword_prompt: Optional[str] = None,
    ) -> dict:
        """
        Analyze job description only, without generating cover letter.
        Returns analysis data for UI auto-fill.
        """
        try:
            job_analysis = await self._analyze_job(job_description, custom_keyword_prompt)

            # Extract additional metadata for UI
            additional_info = await self._extract_job_metadata(job_description)

            return {
                "company_name": job_analysis.company_name or "",
                "keywords": job_analysis.keywords,
                "hiring_manager": additional_info.get("hiring_manager", ""),
                "position_title": additional_info.get("position_title", ""),
                "key_requirements": additional_info.get("key_requirements", []),
                "confidence_score": 0.8 if job_analysis.company_name else 0.5,
            }
        except Exception as e:
            logger.error(f"Error in job analysis: {e}")
            return {
                "company_name": "",
                "keywords": [],
                "hiring_manager": "",
                "position_title": "",
                "key_requirements": [],
                "confidence_score": 0.0,
            }

    async def _extract_job_metadata(self, job_description: str) -> dict:
        """Extract additional job metadata for UI."""
        try:
            metadata_prompt = """
            Analyze the job description and extract key information. Return ONLY a JSON object with these fields:
            - hiring_manager: Hiring manager name if mentioned (string, empty if not found)
            - position_title: Job title/position name (string)
            - key_requirements: Top 5 most important requirements (array of strings)
            
            Job Description:
            {job_description}
            
            Respond ONLY with valid JSON, no other text.
            """

            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": metadata_prompt.format(job_description=job_description),
                    }
                ],
                temperature=0.1,
                max_tokens=400,
            )

            content = response.choices[0].message.content
            if content:
                import json

                result = json.loads(content)
                logger.debug(f"Extracted metadata: {result}")
                return result
            else:
                logger.warning("Empty response from OpenAI for metadata extraction")
        except Exception as e:
            logger.error(f"Error extracting job metadata: {e}")

        # Fallback: extract basic requirements using regex
        fallback_requirements = self._extract_requirements_fallback(job_description)
        return {
            "hiring_manager": "",
            "position_title": "",
            "key_requirements": fallback_requirements,
        }

    def _extract_requirements_fallback(self, job_description: str) -> List[str]:
        """Fallback method to extract requirements using simple patterns."""
        requirements = []
        lines = job_description.split("\n")

        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["требования:", "requirements:", "требуется:", "нужно:"]
            ):
                # Extract requirements from this line and next few lines
                continue
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                # This looks like a requirement
                clean_line = line.lstrip("•-* ").strip()
                if clean_line and len(clean_line) > 3:
                    requirements.append(clean_line)
                    if len(requirements) >= 5:
                        break

        return requirements[:5]  # Return top 5

    async def generate(
        self,
        resume: str,
        job_description: str,
        company_name: str = "",
        hiring_manager: str = "",
        special_requirements: str = "",
        custom_system_prompt: Optional[str] = None,
        custom_keyword_prompt: Optional[str] = None,
    ) -> CoverLetterResult:
        """
        Generate cover letter - simplified version.
        """
        start_time = time.time()
        logger.info("Starting cover letter generation")

        try:
            # Step 1: Simple job analysis
            job_analysis = await self._analyze_job(job_description, custom_keyword_prompt)
            logger.debug(f"Job analysis completed: {len(job_analysis.keywords)} keywords found")

            # Override company name if provided
            if company_name:
                job_analysis.company_name = company_name
                logger.debug(f"Using provided company name: {company_name}")

            # Step 2: Generate cover letter
            cover_letter = await self._generate_cover_letter(
                resume,
                job_description,
                job_analysis,
                company_name,
                special_requirements,
                custom_system_prompt,
            )
            logger.info("Cover letter generated successfully")

            generation_time = time.time() - start_time

            generation_time = time.time() - start_time

            # Simple validation and metadata
            word_count = len(cover_letter.split())
            keyword_matches = sum(
                1 for kw in job_analysis.keywords if kw.lower() in cover_letter.lower()
            )

            # Simple quality score
            quality_score = 0.7  # Base score
            if 200 <= word_count <= 500:
                quality_score += 0.1
            if job_analysis.keywords and keyword_matches > 0:
                quality_score += min(keyword_matches / len(job_analysis.keywords) * 0.2, 0.2)

            metadata = {
                "word_count": word_count,
                "keywords_found": keyword_matches,
                "total_keywords": len(job_analysis.keywords),
            }

            return CoverLetterResult(
                cover_letter=cover_letter,
                quality_score=min(quality_score, 1.0),
                keywords_found=keyword_matches,
                generation_time=generation_time,
                metadata=metadata,
            )

        except OpenAIError as e:
            logger.error(f"OpenAI service error during generation: {e}")
            return await self._simple_fallback(
                resume, job_description, start_time, special_requirements
            )
        except CoverLetterGenerationError as e:
            logger.warning(f"Content generation error: {e}")
            return await self._simple_fallback(
                resume, job_description, start_time, special_requirements
            )
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            return await self._simple_fallback(
                resume, job_description, start_time, special_requirements
            )

    async def _analyze_job(
        self, job_description: str, custom_keyword_prompt: Optional[str] = None
    ) -> JobAnalysis:
        """
        Simple job analysis - extract basic info only.
        """
        logger.debug("Starting job analysis")

        # Simple keyword extraction
        try:
            keywords = await self._extract_keywords(job_description, custom_keyword_prompt)
        except CoverLetterGenerationError:
            logger.warning("Keyword extraction failed, using fallback")
            keywords = self._extract_keywords_regex(job_description)

        # Basic company name extraction
        company_name = self._extract_company_name(job_description)
        if company_name:
            logger.debug(f"Extracted company name: {company_name}")

        return JobAnalysis(
            keywords=keywords,
            company_name=company_name,
        )

    async def _extract_keywords(
        self, job_description: str, custom_prompt: Optional[str] = None
    ) -> List[str]:
        """Simple keyword extraction using OpenAI."""
        logger.debug("Extracting keywords using OpenAI")

        # Use custom prompt if provided, otherwise use default
        base_prompt = (
            custom_prompt if custom_prompt and custom_prompt.strip() else KEYWORD_EXTRACTION_PROMPT
        )
        prompt = base_prompt.format(job_description=job_description[:JOB_DESCRIPTION_PREVIEW_LIMIT])

        try:
            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=KEYWORD_EXTRACTION_MAX_TOKENS,
                temperature=KEYWORD_EXTRACTION_TEMPERATURE,
            )

            content = response.choices[0].message.content
            if content:
                # Parse keywords
                keywords = [kw.strip() for kw in content.split(",")]
                keywords = [kw for kw in keywords if kw and len(kw) > 2][:12]
                logger.debug(f"Extracted {len(keywords)} keywords via OpenAI")
                return keywords

        except OpenAIError as e:
            logger.error(f"OpenAI API error during keyword extraction: {e}")
            raise CoverLetterGenerationError(f"Failed to extract keywords: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during keyword extraction: {e}")
            raise CoverLetterGenerationError(f"Keyword extraction failed: {e}") from e

        # If we get here, content was empty or invalid
        logger.warning("OpenAI returned empty content for keyword extraction")
        raise CoverLetterGenerationError("Empty response from OpenAI")

    def _extract_keywords_regex(self, job_description: str) -> List[str]:
        """Fallback keyword extraction using regex."""
        logger.debug("Using regex fallback for keyword extraction")
        keywords = []
        text_lower = job_description.lower()

        for pattern in TECH_SKILL_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)

        result = list(set(keywords))[:8]
        logger.debug(f"Regex extraction found {len(result)} keywords")
        return result

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

    async def _generate_cover_letter(
        self,
        resume: str,
        job_description: str,
        job_analysis: JobAnalysis,
        company_name: str = "",
        special_requirements: str = "",
        custom_system_prompt: Optional[str] = None,
    ) -> str:
        """Generate cover letter using simplified prompt."""
        logger.debug("Generating cover letter content")

        # Build system prompt (use custom if provided, otherwise default)
        system_prompt = (
            custom_system_prompt
            if custom_system_prompt and custom_system_prompt.strip()
            else COVER_LETTER_SYSTEM_PROMPT
        )

        # Add keywords if available
        if job_analysis.keywords:
            keywords_text = ", ".join(job_analysis.keywords)
            system_prompt += f"\nКлючевые навыки: {keywords_text}\n"

        # Build user prompt
        prompt_parts = [
            "РЕЗЮМЕ КАНДИДАТА:",
            resume,
            "",
            "ОПИСАНИЕ ВАКАНСИИ:",
            job_description,
        ]

        # Add company name if provided
        final_company = company_name or job_analysis.company_name
        if final_company:
            prompt_parts.extend(["", f"НАЗВАНИЕ КОМПАНИИ: {final_company}"])

        # Add special requirements if provided
        if special_requirements:
            prompt_parts.extend(["", f"ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ: {special_requirements}"])

        user_prompt = "\n".join(prompt_parts)

        # Generate cover letter
        try:
            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=COVER_LETTER_MAX_TOKENS,
                temperature=COVER_LETTER_TEMPERATURE,
            )

            content = response.choices[0].message.content
            if content and len(content.split()) >= MINIMUM_COVER_LETTER_WORDS:
                logger.info("Cover letter content generated successfully")
                return content
            else:
                logger.warning("Generated cover letter is too short or empty")
                raise CoverLetterGenerationError("Generated content is too short")

        except OpenAIError as e:
            logger.error(f"OpenAI API error during cover letter generation: {e}")
            raise CoverLetterGenerationError(f"Failed to generate cover letter: {e}") from e

    async def _simple_fallback(
        self, resume: str, job_description: str, start_time: float, special_requirements: str = ""
    ) -> CoverLetterResult:
        """Ultra-simple fallback generation."""
        logger.info("Using fallback generation method")

        try:
            user_prompt = f"Резюме:\n{resume}\n\nВакансия:\n{job_description}"
            if special_requirements:
                user_prompt += f"\n\nДополнительные инструкции:\n{special_requirements}"

            response = await self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": FALLBACK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=FALLBACK_MAX_TOKENS,
                temperature=FALLBACK_TEMPERATURE,
            )

            cover_letter = response.choices[0].message.content or "Ошибка генерации"
            generation_time = time.time() - start_time
            word_count = len(cover_letter.split())

            logger.info("Fallback generation completed successfully")

            # Minimal result
            return CoverLetterResult(
                cover_letter=cover_letter,
                quality_score=0.7,
                keywords_found=0,
                generation_time=generation_time,
                metadata={"fallback_used": True, "word_count": word_count},
            )

        except Exception as e:
            logger.error(f"Fallback generation failed: {e}", exc_info=True)
            generation_time = time.time() - start_time
            return CoverLetterResult(
                cover_letter=f"Критическая ошибка: {str(e)}",
                quality_score=0.0,
                keywords_found=0,
                generation_time=generation_time,
                metadata={"error": str(e)},
            )
