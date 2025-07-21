# Lucidum

A Telegram bot that helps you create, store, and generate resumes and job application messages using the OpenAI API.

## 🧠 Features

- Store resume data (in Markdown or JSON format)
- Generate cover letters based on your resume and job description
- Integrate with OpenAI (GPT-4 / GPT-3.5)
- Simple Telegram interface via commands: `/start`, `/resume`, `/cover`

## ⚙️ Stack

- Python 3.11+
- aiogram (Telegram bot logic)
- SQLite (resume and session storage)
- OpenAI Python SDK
- Markdown (for resume structure)
- Optional: FastAPI (for webhooks or REST API)
