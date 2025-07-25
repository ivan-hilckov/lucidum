import asyncio
import json
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
user_states: dict[str, str] = {}
WAITING_FOR_RESUME: str = "resume"
WAITING_FOR_JOB_DESC: str = "job_desc"


class ResumeStorageError(Exception):
    """Error related to resume storage operations."""

    pass


def load_resumes() -> dict[str, str]:
    """Load resumes from JSON file."""
    try:
        if RESUMES_FILE.exists():
            content: str = RESUMES_FILE.read_text()
            try:
                loaded_data: dict[str, str] = json.loads(content)
                logger.debug(f"Loaded {len(loaded_data)} resumes")
                return loaded_data
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error parsing resumes file: {e}")
                return {}
        return {}
    except Exception as e:
        logger.error(f"Error loading resumes: {e}")
        raise ResumeStorageError(f"Failed to load resumes: {e}") from e


def save_resumes(resumes: dict[str, str]) -> None:
    """Save resumes to JSON file."""
    try:
        _ = RESUMES_FILE.write_text(json.dumps(resumes, indent=2))
        logger.debug(f"Saved {len(resumes)} resumes")
    except Exception as e:
        logger.error(f"Error saving resumes: {e}")
        raise ResumeStorageError(f"Failed to save resumes: {e}") from e


async def download_and_validate_document(document: types.Document) -> str:
    """Download and validate document content."""
    if not document.file_name or not document.file_id:
        raise ValueError("Invalid document")

    if not document.file_name.lower().endswith(".md"):
        raise ValueError("Only .md files are accepted")

    file = await bot.get_file(document.file_id)
    if not file.file_path:
        raise ValueError("Could not get file path")

    file_content = await bot.download_file(file.file_path)
    if not file_content:
        raise ValueError("File content is empty")

    try:
        return file_content.read().decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError("File contains invalid characters") from e


async def save_user_resume(user_id: str, resume_content: str) -> None:
    """Save resume for user."""
    resumes = load_resumes()
    resumes[user_id] = resume_content
    save_resumes(resumes)


def get_user_state(user_id: str) -> str | None:
    """Get user state."""
    return user_states.get(user_id)


def set_user_state(user_id: str, state: str) -> None:
    """Set user state."""
    user_states[user_id] = state


def clear_user_state(user_id: str) -> None:
    """Clear user state."""
    user_states.pop(user_id, None)


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
    set_user_state(user_id, WAITING_FOR_RESUME)

    _ = await message.answer(
        "Please upload your resume as a .md file 📄\n(Only Markdown files are accepted)"
    )


@dp.message(Command("generate"))
async def generate_handler(message: types.Message) -> None:
    """Handle /generate command."""
    if not message.from_user:
        return

    user_id: str = str(message.from_user.id)

    try:
        resumes = load_resumes()
        if user_id not in resumes:
            _ = await message.answer("❌ Please set your resume first with /set_resume")
            return

        set_user_state(user_id, WAITING_FOR_JOB_DESC)
        _ = await message.answer("Please send the job description to generate a cover letter:")

    except ResumeStorageError:
        _ = await message.answer("❌ Error accessing resume storage. Please try again.")


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
    if get_user_state(user_id) != WAITING_FOR_RESUME:
        _ = await message.answer("❌ Please use /set_resume command first to upload your resume.")
        return

    if not document:
        _ = await message.answer("❌ Invalid document. Please try uploading again.")
        return

    try:
        resume_content = await download_and_validate_document(document)
        await save_user_resume(user_id, resume_content)
        clear_user_state(user_id)

        _ = await message.answer(
            f"✅ Resume from '{document.file_name}' saved successfully!\n"
            + "Use /generate to create cover letters."
        )

    except ValueError as e:
        _ = await message.answer(f"❌ {str(e)}")
    except ResumeStorageError:
        _ = await message.answer("❌ Error saving resume. Please try again.")
    except Exception as e:
        logger.error(f"Error processing file for user {user_id}: {e}")
        _ = await message.answer("❌ Error processing file. Please try again.")


# Handle text messages (job description only)
@dp.message()
async def text_handler(message: types.Message) -> None:
    """Handle text messages for job description."""
    if not message.from_user or not message.text:
        return

    user_id: str = str(message.from_user.id)
    text: str = message.text
    state = get_user_state(user_id)

    if state == WAITING_FOR_RESUME:
        _ = await message.answer(
            "❌ Please upload your resume as a .md file, not as text.\n"
            + "Use the document upload feature to send your .md file."
        )
        return

    if state == WAITING_FOR_JOB_DESC:
        try:
            resumes = load_resumes()
            if user_id not in resumes:
                _ = await message.answer("❌ Please set your resume first with /set_resume")
                return

            _ = await message.answer("🔄 Generating cover letter...")
            cover_letter = await generate_cover_letter(resumes[user_id], text)
            _ = await message.answer(f"📄 Your cover letter:\n\n{cover_letter}")
            clear_user_state(user_id)

        except ResumeStorageError:
            _ = await message.answer("❌ Error accessing resume storage. Please try again.")
        except Exception as e:
            logger.error(f"Cover letter generation failed for user {user_id}: {e}")
            _ = await message.answer("❌ Error generating cover letter. Please try again.")
    else:
        _ = await message.answer(
            "❌ Unknown command. Please use:\n"
            + "/set_resume - to upload your resume\n"
            + "/generate - to create a cover letter"
        )


async def generate_cover_letter(resume: str, job_description: str) -> str:
    """Generate a cover letter using simplified system."""
    logger.debug("Starting cover letter generation with CoverLetterGenerator")

    try:
        # Use simple cover letter generator
        from cover_letter import CoverLetterGenerator

        generator = CoverLetterGenerator(client)
        result = await generator.generate(resume=resume, job_description=job_description)

        # Simple response
        response_parts = [result.cover_letter]

        # Add quality info if low
        if result.quality_score < 0.8:
            logger.info(
                f"Generated cover letter with low quality score: {result.quality_score:.2f}"
            )
            response_parts.append(f"\n⚠️ Качество: {result.quality_score:.0%}")

        return "\n".join(response_parts)

    except Exception as e:
        logger.warning(f"Main generator failed, using fallback: {e}")
        # Use generator's internal fallback instead
        generator = CoverLetterGenerator(client)
        result = await generator._simple_fallback(resume, job_description, 0.0)
        return result.cover_letter


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting Lucidum bot")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
