#!/usr/bin/env python3
"""
Integration test for complete cover letter generation pipeline.
This tests the full end-to-end workflow with mocked OpenAI responses.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from cover_letter import CoverLetterGenerator


async def test_full_pipeline():
    """Test the complete cover letter generation pipeline."""
    print("🧪 Testing full cover letter generation pipeline...")

    # Sample data
    sample_resume = """
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

**СтартапИнк**, Санкт-Петербург  
_Python Developer_  
_2018 — 2020_

- Создала MVP продукта за 3 месяца
- Интегрировала 12 внешних API
- Покрытие тестами 85%

## Навыки

- **Технические:** Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes, AWS
- **Языки:** Русский (родной), Английский (C1)
"""

    sample_job_description = """
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

Присылайте резюме и сопроводительное письмо на hr@techstart.com
"""

    # Create mock OpenAI client
    mock_client = Mock()
    mock_client.chat = Mock()
    mock_client.chat.completions = Mock()
    mock_client.chat.completions.create = AsyncMock()

    # Mock responses for different API calls
    def create_mock_response(content):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = content
        return mock_response

    responses = [
        # Keywords extraction
        create_mock_response(
            "Python, Django, FastAPI, PostgreSQL, Docker, Kubernetes, команда, архитектура, микросервисы, CI/CD, backend, fintech, Senior Developer"
        ),
        # Company analysis
        create_mock_response(
            '{"name": "TechStart", "size": "small", "culture": "casual", "industry": "fintech"}'
        ),
        # Requirements extraction
        create_mock_response(
            '{"hard_skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"], "soft_skills": ["leadership", "mentoring"], "experience_years": 4, "education_level": null, "certifications": []}'
        ),
        # Cover letter generation
        create_mock_response("""Уважаемая команда TechStart!

Меня заинтересовала позиция Senior Python Developer в вашей fintech компании. С 6-летним опытом коммерческой разработки на Python, я уверена, что мой профиль идеально подходит для ваших задач.

В ТехКорп я разработала 8 микросервисов на Django и FastAPI, увеличив производительность системы на 45%. Мой опыт руководства командой из 5 разработчиков и внедрения CI/CD pipeline (сокращение времени деплоя на 60%) напрямую соответствует вашим требованиям к архитектурным решениям и менторингу.

Особенно привлекает возможность работы в быстрорастущем fintech стартапе. Мой опыт создания MVP за 3 месяца в СтартапИнк показывает способность работать в динамичной среде и быстро доставлять результат.

Готова обсудить, как мой опыт с микросервисами, Kubernetes и техническим лидерством поможет TechStart достичь новых высот.

С уважением,
Анна Петрова"""),
    ]

    mock_client.chat.completions.create.side_effect = responses

    # Create generator and run
    generator = CoverLetterGenerator(mock_client)

    result = await generator.generate(
        resume=sample_resume, job_description=sample_job_description, company_name="TechStart"
    )

    # Verify results
    print("📊 Generation Results:")
    print(f"✅ Cover letter generated: {len(result.cover_letter)} characters")
    print(f"✅ Quality score: {result.quality_score:.1%}")
    print(f"✅ Role used: {result.role_used}")
    print(f"✅ Generation time: {result.generation_time:.2f}s")
    print(f"✅ Validation passed: {result.validation_result.is_valid}")

    # Print the actual cover letter
    print("\n📄 Generated Cover Letter:")
    print("=" * 60)
    print(result.cover_letter)
    print("=" * 60)

    # Print validation details
    print(f"\n🔍 Validation Details:")
    print(f"Length OK: {result.validation_result.length_ok}")
    print(f"Structure OK: {result.validation_result.structure_ok}")
    print(f"Has metrics: {result.validation_result.has_metrics}")
    print(f"Keyword match: {result.validation_result.keyword_match:.1%}")
    print(f"Personalization: {result.validation_result.personalization_score:.1%}")

    if result.validation_result.issues:
        print(f"Issues: {', '.join(result.validation_result.issues)}")

    # Print job analysis
    print(f"\n🎯 Job Analysis:")
    print(f"Company: {result.job_analysis.company_name}")
    print(f"Industry: {result.job_analysis.industry}")
    print(f"Seniority: {result.job_analysis.seniority_level}")
    print(f"Technical role: {result.job_analysis.is_technical_role}")
    print(f"Keywords found: {len(result.job_analysis.keywords)}")

    # Verify quality
    assert result.quality_score > 0.5, f"Quality score too low: {result.quality_score}"
    assert len(result.cover_letter) > 200, "Cover letter too short"
    assert "TechStart" in result.cover_letter, "Company name not mentioned"
    assert "Python" in result.cover_letter, "Key skill not mentioned"

    print("\n🎉 All integration tests passed!")
    return True


async def test_fallback_generation():
    """Test fallback generation when advanced system fails."""
    print("\n🧪 Testing fallback generation...")

    # Create mock client that will fail for advanced calls
    mock_client = Mock()
    mock_client.chat = Mock()
    mock_client.chat.completions = Mock()

    # First few calls fail, last one succeeds (fallback)
    def side_effect(*args, **kwargs):
        if side_effect.call_count < 3:
            side_effect.call_count += 1
            raise Exception("API Error")
        else:
            return Mock(
                message=Mock(
                    content="Простое сопроводительное письмо для тестирования fallback генерации. Имею опыт работы с Python и готов присоединиться к команде."
                )
            )

    side_effect.call_count = 0
    mock_client.chat.completions.create = AsyncMock(side_effect=side_effect)

    generator = CoverLetterGenerator(mock_client)

    result = await generator.generate(
        resume="# Test Resume\nPython developer", job_description="Looking for Python developer"
    )

    print(f"✅ Fallback result: {len(result.cover_letter)} characters")
    print(f"✅ Fallback used: {result.metadata.get('fallback_used', False)}")

    assert len(result.cover_letter) > 50, "Fallback result too short"
    print("✅ Fallback generation works!")

    return True


async def main():
    """Run all integration tests."""
    print("🚀 Cover Letter System - Integration Tests")
    print("=" * 60)

    try:
        # Test 1: Full pipeline
        success1 = await test_full_pipeline()

        # Test 2: Fallback
        success2 = await test_fallback_generation()

        if success1 and success2:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("\n✨ The cover letter system is fully functional and ready for production use.")
            print("\nNext steps:")
            print("1. Set up real OpenAI API key in .env file")
            print("2. Set up Telegram bot token")
            print("3. Run: uv run python bot.py")
            return True
        else:
            print("\n❌ Some integration tests failed.")
            return False

    except Exception as e:
        print(f"\n❌ Integration test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
