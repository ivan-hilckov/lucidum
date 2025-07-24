# 🧠 Lucidum — Simplified MVP Implementation Plan

## 📍 Project Goal

Create a minimal Telegram bot that helps users:

- Store a simple resume
- Generate cover letters using OpenAI API
- Quick setup and deployment

---

## 🚀 MVP Functionality (Phase 1)

### Core Commands:

- `/start` — welcome and instructions
- `/set_resume` — save resume as plain text
- `/generate` — create cover letter from job description

### MVP Requirements:

- Python 3.11+ with `aiogram` and `openai`
- [`uv`](https://github.com/astral-sh/uv) for fast dependency management
- Simple file-based storage (upgrade to DB later)
- Basic OpenAI integration
- No Docker (local development first)

---

## 🛠 Quick Start Setup

### 1. Dependencies

Install [`uv`](https://github.com/astral-sh/uv) (much faster than pip):

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project and install dependencies
uv init lucidum
cd lucidum
uv add aiogram openai python-dotenv
```

### 2. Project Structure

```
lucidum/
├── bot.py              # Main bot file (everything in one file for MVP)
├── .env                # Bot token and OpenAI key
├── pyproject.toml      # uv project configuration
├── uv.lock            # Dependency lock file
├── data/               # Simple file storage for resumes
│   └── resumes.json    # User resumes storage
└── test_data/          # Test files for functionality verification
    ├── CV.md           # Sample resume (Frontend Team Lead)
    └── VACANCY.md      # Sample job description (React Developer)
```

### 3. Environment Setup

Create `.env`:

```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

---

## 💾 Simple Data Storage

### File-based Storage (MVP)

- Store user resumes in `data/resumes.json`
- Format: `{"user_id": "resume_text"}`
- No database needed initially

Example:

```json
{
  "123456789": "John Doe\nSoftware Engineer\n5 years Python experience...",
  "987654321": "Jane Smith\nProduct Manager\n3 years at tech startups..."
}
```

---

## 🤖 Bot Logic (Single File)

### `bot.py` — All-in-one implementation:

```python
import asyncio
import json
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Data storage
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
RESUMES_FILE = DATA_DIR / "resumes.json"

def load_resumes():
    if RESUMES_FILE.exists():
        return json.loads(RESUMES_FILE.read_text())
    return {}

def save_resumes(resumes):
    RESUMES_FILE.write_text(json.dumps(resumes, indent=2))

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "🧠 Welcome to Lucidum!\n\n"
        "Commands:\n"
        "/set_resume - Save your resume\n"
        "/generate - Create cover letter"
    )

@dp.message(Command("set_resume"))
async def set_resume_handler(message: types.Message):
    await message.answer("Please send your resume as plain text:")

@dp.message(Command("generate"))
async def generate_handler(message: types.Message):
    user_id = str(message.from_user.id)
    resumes = load_resumes()

    if user_id not in resumes:
        await message.answer("❌ Please set your resume first with /set_resume")
        return

    await message.answer("Please send the job description to generate a cover letter:")

# Handle text messages (resume or job description)
@dp.message()
async def text_handler(message: types.Message):
    user_id = str(message.from_user.id)
    text = message.text

    # Simple state management (can be improved later)
    # For MVP, assume user alternates between setting resume and generating

    resumes = load_resumes()

    if user_id not in resumes:
        # Save as resume
        resumes[user_id] = text
        save_resumes(resumes)
        await message.answer("✅ Resume saved! Use /generate to create cover letters.")
    else:
        # Generate cover letter
        await message.answer("🔄 Generating cover letter...")

        try:
            cover_letter = await generate_cover_letter(resumes[user_id], text)
            await message.answer(f"📄 Your cover letter:\n\n{cover_letter}")
        except Exception as e:
            await message.answer(f"❌ Error: {str(e)}")

async def generate_cover_letter(resume: str, job_description: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a professional cover letter writer. Create concise, relevant cover letters."
            },
            {
                "role": "user",
                "content": f"Resume:\n{resume}\n\nJob Description:\n{job_description}\n\nWrite a professional cover letter:"
            }
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Bot

```bash
# Run with uv
uv run bot.py

# Or activate virtual environment and run normally
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python bot.py
```

---

## 🧪 Testing with Sample Data

The project includes test files for manual verification:

### Test Files:

- **`CV.md`** — Sample resume of Ivan Khilkov (Frontend Team Lead with 17+ years experience)
- **`VACANCY.md`** — Job posting for React Developer at Wiregate company

### Testing Workflow:

1. **Set Resume**: Copy content from `CV.md` and send it after `/set_resume` command
2. **Generate Cover Letter**: Copy job description from `VACANCY.md` and send it after `/generate` command
3. **Verify Output**: Check that the generated cover letter matches the candidate's experience with job requirements

### Example Test Scenario:

```
User: /start
Bot: 🧠 Welcome to Lucidum!...

User: /set_resume
Bot: Please send your resume as plain text:

User: [Paste content from CV.md]
Bot: ✅ Resume saved! Use /generate to create cover letters.

User: /generate
Bot: Please send the job description to generate a cover letter:

User: [Paste content from VACANCY.md]
Bot: 🔄 Generating cover letter...
Bot: 📄 Your cover letter: [Generated text highlighting React experience, leadership skills, etc.]
```

---

## 🎯 MVP Development Timeline

### Week 1: Core Bot

- [ ] Basic bot setup with commands
- [ ] File-based resume storage
- [ ] OpenAI integration
- [ ] Simple text-based interaction

### Week 2: Improvements

- [ ] Better state management
- [ ] Error handling
- [ ] Input validation
- [ ] Basic logging

### Week 3: Database Migration

- [ ] PostgreSQL setup
- [ ] Migrate from file storage
- [ ] User management

### Week 4: Deployment

- [ ] Docker containerization
- [ ] Production deployment

---

## 🔧 Next Phase Features

After MVP is working:

1. **Database Integration**:

   - PostgreSQL with proper user/resume tables
   - Multiple resume support per user

2. **Better UX**:

   - Inline keyboards
   - Command state management
   - Resume editing

3. **Advanced Features**:

   - Different cover letter styles
   - Resume templates
   - Usage analytics

4. **Production**:
   - Docker deployment (with `uv` for fast builds)
   - Error monitoring
   - Rate limiting

---

## ✅ Simplified MVP Checklist

**Essential (Must Have)**:

- [ ] `/start`, `/set_resume`, `/generate` commands working
- [ ] OpenAI API integration
- [ ] Basic file storage
- [ ] Error handling for API failures
- [ ] Manual testing with CV.md and VACANCY.md files

**Important (Should Have)**:

- [ ] Input validation
- [ ] Better user feedback
- [ ] Resume update functionality

**Nice to Have (Could Have)**:

- [ ] Logging
- [ ] Usage statistics
- [ ] Better formatting

---

## 💡 Key Simplifications from Original PRD

1. **Single file instead of multiple modules**
2. **File storage instead of PostgreSQL**
3. **No Docker for development**
4. **Simple text interaction (no inline keyboards)**
5. **Basic prompt (no template system)**
6. **No GitHub Actions**
7. **No multiple language support**

This approach gets you a working bot in hours, not days!
