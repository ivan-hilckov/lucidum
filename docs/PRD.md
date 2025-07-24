# 🧠 Lucidum — Implementation Plan for the Telegram Bot for Resume and Cover Letter Generation

## 📍 Project Goal

Create a Telegram bot that helps users:

- Save and edit resumes
- Generate cover letters for job applications
- Use OpenAI API to generate relevant texts

---

## 🚀 MVP Functionality

### Main Bot Commands:

- `/start` — welcome message and explanation
- `/resume` — upload or create a resume
- `/cover` — generate a cover letter for a vacancy

### Minimum Requirements:

- Python library: `aiogram`
- Storage: PostgreSQL (`asyncpg`) with resume in JSON or Markdown
- Text generation: OpenAI API (ChatCompletion)
- Simple UX (reply buttons, hints)
- Docker deployment

---

## 🧩 Architecture

### Components:

1. `bot.py` — entry point, command registration and bot launch
2. `handlers.py` — logic for handling `/start`, `/resume`, `/cover`
3. `openai_service.py` — functions for prompt building and text generation
4. `db.py` — PostgreSQL interaction (using `asyncpg`)
5. `models.py` — Pydantic models for resume, cover, user
6. `prompts.py` — instruction templates and examples for generation
7. `utils.py` — helper functions (e.g., formatting, validation)
8. `.env` — configuration: bot token, OpenAI key, database URL

---

## 🛠 Technical Steps

### 1. Environment Setup

- Install dependencies using [`uv`](https://github.com/astral-sh/uv):
  ```bash
  uv pip install aiogram openai asyncpg pydantic python-dotenv
  ```
- Setup `.env` with required keys:
  - `BOT_TOKEN=...`
  - `OPENAI_API_KEY=...`
  - `DATABASE_URL=postgresql://user:pass@host/dbname`

### 2. Project Structure

```bash
lucidum/
├── bot.py               # Entry point
├── handlers.py          # Bot command logic
├── openai_service.py    # Prompt building and text generation
├── db.py                # PostgreSQL logic (asyncpg)
├── models.py            # Pydantic schemas
├── prompts.py           # Prompt templates
├── utils.py             # Helper functions
├── .env                 # Secrets and config
└── Dockerfile           # Deployment
```

### 3. Command Logic

#### `/start`

- Greeting message
- Buttons: `/resume`, `/cover`

#### `/resume`

- Check if resume exists
- Ask for Markdown file or structured input
- Save to database

#### `/cover`

- Ask for job description text
- Optional: language, style, highlights
- Generate with OpenAI
- Send result to user, with save/share options

---

## 🧪 Data Storage

### PostgreSQL Table Structure:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  tg_id BIGINT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE resumes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  content JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE covers (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  vacancy_text TEXT NOT NULL,
  result TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

- Resume content is stored as `JSONB` for easier querying and future flexibility.
- `TIMESTAMPTZ` ensures proper time zone handling.

---

## 📦 Docker & Deployment

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install --system

COPY . .

CMD ["python", "bot.py"]
```

> Uses [`uv`](https://github.com/astral-sh/uv) instead of `pip install -r requirements.txt` for faster, cache-friendly dependency installation.

---

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  bot:
    build: .
    env_file: .env
    command: ["python", "bot.py"]
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: lucidum
      POSTGRES_USER: lucidum
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always

volumes:
  pgdata:
```

> The bot container depends on PostgreSQL and will automatically restart on failure.

---

### `.env` example

```
BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://lucidum:secret@db/lucidum
```

---

### GitHub Actions: `deploy.yml`

```yaml
name: Deploy Lucidum Bot

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: yourdockerhub/lucidum:latest

      # Optional: deploy step (SSH + docker-compose on your server)
```

> For production deployment, you can either push to a Docker registry and pull from your server, or use platforms like Railway, Render, or Fly.io.

---

---

## 🧠 OpenAI API Integration

Lucidum uses OpenAI's `chat/completions` endpoint to generate cover letters based on user resumes and job descriptions.

### Key Concepts:

- [ChatCompletion API docs](https://platform.openai.com/docs/guides/gpt/chat-completions)
- The prompt is built as a sequence of messages with roles: `system`, `user`, and `assistant`.
- Contextual information (resume, job description, style) is injected into the prompt dynamically.

---

### Example: Prompt Structure

```python
messages = [
    {
        "role": "system",
        "content": "You are an assistant that writes professional cover letters for job seekers. Be concise, clear, and relevant."
    },
    {
        "role": "user",
        "content": (
            "Here is the resume:\n" + resume_text +
            "\n\nHere is the job description:\n" + vacancy_text +
            "\n\nPlease write a tailored cover letter."
        )
    }
]
```

The resulting API call:

```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.7,
    max_tokens=800
)
```

---

### Prompt Templates

- Stored in `prompts.py` or `prompts/` directory.
- Template variations may include:
  - Language (EN, RU)
  - Tone (formal, friendly, technical)
  - Highlights (user-specified skills to emphasize)

Templates are filled using `.format()` or f-strings before being sent to the model.

---

### Model Tuning Parameters

| Parameter           | Description                                         | Suggested Value           |
| ------------------- | --------------------------------------------------- | ------------------------- |
| `temperature`       | Controls creativity (0 = deterministic, 1 = random) | `0.5 – 0.8`               |
| `max_tokens`        | Maximum length of the generated text                | `600 – 1000`              |
| `top_p`             | Controls nucleus sampling                           | Optional (default: `1.0`) |
| `frequency_penalty` | Penalizes repeated phrases                          | Optional                  |

Example:

```python
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    temperature=0.6,
    max_tokens=800,
    frequency_penalty=0.1
)
```

> See also: [OpenAI Cookbook](https://github.com/openai/openai-cookbook) for advanced usage examples.

---

## ✅ MVP Checklist

- [ ] `/start` command with welcome message and inline buttons
- [ ] Resume upload or creation via `/resume`
- [ ] Cover letter generation via `/cover` using OpenAI API
- [ ] PostgreSQL database (asyncpg)
- [ ] Prompt templating and ChatCompletion integration
- [ ] Docker container with `uv`-based install
- [ ] `docker-compose` with Postgres service
- [ ] GitHub Actions CI for Docker build and deploy
- [ ] Basic UX with reply buttons and input hints
