import asyncio
import json
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from dotenv import load_dotenv
from openai import AsyncOpenAI

_ = load_dotenv()

# Initialize
bot_token: str | None = os.getenv("BOT_TOKEN")
if not bot_token:
    raise ValueError("BOT_TOKEN environment variable is required")

openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

bot: Bot = Bot(token=bot_token)
dp: Dispatcher = Dispatcher()
client: AsyncOpenAI = AsyncOpenAI(api_key=openai_api_key)

# Data storage
DATA_DIR: Path = Path("data")
DATA_DIR.mkdir(exist_ok=True)
RESUMES_FILE: Path = DATA_DIR / "resumes.json"

# Simple state management
user_states: dict[str, str] = {}  # user_id -> state
WAITING_FOR_RESUME: str = "waiting_for_resume"
WAITING_FOR_JOB_DESC: str = "waiting_for_job_desc"


def load_resumes() -> dict[str, str]:
    """Load resumes from JSON file."""
    if RESUMES_FILE.exists():
        content: str = RESUMES_FILE.read_text()
        try:
            loaded_data: dict[str, str] = json.loads(content)
            return loaded_data
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def save_resumes(resumes: dict[str, str]) -> None:
    """Save resumes to JSON file."""
    _ = RESUMES_FILE.write_text(json.dumps(resumes, indent=2))


@dp.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    """Handle /start command."""
    _ = await message.answer(
        "🧠 Welcome to Lucidum!\n\n"
        "Commands:\n"
        "/set_resume - Save your resume (MD file only)\n"
        "/generate - Create cover letter"
    )


@dp.message(Command("set_resume"))
async def set_resume_handler(message: types.Message) -> None:
    """Handle /set_resume command."""
    if not message.from_user:
        return

    user_id: str = str(message.from_user.id)
    user_states[user_id] = WAITING_FOR_RESUME

    _ = await message.answer(
        "Please upload your resume as a .md file 📄\n(Only Markdown files are accepted)"
    )


@dp.message(Command("generate"))
async def generate_handler(message: types.Message) -> None:
    """Handle /generate command."""
    if not message.from_user:
        return

    user_id: str = str(message.from_user.id)
    resumes: dict[str, str] = load_resumes()

    if user_id not in resumes:
        _ = await message.answer("❌ Please set your resume first with /set_resume")
        return

    user_states[user_id] = WAITING_FOR_JOB_DESC
    _ = await message.answer("Please send the job description to generate a cover letter:")


# Handle document uploads
def is_document_message(message: types.Message) -> bool:
    """Check if message contains a document."""
    return message.content_type == ContentType.DOCUMENT


@dp.message(is_document_message)
async def document_handler(message: types.Message) -> None:
    """Handle document uploads for resume."""
    if not message.from_user:
        return

    user_id: str = str(message.from_user.id)
    document = message.document

    # Check user state
    if user_states.get(user_id) != WAITING_FOR_RESUME:
        _ = await message.answer("❌ Please use /set_resume command first to upload your resume.")
        return

    # Check if document exists and has required attributes
    if not document or not document.file_name or not document.file_id:
        _ = await message.answer("❌ Invalid document. Please try uploading again.")
        return

    # Check if it's a markdown file
    if not document.file_name.lower().endswith(".md"):
        _ = await message.answer("❌ Please upload only .md (Markdown) files for your resume.")
        return

    try:
        # Download the file
        file = await bot.get_file(document.file_id)
        if not file.file_path:
            _ = await message.answer("❌ Error: Could not download file.")
            return

        file_content = await bot.download_file(file.file_path)
        if not file_content:
            _ = await message.answer("❌ Error: File content is empty.")
            return

        # Read the content as text
        resume_content: str = file_content.read().decode("utf-8")

        # Save the resume
        resumes: dict[str, str] = load_resumes()
        resumes[user_id] = resume_content
        save_resumes(resumes)

        # Clear user state
        _ = user_states.pop(user_id, None)

        _ = await message.answer(
            f"✅ Resume from '{document.file_name}' saved successfully!\n"
            + "Use /generate to create cover letters."
        )

    except Exception as e:
        _ = await message.answer(f"❌ Error processing file: {str(e)}")


# Handle text messages (job description only)
@dp.message()
async def text_handler(message: types.Message) -> None:
    """Handle text messages for job description."""
    if not message.from_user or not message.text:
        return

    user_id: str = str(message.from_user.id)
    text: str = message.text

    # Check user state
    if user_states.get(user_id) == WAITING_FOR_RESUME:
        _ = await message.answer(
            "❌ Please upload your resume as a .md file, not as text.\n"
            + "Use the document upload feature to send your .md file."
        )
        return

    if user_states.get(user_id) == WAITING_FOR_JOB_DESC:
        # Generate cover letter
        resumes: dict[str, str] = load_resumes()

        if user_id not in resumes:
            _ = await message.answer("❌ Please set your resume first with /set_resume")
            return

        _ = await message.answer("🔄 Generating cover letter...")

        try:
            cover_letter: str = await generate_cover_letter(resumes[user_id], text)
            _ = await message.answer(f"📄 Your cover letter:\n\n{cover_letter}")
            # Clear user state
            _ = user_states.pop(user_id, None)
        except Exception as e:
            _ = await message.answer(f"❌ Error: {str(e)}")
    else:
        _ = await message.answer(
            "❌ Unknown command. Please use:\n"
            + "/set_resume - to upload your resume\n"
            + "/generate - to create a cover letter"
        )


async def generate_cover_letter(resume: str, job_description: str) -> str:
    """Generate a cover letter using advanced OpenAI API with analysis and validation."""
    try:
        # Use new advanced cover letter generator
        from cover_letter import CoverLetterGenerator

        generator = CoverLetterGenerator(client)
        result = await generator.generate(resume=resume, job_description=job_description)

        # Prepare response with quality information
        response_parts = [result.cover_letter]

        # Add quality feedback if score is below threshold
        if result.quality_score < 0.8:
            response_parts.append(f"\n⚠️ Качество: {result.quality_score:.1%}")
            if result.validation_result.issues:
                response_parts.append(
                    f"Рекомендации: {', '.join(result.validation_result.suggestions[:2])}"
                )

        # Add metadata for debugging (can be removed in production)
        if result.metadata.get("role_description"):
            response_parts.append(f"\n🤖 Роль: {result.metadata['role_description']}")

        return "\n".join(response_parts)

    except Exception as e:
        # Fallback to simple generation if new system fails
        print(f"Advanced generation failed, using fallback: {e}")
        return await generate_cover_letter_fallback(resume, job_description)


async def generate_cover_letter_fallback(resume: str, job_description: str) -> str:
    """Fallback cover letter generation (original simple method)."""
    try:
        system_prompt = """
        You are a professional cover letter writer. Create concise, relevant cover letters
        in Russian language. Base the cover letter strictly on the real experience and skills mentioned
        in the provided resume.
        """

        user_prompt = f"""
        Resume:
        {resume}

        Job Description:
        {job_description}
        """

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1500,
            temperature=0.5,
        )

        content: str | None = response.choices[0].message.content
        return content if content else "Error: Empty response from OpenAI"

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


async def main() -> None:
    """Main function to start the bot."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
