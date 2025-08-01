# Lucidum

A Telegram bot that helps you create, store, and generate resumes and job application messages using the OpenAI API.

Lucidum is a Telegram bot that helps job seekers create professional, personalized cover letters based on their resumes and job descriptions.

It supports uploading, storing, and editing resumes in Markdown or structured format, and uses the OpenAI API to generate high-quality application texts.

The bot features a simple UX with inline buttons, secure data storage in PostgreSQL, and a production-ready architecture with Docker and GitHub Actions.

Lucidum is designed to streamline the job application process and make high-impact writing accessible with minimal user input.

## 🧠 Features

- Store resume data (text input or upload .md files)
- Generate cover letters based on your resume and job description
- Integrate with OpenAI (GPT-4 / GPT-3.5)
- Simple Telegram interface via commands: `/start`, `/set_resume`, `/generate`

### Resume Input Options

- **Text Input**: Type your resume directly in the chat
- **File Upload**: Upload a .md (Markdown) file containing your resume

## ⚙️ Stack

- Python 3.11+
- aiogram (Telegram bot logic)
- postgres (resume and session storage)
- OpenAI Python SDK
- Markdown (for resume structure)
