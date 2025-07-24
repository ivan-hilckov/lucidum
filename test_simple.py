#!/usr/bin/env python3
"""
Simple test script to verify cover letter system works.
Run this script to test basic functionality without external dependencies.
"""

import sys
import asyncio
from unittest.mock import Mock, AsyncMock


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")

    try:
        from cover_letter.models import (
            RoleType,
            CompanySize,
            CompanyCulture,
            Requirements,
            JobAnalysis,
            ValidationResult,
            CoverLetterResult,
        )

        print("✅ Models imported successfully")

        from cover_letter.analyzer import JobAnalyzer

        print("✅ JobAnalyzer imported successfully")

        from cover_letter.prompt_builder import PromptBuilder

        print("✅ PromptBuilder imported successfully")

        from cover_letter.validator import CoverLetterValidator

        print("✅ CoverLetterValidator imported successfully")

        from cover_letter.generator import CoverLetterGenerator

        print("✅ CoverLetterGenerator imported successfully")

        from cover_letter.roles import RoleDefinitions

        print("✅ RoleDefinitions imported successfully")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_models():
    """Test model creation and basic functionality."""
    print("\n🧪 Testing models...")

    try:
        from cover_letter.models import (
            RoleType,
            CompanySize,
            CompanyCulture,
            Requirements,
            JobAnalysis,
            ValidationResult,
        )

        # Test Requirements
        requirements = Requirements(
            hard_skills=["Python", "Django"],
            soft_skills=["Communication"],
            experience_years=3,
            education_level="Bachelor",
            certifications=["AWS"],
        )
        assert len(requirements.hard_skills) == 2
        print("✅ Requirements model works")

        # Test JobAnalysis
        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TestCorp",
            company_size=CompanySize.STARTUP,
            company_culture=CompanyCulture.TECHNICAL,
            industry="Technology",
            requirements=requirements,
            seniority_level="senior",
            is_technical_role=True,
            is_creative_role=False,
        )
        assert job_analysis.company_name == "TestCorp"
        assert job_analysis.is_technical_role == True
        print("✅ JobAnalysis model works")

        # Test enums
        assert RoleType.CORPORATE_RECRUITER.value == "corporate_recruiter"
        assert CompanySize.STARTUP.value == "startup"
        print("✅ Enums work correctly")

        return True

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def test_role_definitions():
    """Test role definitions and prompts."""
    print("\n🧪 Testing role definitions...")

    try:
        from cover_letter.roles import RoleDefinitions
        from cover_letter.models import RoleType

        # Test role prompt retrieval
        prompt = RoleDefinitions.get_role_prompt(RoleType.CORPORATE_RECRUITER)
        assert len(prompt) > 100
        assert "рекрутер" in prompt.lower()
        print("✅ Role prompts work")

        # Test role description
        description = RoleDefinitions.get_role_description(RoleType.CORPORATE_RECRUITER)
        assert len(description) > 10
        print("✅ Role descriptions work")

        # Test temperature
        temp = RoleDefinitions.get_role_temperature(RoleType.CORPORATE_RECRUITER)
        assert 0.0 <= temp <= 1.0
        print("✅ Role temperatures work")

        return True

    except Exception as e:
        print(f"❌ Role definitions test failed: {e}")
        return False


def test_prompt_builder():
    """Test prompt builder functionality."""
    print("\n🧪 Testing prompt builder...")

    try:
        from cover_letter.prompt_builder import PromptBuilder
        from cover_letter.models import (
            JobAnalysis,
            CompanySize,
            CompanyCulture,
            Requirements,
            RoleType,
        )

        builder = PromptBuilder()

        # Create test job analysis
        job_analysis = JobAnalysis(
            keywords=["Python", "Django"],
            company_name="TechCorp",
            company_size=CompanySize.MEDIUM,
            company_culture=CompanyCulture.TECHNICAL,
            industry="Technology",
            requirements=Requirements([], [], None, None, []),
            seniority_level="senior",
            is_technical_role=True,
            is_creative_role=False,
        )

        # Test role selection
        role = builder.select_optimal_role(job_analysis)
        assert isinstance(role, RoleType)
        print(f"✅ Role selection works: {role}")

        # Test system prompt building
        context = {"keywords": ["Python", "Django"]}
        system_prompt = builder.build_system_prompt(RoleType.CORPORATE_RECRUITER, context)
        assert len(system_prompt) > 200
        assert "КРИТЕРИИ КАЧЕСТВА" in system_prompt
        print("✅ System prompt building works")

        # Test user prompt building
        resume = "# Test Resume\nPython developer with 3 years experience"
        job_desc = "Looking for Python developer"
        user_prompt = builder.build_user_prompt(resume, job_desc, job_analysis)
        assert "ИНФОРМАЦИЯ О КАНДИДАТЕ" in user_prompt
        assert resume in user_prompt
        print("✅ User prompt building works")

        return True

    except Exception as e:
        print(f"❌ Prompt builder test failed: {e}")
        return False


