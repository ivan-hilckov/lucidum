"""
Shared test fixtures and utilities for cover letter tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def sample_resume():
    """Sample resume for testing."""
    return """
# Анна Петрова

**Senior Python Developer**

## Опыт работы

**ТехКорп**, Москва
_Senior Python Developer_
_2020 — настоящее время_

- Разработала 8 микросервисов на Django и FastAPI
- Увеличила производительность системы на 45% через оптимизацию
- Руководила командой из 5 разработчиков
- Внедрила CI/CD pipeline, сократив время деплоя на 60%

## Навыки

- **Технические:** Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes, AWS
- **Языки:** Русский (родной), Английский (C1)
"""


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
TechStart ищет Senior Python Developer

О компании:
Мы - быстрорастущий стартап в сфере fintech с командой 50+ человек.

Требования:
- 4+ года коммерческого опыта с Python
- Глубокое знание Django/FastAPI
- Опыт работы с PostgreSQL, Redis
- Знание Docker, Kubernetes
- Опыт руководства командой
- Английский язык B2+

Обязанности:
- Разработка backend сервисов
- Архитектурные решения
- Менторинг junior разработчиков
- Code review

Мы предлагаем:
- Зарплата 250-350k рублей
- Удаленная работа
- Акции компании
- Медицинская страховка
"""


@pytest.fixture
def simple_resume():
    """Simple resume for basic tests."""
    return """
# Иван Иванов

**Python Developer**

## Опыт работы

**ТехКорп**, Москва
_Python Developer_
_2020 — настоящее время_

- Разработал 3 сервиса на Django
- Увеличил производительность на 30%
- Работал с PostgreSQL и Redis

## Навыки

- Python, Django, PostgreSQL, Docker
"""


@pytest.fixture
def simple_job_description():
    """Simple job description for basic tests."""
    return """
Ищем Python Developer в стартап.

Требования:
- 2+ года опыта с Python
- Знание Django
- Опыт с базами данных

Мы молодая команда в сфере IT.
"""


class MockOpenAIResponseBuilder:
    """Helper class to build mock OpenAI responses."""

    @staticmethod
    def create_response(content: str):
        """Create a mock response with given content."""
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = content
        return response

    @staticmethod
    def create_analysis_responses():
        """Create standard analysis responses for testing."""
        return [
            # Keywords extraction
            MockOpenAIResponseBuilder.create_response(
                "Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes, команда, архитектура, микросервисы, CI/CD, backend, fintech, Senior Developer"
            ),
            # Company analysis
            MockOpenAIResponseBuilder.create_response(
                '{"name": "TechStart", "size": "small", "culture": "casual", "industry": "fintech"}'
            ),
            # Requirements extraction
            MockOpenAIResponseBuilder.create_response(
                '{"hard_skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"], "soft_skills": ["leadership", "mentoring"], "experience_years": 4, "education_level": null, "certifications": []}'
            ),
        ]

    @staticmethod
    def create_cover_letter_response():
        """Create a mock cover letter response."""
        return MockOpenAIResponseBuilder.create_response("""Уважаемая команда TechStart!

Меня заинтересовала позиция Senior Python Developer в вашей fintech компании. С 6-летним опытом коммерческой разработки на Python, я уверена, что мой профиль идеально подходит для ваших задач.

В ТехКорп я разработала 8 микросервисов на Django и FastAPI, увеличив производительность системы на 45%. Мой опыт руководства командой из 5 разработчиков и внедрения CI/CD pipeline (сокращение времени деплоя на 60%) напрямую соответствует вашим требованиям к архитектурным решениям и менторингу.

Особенно привлекает возможность работы в быстрорастущем fintech стартапе. Мой опыт создания MVP за 3 месяца в СтартапИнк показывает способность работать в динамичной среде и быстро доставлять результат.

Готова обсудить, как мой опыт с микросервисами, Kubernetes и техническим лидерством поможет TechStart достичь новых высот.

С уважением,
Анна Петрова""")


@pytest.fixture
def mock_response_builder():
    """Fixture for MockOpenAIResponseBuilder."""
    return MockOpenAIResponseBuilder
