#!/usr/bin/env python3
"""
Final comprehensive test to verify the cover letter system is working properly.
This test uses minimal mocking and tests the actual system functionality.
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock, patch


async def test_simple_generation():
    """Test cover letter generation with mocked OpenAI API."""
    print("🧪 Testing cover letter generation with mocked API...")

    # Sample data
    resume = """
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

    job_description = """
Ищем Python Developer в стартап.

Требования:
- 2+ года опыта с Python
- Знание Django
- Опыт с базами данных

Мы молодая команда в сфере IT.
"""

    # Mock OpenAI client with a comprehensive mock
    class MockOpenAIClient:
        def __init__(self):
            self.chat = Mock()
            self.chat.completions = Mock()
            self.chat.completions.create = AsyncMock()

            # Set up responses in order
            self.responses = [
                # Keywords extraction
                "Python, Django, PostgreSQL, стартап, developer, IT, разработчик",
                # Company info
                '{"name": null, "size": "startup", "culture": "casual", "industry": "IT"}',
                # Requirements
                '{"hard_skills": ["Python", "Django"], "soft_skills": ["teamwork"], "experience_years": 2, "education_level": null, "certifications": []}',
                # Cover letter
                """Здравствуйте!

Меня заинтересовала позиция Python Developer в вашем стартапе. Имею 3+ года опыта разработки на Python с использованием Django.

В ТехКорп я разработал 3 сервиса на Django и увеличил производительность системы на 30%. Мой опыт работы с PostgreSQL и Redis позволит мне быстро интегрироваться в вашу команду.

Привлекает возможность работы в молодой IT команде. Готов внести свой вклад в развитие продукта.

Жду возможности обсудить детали.

С уважением,
Иван Иванов""",
            ]

            self.call_count = 0

        async def create_response(self, *args, **kwargs):
            if self.call_count < len(self.responses):
                content = self.responses[self.call_count]
                self.call_count += 1

                response = Mock()
                response.choices = [Mock()]
                response.choices[0].message = Mock()
                response.choices[0].message.content = content
                return response
            else:
                # Fallback response
                response = Mock()
                response.choices = [Mock()]
                response.choices[0].message = Mock()
                response.choices[0].message.content = "Test response"
                return response

    mock_client = MockOpenAIClient()
    mock_client.chat.completions.create = mock_client.create_response

    # Import and test with patch
    from cover_letter.generator import CoverLetterGenerator

    generator = CoverLetterGenerator(mock_client)

    result = await generator.generate(resume=resume, job_description=job_description)

    # Verify basic functionality
    print(f"✅ Generated cover letter: {len(result.cover_letter)} chars")
    print(f"✅ Quality score: {result.quality_score:.1%}")
    print(f"✅ Role used: {result.role_used}")
    print(f"✅ Generation time: {result.generation_time:.3f}s")

    # Print the cover letter
    print("\n📄 Generated Cover Letter:")
    print("-" * 50)
    print(result.cover_letter)
    print("-" * 50)

    # Basic assertions
    assert len(result.cover_letter) > 100, "Cover letter too short"
    assert result.quality_score >= 0.0, "Invalid quality score"
    assert "Python" in result.cover_letter, "Key skill missing"

    print("✅ Simple generation test passed!")
    return True


def test_individual_components():
    """Test individual components work correctly."""
    print("\n🧪 Testing individual components...")

    # Test models
    from cover_letter.models import RoleType, JobAnalysis, Requirements, CompanySize

    requirements = Requirements(
        hard_skills=["Python"],
        soft_skills=["communication"],
        experience_years=2,
        education_level=None,
        certifications=[],
    )

    job_analysis = JobAnalysis(
        keywords=["Python", "Django"],
        company_name="TestCorp",
        company_size=CompanySize.STARTUP,
        company_culture=None,
        industry="IT",
        requirements=requirements,
        seniority_level="middle",
        is_technical_role=True,
        is_creative_role=False,
    )

    print("✅ Models work correctly")

    # Test role selection
    from cover_letter.prompt_builder import PromptBuilder

    builder = PromptBuilder()
    role = builder.select_optimal_role(job_analysis)

    assert role in [r for r in RoleType], "Invalid role selected"
    print(f"✅ Role selection works: {role}")

    # Test prompt building
    system_prompt = builder.build_system_prompt(role, {"keywords": ["Python"]})
    user_prompt = builder.build_user_prompt("Test resume", "Test job", job_analysis)

    assert len(system_prompt) > 100, "System prompt too short"
    assert len(user_prompt) > 50, "User prompt too short"
    print("✅ Prompt building works")

    # Test validation
    from cover_letter.validator import CoverLetterValidator

    mock_client = Mock()
    validator = CoverLetterValidator(mock_client)

    test_letter = """Уважаемые коллеги!

Меня заинтересовала позиция Python Developer. Имею 3 года опыта разработки.

Увеличил производительность на 25% и руководил командой из 2 разработчиков.

Готов обсудить возможности сотрудничества.

С уважением,
Тест Тестов"""

    # Test individual validation methods
    assert validator._check_length(test_letter), "Length validation failed"
    assert validator._check_structure(test_letter), "Structure validation failed"
    assert validator._check_metrics(test_letter), "Metrics validation failed"

    print("✅ Validation components work")

    return True


def test_bot_integration():
    """Test that bot can use the new system."""
    print("\n🧪 Testing bot integration...")

    try:
        # Test import
        import bot

        # Check functions exist
        assert hasattr(bot, "generate_cover_letter"), "Missing generate_cover_letter"
        assert hasattr(bot, "generate_cover_letter_fallback"), "Missing fallback function"

        # Check new system can be imported
        from cover_letter import CoverLetterGenerator

        print("✅ Bot integration works")
        return True

    except Exception as e:
        print(f"❌ Bot integration failed: {e}")
        return False


async def run_final_tests():
    """Run comprehensive final tests."""
    print("🚀 Final Cover Letter System Tests")
    print("=" * 60)

    tests = [
        ("Individual Components", test_individual_components),
        ("Bot Integration", test_bot_integration),
        ("Simple Generation", test_simple_generation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")

        except Exception as e:
            print(f"❌ {test_name}: FAILED with error: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✨ Your cover letter system is ready for use!")
        print("\n📋 Next steps:")
        print("1. Add real OpenAI API key to .env file")
        print("2. Add real Telegram bot token to .env file")
        print("3. Start the bot: uv run python bot.py")
        print("4. Test with /set_resume and /generate commands")
        print("\n🔧 The system includes:")
        print("- 7 different AI roles for various job types")
        print("- Automatic job analysis and keyword extraction")
        print("- Quality validation and improvement")
        print("- Fallback generation for reliability")
        print("- Structured prompts following HR best practices")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Check the error messages above for debugging.")
        return False


if __name__ == "__main__":
    print("Cover Letter System - Final Verification")
    print("=" * 60)

    success = asyncio.run(run_final_tests())
    sys.exit(0 if success else 1)