def test_validator():
    """Test validator functionality."""
    print("\n🧪 Testing validator...")

    try:
        from cover_letter.validator import CoverLetterValidator

        # Create mock client
        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock()

        validator = CoverLetterValidator(mock_client)

        # Test length check
        short_text = "Короткий текст"
        good_text = " ".join(["слово"] * 300)
        long_text = " ".join(["слово"] * 500)

        assert validator._check_length(short_text) == False
        assert validator._check_length(good_text) == True
        assert validator._check_length(long_text) == False
        print("✅ Length validation works")

        # Test structure check
        bad_structure = "Один абзац"
        good_structure = "Первый\n\nВторой\n\nТретий"

        assert validator._check_structure(bad_structure) == False
        assert validator._check_structure(good_structure) == True
        print("✅ Structure validation works")

        # Test metrics check
        no_metrics = "Работал программистом"
        with_metrics = "Увеличил производительность на 40% за 2 года"

        assert validator._check_metrics(no_metrics) == False
        assert validator._check_metrics(with_metrics) == True
        print("✅ Metrics validation works")

        # Test keyword check
        text = "Использую Python и Django"
        keywords = ["Python", "Django", "React"]
        match_ratio = validator._check_keywords(text, keywords)
        assert abs(match_ratio - 2 / 3) < 0.01
        print("✅ Keyword validation works")

        return True

    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


async def test_analyzer():
    """Test analyzer functionality."""
    print("\n🧪 Testing analyzer...")

    try:
        from cover_letter.analyzer import JobAnalyzer

        # Create mock client
        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock()

        analyzer = JobAnalyzer(mock_client)

        # Test technical role detection
        tech_desc = "Looking for Python developer with Django experience"
        non_tech_desc = "Looking for marketing manager"

        assert analyzer._is_technical_role(tech_desc) == True
        assert analyzer._is_technical_role(non_tech_desc) == False
        print("✅ Technical role detection works")

        # Test creative role detection
        creative_desc = "Looking for UI designer"
        non_creative_desc = "Looking for Python developer"

        assert analyzer._is_creative_role(creative_desc) == True
        assert analyzer._is_creative_role(non_creative_desc) == False
        print("✅ Creative role detection works")

        # Test seniority detection
        senior_desc = "Senior Python Developer"
        junior_desc = "Junior Developer position"

        assert analyzer._determine_seniority(senior_desc) == "senior"
        assert analyzer._determine_seniority(junior_desc) == "junior"
        print("✅ Seniority detection works")

        return True

    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False


def test_bot_integration():
    """Test bot integration."""
    print("\n🧪 Testing bot integration...")

    try:
        # Test import in bot context
        import bot

        # Check if the new function is there
        assert hasattr(bot, "generate_cover_letter")
        assert hasattr(bot, "generate_cover_letter_fallback")
        print("✅ Bot has new functions")

        # Check if imports work
        from cover_letter import CoverLetterGenerator

        print("✅ Bot can import CoverLetterGenerator")

        return True

    except Exception as e:
        print(f"❌ Bot integration test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting comprehensive cover letter system tests\n")

    tests = [
        ("Imports", test_imports),
        ("Models", test_models),
        ("Role Definitions", test_role_definitions),
        ("Prompt Builder", test_prompt_builder),
        ("Validator", test_validator),
        ("Analyzer", test_analyzer),
        ("Bot Integration", test_bot_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"=" * 50)
        print(f"Running {test_name} tests")
        print("=" * 50)

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
                print(f"✅ {test_name} tests PASSED")
            else:
                print(f"❌ {test_name} tests FAILED")

        except Exception as e:
            print(f"❌ {test_name} tests FAILED with exception: {e}")

        print()

    print("=" * 50)
    print(f"FINAL RESULTS: {passed}/{total} test suites passed")
    print("=" * 50)

    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
        return True
    else:
        print(f"⚠️  {total - passed} test suite(s) failed. Check the issues above.")
        return False


if __name__ == "__main__":
    print("Cover Letter System - Simple Test Suite")
    print("=" * 50)

    success = asyncio.run(run_all_tests())

    if success:
        print("\n🎯 Quick usage example:")
        print("python3 -c \"from cover_letter.models import RoleType; print('System ready!')\"")
        sys.exit(0)
    else:
        sys.exit(1)
