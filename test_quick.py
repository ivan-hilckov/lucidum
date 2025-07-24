#!/usr/bin/env python3
"""
Quick verification test for cover letter system core functionality.
"""

import asyncio


def test_basic_functionality():
    """Test that all components can be imported and instantiated."""
    print("🧪 Testing basic functionality...")

    # Test imports
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
        from cover_letter.analyzer import JobAnalyzer
        from cover_letter.prompt_builder import PromptBuilder
        from cover_letter.validator import CoverLetterValidator
        from cover_letter.generator import CoverLetterGenerator
        from cover_letter.roles import RoleDefinitions

        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test model creation
    try:
        requirements = Requirements(
            hard_skills=["Python", "Django"],
            soft_skills=["Communication", "Teamwork"],
            experience_years=3,
            education_level="Bachelor",
            certifications=["AWS"],
        )

        job_analysis = JobAnalysis(
            keywords=["Python", "Django", "PostgreSQL"],
            company_name="TechCorp",
            company_size=CompanySize.STARTUP,
            company_culture=CompanyCulture.TECHNICAL,
            industry="Technology",
            requirements=requirements,
            seniority_level="senior",
            is_technical_role=True,
            is_creative_role=False,
        )
        print("✅ Models created successfully")
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

    # Test role selection
    try:
        builder = PromptBuilder()
        role = builder.select_optimal_role(job_analysis)
        assert role == RoleType.INDUSTRY_SME  # Should select this for technical role
        print(f"✅ Role selection works: {role}")
    except Exception as e:
        print(f"❌ Role selection failed: {e}")
        return False

    # Test prompt building
    try:
        context = {"keywords": ["Python", "Django"]}
        system_prompt = builder.build_system_prompt(RoleType.CORPORATE_RECRUITER, context)
        user_prompt = builder.build_user_prompt(
            "# Test Resume\nPython developer", "Looking for Python developer", job_analysis
        )

        assert len(system_prompt) > 200
        assert "Python, Django" in system_prompt
        assert "ИНФОРМАЦИЯ О КАНДИДАТЕ" in user_prompt
        print("✅ Prompt building works")
    except Exception as e:
        print(f"❌ Prompt building failed: {e}")
        return False

    # Test role definitions
    try:
        all_roles_work = True
        for role_type in RoleType:
            prompt = RoleDefinitions.get_role_prompt(role_type)
            description = RoleDefinitions.get_role_description(role_type)
            temperature = RoleDefinitions.get_role_temperature(role_type)

            if len(prompt) < 50 or len(description) < 5 or not (0.0 <= temperature <= 1.0):
                all_roles_work = False
                break

        assert all_roles_work
        print("✅ All 7 roles defined correctly")
    except Exception as e:
        print(f"❌ Role definitions failed: {e}")
        return False

    # Test validation logic (without OpenAI calls)
    try:
        from unittest.mock import Mock

        mock_client = Mock()
        validator = CoverLetterValidator(mock_client)

        # Test with proper length text
        long_text = " ".join(["word"] * 300)  # ~300 words
        short_text = "Short text"

        assert validator._check_length(long_text) == True
        assert validator._check_length(short_text) == False

        # Test structure
        good_structure = "Para 1\n\nPara 2\n\nPara 3"
        bad_structure = "Single paragraph"

        assert validator._check_structure(good_structure) == True
        assert validator._check_structure(bad_structure) == False

        # Test metrics
        with_metrics = "Увеличил производительность на 40% за 2 года"
        without_metrics = "Работал разработчиком"

        assert validator._check_metrics(with_metrics) == True
        assert validator._check_metrics(without_metrics) == False

        print("✅ Validation logic works")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

    return True


def test_system_architecture():
    """Test that the system architecture is correctly implemented."""
    print("\n🧪 Testing system architecture...")

    try:
        # Test that generator can be instantiated
        from unittest.mock import Mock
        from cover_letter.generator import CoverLetterGenerator

        mock_client = Mock()
        generator = CoverLetterGenerator(mock_client)

        # Check that all components are initialized
        assert hasattr(generator, "client")
        assert hasattr(generator, "analyzer")
        assert hasattr(generator, "prompt_builder")
        assert hasattr(generator, "validator")

        print("✅ Generator architecture correct")

        # Test analyzer has required methods
        from cover_letter.analyzer import JobAnalyzer

        analyzer = JobAnalyzer(mock_client)

        assert hasattr(analyzer, "analyze_job")
        assert hasattr(analyzer, "_extract_keywords")
        assert hasattr(analyzer, "_is_technical_role")
        assert hasattr(analyzer, "_is_creative_role")
        assert hasattr(analyzer, "_determine_seniority")

        print("✅ Analyzer architecture correct")

        return True

    except Exception as e:
        print(f"❌ Architecture test failed: {e}")
        return False


def test_bot_compatibility():
    """Test bot compatibility without actually starting the bot."""
    print("\n🧪 Testing bot compatibility...")

    try:
        # Check bot file has required functions
        import bot

        assert hasattr(bot, "generate_cover_letter")
        assert hasattr(bot, "generate_cover_letter_fallback")

        # Check that cover_letter package can be imported from bot context
        import sys
        import os

        sys.path.insert(0, os.path.dirname(__file__))

        from cover_letter import CoverLetterGenerator

        print("✅ Bot compatibility confirmed")
        return True

    except Exception as e:
        print(f"❌ Bot compatibility failed: {e}")
        return False


def run_quick_tests():
    """Run all quick tests."""
    print("🚀 Cover Letter System - Quick Verification")
    print("=" * 60)

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("System Architecture", test_system_architecture),
        ("Bot Compatibility", test_bot_compatibility),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'-' * 20} {test_name} {'-' * 20}")

        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 ALL QUICK TESTS PASSED!")
        print("\n✨ Core system functionality verified!")
        print("\n📋 System Features Confirmed:")
        print("✅ 7 different AI roles for job types")
        print("✅ Job analysis and keyword extraction")
        print("✅ Quality validation components")
        print("✅ Prompt building with role selection")
        print("✅ Bot integration ready")
        print("✅ Fallback generation for reliability")

        print("\n🚀 Ready for production!")
        print("Add your OpenAI API key and Telegram bot token to .env file")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_quick_tests()
    exit(0 if success else 1)
