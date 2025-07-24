# Tests

Организованная структура тестов для системы генерации сопроводительных писем.

## Структура

```
tests/
├── conftest.py                     # Общие фикстуры и утилиты
└── test_cover_letter/
    ├── test_basic.py              # Базовые smoke тесты
    ├── test_models.py             # Тесты моделей данных
    ├── test_analyzer.py           # Тесты анализатора вакансий
    ├── test_prompt_builder.py     # Тесты построителя промптов
    ├── test_roles.py              # Тесты определений ролей
    └── test_integration.py        # Интеграционные тесты
```

## Запуск тестов

```bash
# Все тесты
make test

# Только smoke тесты
pytest tests/test_cover_letter/test_basic.py -v

# Конкретный компонент
pytest tests/test_cover_letter/test_models.py -v

# С coverage
pytest tests/ --cov=cover_letter --cov-report=html
```

## Типы тестов

- **Smoke тесты** (`test_basic.py`) - базовая проверка импортов и создания объектов
- **Unit тесты** (`test_models.py`, `test_analyzer.py`, etc.) - тестирование отдельных компонентов
- **Интеграционные тесты** (`test_integration.py`) - тестирование полного flow генерации

## Фикстуры

Общие фикстуры определены в `conftest.py`:

- `mock_openai_client` - мок OpenAI клиента
- `sample_resume` / `simple_resume` - тестовые резюме
- `sample_job_description` / `simple_job_description` - тестовые вакансии
- `mock_response_builder` - утилита для создания мок ответов
