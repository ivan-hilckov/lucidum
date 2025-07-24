"""
Tests for role definitions.
"""

import pytest
from cover_letter.roles import RoleDefinitions
from cover_letter.models import RoleType


class TestRoleDefinitions:
    """Test RoleDefinitions functionality."""

    def test_get_role_prompt_for_all_roles(self):
        """Test that all roles have prompts defined."""
        for role_type in RoleType:
            prompt = RoleDefinitions.get_role_prompt(role_type)
            assert isinstance(prompt, str)
            assert len(prompt) > 100, f"Role {role_type} has too short prompt"

    def test_get_role_description_for_all_roles(self):
        """Test that all roles have descriptions defined."""
        for role_type in RoleType:
            description = RoleDefinitions.get_role_description(role_type)
            assert isinstance(description, str)
            assert len(description) > 5, f"Role {role_type} has too short description"

    def test_get_role_temperature_for_all_roles(self):
        """Test that all roles have valid temperatures."""
        for role_type in RoleType:
            temperature = RoleDefinitions.get_role_temperature(role_type)
            assert isinstance(temperature, float)
            assert 0.0 <= temperature <= 1.0, (
                f"Role {role_type} has invalid temperature {temperature}"
            )

    def test_corporate_recruiter_specifics(self):
        """Test specific values for CORPORATE_RECRUITER role."""
        role = RoleType.CORPORATE_RECRUITER

        prompt = RoleDefinitions.get_role_prompt(role)
        description = RoleDefinitions.get_role_description(role)
        temperature = RoleDefinitions.get_role_temperature(role)

        # Check content
        assert "корпоративный рекрутер" in prompt.lower()
        assert "опытный корпоративный рекрутер" in description.lower()
        assert temperature == 0.3  # Should be conservative

    def test_different_roles_have_different_content(self):
        """Test that different roles have different prompts."""
        roles_to_test = list(RoleType)[:3]  # Test first 3 roles

        prompts = []
        descriptions = []

        for role in roles_to_test:
            prompts.append(RoleDefinitions.get_role_prompt(role))
            descriptions.append(RoleDefinitions.get_role_description(role))

        # All prompts should be different
        assert len(set(prompts)) == len(prompts), "Some roles have identical prompts"
        # All descriptions should be different
        assert len(set(descriptions)) == len(descriptions), "Some roles have identical descriptions"

    def test_role_prompt_structure(self):
        """Test that role prompts have proper structure."""
        for role_type in RoleType:
            prompt = RoleDefinitions.get_role_prompt(role_type)

            # Should contain common elements
            assert "РОЛЬ" in prompt
            assert "КРИТЕРИИ КАЧЕСТВА" in prompt
            # Should be in Russian
            assert any(char in prompt for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя")

    def test_temperature_ranges_make_sense(self):
        """Test that temperatures are in reasonable ranges."""
        temperatures = []
        for role_type in RoleType:
            temp = RoleDefinitions.get_role_temperature(role_type)
            temperatures.append(temp)

        # Should have variety in temperatures
        min_temp = min(temperatures)
        max_temp = max(temperatures)

        assert min_temp >= 0.1, "Minimum temperature too low"
        assert max_temp <= 0.8, "Maximum temperature too high"
        assert max_temp - min_temp >= 0.1, "Not enough temperature variety"
