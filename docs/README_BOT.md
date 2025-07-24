# Lucidum Telegram Bot

A Telegram bot that helps you create, store, and generate resumes and job application messages using the OpenAI API.

## 🧠 Features

- **Resume Storage**: Store your resume data with two input methods:
  - Text input: Type your resume directly in the chat
  - File upload: Upload a .md (Markdown) file containing your resume
- **Cover Letter Generation**: Generate personalized cover letters based on your resume and job descriptions
- **OpenAI Integration**: Powered by GPT-4 for high-quality text generation
- **Simple Interface**: Easy-to-use Telegram commands

## 🚀 Commands

- `/start` - Welcome message and command overview
- `/set_resume` - Set your resume (text input or upload .md file)
- `/generate` - Generate a cover letter (requires job description)

## 📝 Usage

### Setting Up Your Resume

#### Method 1: Text Input

1. Send `/set_resume`
2. Type or paste your resume as plain text

#### Method 2: File Upload

1. Send `/set_resume`
2. Upload a `.md` file containing your resume

### Generating Cover Letters

1. Send `/generate`
2. Send the job description as text
3. Receive your personalized cover letter

## 📄 Resume Format (MD File)

Your markdown resume should include:

```markdown
# Your Name

**Your Title/Position**

**Contact Information:**

- Email: your.email@example.com
- Phone: +1234567890
- LinkedIn: linkedin.com/in/yourprofile

## Experience

**Company Name**, Location
_Position Title_
_Start Date — End Date_

- Achievement or responsibility
- Another achievement with metrics
- Key skills or technologies used

## Skills

- **Technical:** List your technical skills
- **Languages:** Language proficiency levels

## Education

**University Name**, Location
_Degree and Field of Study_
_Graduation Year_
```

## ⚙️ Requirements

- Python 3.11+
- aiogram
- OpenAI API key
- Telegram Bot Token

## 🔧 Environment Variables

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

## 📦 Installation

1. Clone the repository
2. Install dependencies: `uv sync`
3. Set environment variables
4. Run: `python bot.py`
