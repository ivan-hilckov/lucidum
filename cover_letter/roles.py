from typing import Dict, Any

from .models import RoleType


class RoleDefinitions:
    """Simple role definitions - only CORPORATE_RECRUITER."""

    ROLES: Dict[RoleType, Dict[str, Any]] = {
        RoleType.CORPORATE_RECRUITER: {
            "description": "опытный HR-специалист",
            "prompt": """
Ты - опытный HR-специалист, который пишет сопроводительные письма для отклика на вакансии.

Создай профессиональное сопроводительное письмо на русском языке.

ТРЕБОВАНИЯ:
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
            """,
            "temperature": 0.8,
            "best_for": ["general", "corporate", "all_types"],
        },
    }

    @classmethod
    def get_role_prompt(cls, role_type: RoleType) -> str:
        """Get the prompt for CORPORATE_RECRUITER."""
        return cls.ROLES[RoleType.CORPORATE_RECRUITER]["prompt"]

    @classmethod
    def get_role_description(cls, role_type: RoleType) -> str:
        """Get the description for CORPORATE_RECRUITER."""
        return cls.ROLES[RoleType.CORPORATE_RECRUITER]["description"]

    @classmethod
    def get_role_temperature(cls, role_type: RoleType) -> float:
        """Get temperature - always 0.3."""
        return 0.3
