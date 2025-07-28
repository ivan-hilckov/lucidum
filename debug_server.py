#!/usr/bin/env python3
"""
Debug server for testing cover letter generation prompts.
Independent of the main Telegram bot.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

from cover_letter.generator import CoverLetterGenerator
from cover_letter.prompts import (
    KEYWORD_EXTRACTION_PROMPT,
    COVER_LETTER_SYSTEM_PROMPT,
    FALLBACK_SYSTEM_PROMPT,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Cover Letter Debug Server", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

openai_client = AsyncOpenAI(api_key=openai_api_key)
generator = CoverLetterGenerator(openai_client)


class DebugRequest(BaseModel):
    """Request model for debug generation."""

    resume: str
    job_description: str
    company_name: Optional[str] = ""
    hiring_manager: Optional[str] = ""
    special_requirements: Optional[str] = ""

    # Debug options
    custom_system_prompt: Optional[str] = None
    custom_keyword_prompt: Optional[str] = None
    use_fallback: bool = False

    # Advanced options
    model_name: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.98
    max_tokens: Optional[int] = 1000


class PromptsResponse(BaseModel):
    """Response model for current prompts."""

    keyword_extraction_prompt: str
    system_prompt: str
    fallback_prompt: str


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis."""

    job_description: str


class JobAnalysisResponse(BaseModel):
    """Response model for job analysis."""

    company_name: str
    hiring_manager: str
    position_title: str
    key_requirements: list[str]
    confidence_score: float


@app.get("/", response_class=HTMLResponse)
async def get_debug_interface():
    """Serve the debug interface HTML from static files."""
    from fastapi.responses import FileResponse

    return FileResponse("static/index.html")


@app.get("/prompts", response_model=PromptsResponse)
async def get_current_prompts():
    """Get current prompts for editing."""
    return PromptsResponse(
        keyword_extraction_prompt=KEYWORD_EXTRACTION_PROMPT,
        system_prompt=COVER_LETTER_SYSTEM_PROMPT,
        fallback_prompt=FALLBACK_SYSTEM_PROMPT,
    )


@app.post("/analyze-job")
async def analyze_job_description(request: JobAnalysisRequest):
    """Analyze job description using the generator's _analyze_job method."""

    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    try:
        # Use the generator's dedicated analysis method
        analysis_result = await generator.analyze_job_only(request.job_description)

        return JobAnalysisResponse(
            company_name=analysis_result["company_name"],
            hiring_manager=analysis_result["hiring_manager"],
            position_title=analysis_result["position_title"],
            key_requirements=analysis_result["key_requirements"],
            confidence_score=analysis_result["confidence_score"],
        )

    except Exception as e:
        logger.error(f"Error analyzing job description: {e}", exc_info=True)
        # Return fallback response
        return JobAnalysisResponse(
            company_name="",
            hiring_manager="",
            position_title="",
            key_requirements=[],
            confidence_score=0.0,
        )


@app.post("/generate")
async def generate_cover_letter(request: DebugRequest):
    """Generate cover letter with optional custom prompts."""

    if not request.resume.strip():
        raise HTTPException(status_code=400, detail="Resume is required")

    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    try:
        # Pass custom prompts if provided
        result = await generator.generate(
            resume=request.resume,
            job_description=request.job_description,
            company_name=request.company_name or "",
            hiring_manager=request.hiring_manager or "",
            special_requirements=request.special_requirements or "",
            custom_system_prompt=request.custom_system_prompt,
            custom_keyword_prompt=request.custom_keyword_prompt,
        )

        return result

    except Exception as e:
        logger.error(f"Error generating cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


def run_debug_server():
    """Run the debug server."""
    print("🚀 Starting Cover Letter Debug Server...")
    print("📋 Interface available at: http://localhost:8001")
    print("⚠️  Make sure OPENAI_API_KEY is set in your .env file")
    print("🛑 Press Ctrl+C to stop")

    uvicorn.run("debug_server:app", host="127.0.0.1", port=8001, reload=True, log_level="info")


if __name__ == "__main__":
    run_debug_server()
