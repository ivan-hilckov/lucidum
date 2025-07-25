"""
Prompts and constants for cover letter generation.
"""

# Keyword extraction prompt
KEYWORD_EXTRACTION_PROMPT = """
Извлеки 8-12 ключевых навыков и технологий из описания вакансии.
Верни только список через запятую, без объяснений.

Описание вакансии:
{job_description}
"""

# Main cover letter generation system prompt
COVER_LETTER_SYSTEM_PROMPT = """
РОЛЬ: Ты - опытный корпоративный рекрутер, который пишет сопроводительные письма для отклика на вакансии.

Создай профессиональное сопроводительное письмо на русском языке.

КРИТЕРИИ КАЧЕСТВА:
- Длина: 250-350 слов
- Структура: Приветствие + 2 абзаца с достижениями + Заключение
- Используй в качестве примеров работ те позиции в которых специалист работал дольше всего
- Используй в качестве примеров работ те позиции из резюме которые наиболее близки к вакансии
- Включи 2-3 конкретных достижения с цифрами из резюме
- Используй навыки из описания вакансии
- Тон: уверенный, профессиональный

ИЗБЕГАЙ:
- Общих фраз
- Повторения резюме
- Лишних эмоций
- Упоминания зарплаты
"""

# Combined fallback prompt - replaces both old fallback prompts
FALLBACK_SYSTEM_PROMPT = """
Создай профессиональное сопроводительное письмо на русском языке.
Используй реальный опыт и навыки из резюме, упомяни подходящие навыки для вакансии.
Длина: 250-350 слов. Тон: профессиональный, уверенный.
"""

# Simple regex patterns for keyword extraction fallback
TECH_SKILL_PATTERNS = [
    r"\b(?:python|javascript|react|vue|angular|django|flask)\b",
    r"\b(?:sql|mysql|postgresql|mongodb|redis)\b",
    r"\b(?:git|docker|aws|azure|kubernetes)\b",
    r"\b(?:html|css|typescript|node\.?js)\b",
]

# OpenAI model configuration
DEFAULT_MODEL = "gpt-4o-mini"
KEYWORD_EXTRACTION_TEMPERATURE = 0.1
COVER_LETTER_TEMPERATURE = 0.3
FALLBACK_TEMPERATURE = 0.5

# Token limits
KEYWORD_EXTRACTION_MAX_TOKENS = 150
COVER_LETTER_MAX_TOKENS = 600
FALLBACK_MAX_TOKENS = 500


# Content limits
JOB_DESCRIPTION_PREVIEW_LIMIT = 1000
MINIMUM_COVER_LETTER_WORDS = 50
