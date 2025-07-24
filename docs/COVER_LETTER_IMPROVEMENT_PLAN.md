# План улучшения генерации Cover Letter в Lucidum Bot

## Анализ текущего состояния

### Проблемы существующего метода `generate_cover_letter`:

1. **Примитивный промпт**: Очень простая инструкция без учета best practices
2. **Отсутствие структуры**: Нет четкого понимания структуры cover letter
3. **Нет персонализации**: Не учитывается специфика компании и вакансии
4. **Отсутствие валидации**: Нет проверки качества результата
5. **Нет анализа вакансии**: Не извлекаются ключевые слова и требования
6. **Монолитность**: Вся логика в одном методе, сложно расширять

### Возможности улучшения на основе документации:

1. **Использование ролевых промптов** из `ROLES.md`
2. **Применение критериев качества** из `COVER_LETTER_CRETERIA.md`
3. **Следование best practices** из `COVER_LETTER.md`

## Архитектурные изменения

### 1. Создание отдельного класса `CoverLetterGenerator`

```python
class CoverLetterGenerator:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.validator = CoverLetterValidator()
        self.analyzer = JobAnalyzer()

    async def generate(self, resume: str, job_description: str,
                      company_name: str = "", hiring_manager: str = "") -> CoverLetterResult
```

### 2. Вспомогательные классы:

- `JobAnalyzer` - анализ вакансии и извлечение ключевых слов
- `CoverLetterValidator` - валидация результата по критериям
- `PromptBuilder` - построение промптов на основе ролей
- `CoverLetterResult` - структурированный результат с метаданными

## Пошаговый план реализации

### Этап 1: Создание вспомогательных классов

#### 1.1 Класс `JobAnalyzer`

**Задачи:**

- Извлечение ключевых слов из описания вакансии
- Определение индустрии и типа компании
- Анализ требуемых навыков и квалификации
- Извлечение информации о компании (если есть)

**Методы:**

```python
async def extract_keywords(self, job_description: str) -> List[str]
async def analyze_company_culture(self, job_description: str) -> CompanyCulture
async def extract_requirements(self, job_description: str) -> Requirements
```

#### 1.2 Класс `PromptBuilder`

**Задачи:**

- Выбор оптимальной роли из 7 вариантов в `ROLES.md`
- Построение системного промпта с учетом контекста
- Создание пользовательского промпта с структурированными данными

**Методы:**

```python
def select_optimal_role(self, job_analysis: JobAnalysis) -> RoleType
def build_system_prompt(self, role: RoleType, context: Context) -> str
def build_user_prompt(self, resume: str, job_description: str, keywords: List[str]) -> str
```

#### 1.3 Класс `CoverLetterValidator`

**Задачи:**

- Проверка по критериям из `COVER_LETTER_CRETERIA.md`
- Анализ длины и структуры
- Проверка наличия ключевых слов
- Оценка персонализации

**Методы:**

```python
def validate_structure(self, cover_letter: str) -> ValidationResult
def check_personalization(self, cover_letter: str, company_name: str) -> bool
def verify_keywords(self, cover_letter: str, keywords: List[str]) -> KeywordMatch
def assess_quality(self, cover_letter: str) -> QualityScore
```

### Этап 2: Разработка многоступенчатой генерации

#### 2.1 Анализ вакансии (JobAnalyzer)

```python
async def analyze_job(self, job_description: str) -> JobAnalysis:
    # 1. Извлечение ключевых слов для ATS
    # 2. Определение типа компании (стартап, корпорация, НКО)
    # 3. Анализ культуры компании
    # 4. Извлечение hard/soft skills
    # 5. Определение сениорности позиции
```

#### 2.2 Выбор роли и построение промпта

```python
def select_role_and_build_prompt(self, job_analysis: JobAnalysis) -> PromptSet:
    # Логика выбора роли:
    # - ATS Specialist для крупных компаний
    # - Career Storytelling для креативных индустрий
    # - Industry SME для технических ролей
    # - Growth-Mindset для entry-level
    # и т.д.
```

#### 2.3 Генерация с улучшенными промптами

```python
async def generate_with_role(self, prompt_set: PromptSet) -> str:
    # Использование температуры в зависимости от роли
    # Chain-of-thought для самопроверки
    # Несколько итераций при необходимости
```

#### 2.4 Валидация и улучшение

```python
async def validate_and_improve(self, cover_letter: str, context: Context) -> CoverLetterResult:
    # 1. Проверка по всем критериям
    # 2. При низком качестве - повторная генерация с корректировками
    # 3. Финальная проверка
```

### Этап 3: Улучшение промптов

#### 3.1 Системный промпт (базовый шаблон)

```
Ты - {ROLE_DESCRIPTION}.

ЗАДАЧА: Создать персонализированное сопроводительное письмо на русском языке.

КРИТЕРИИ КАЧЕСТВА:
- Длина: 250-400 слов
- Структура: Введение, основная часть (достижения), культурное соответствие, заключение
- Персонализация: упоминание компании и конкретной позиции
- Метрики: минимум 2 количественных достижения
- Ключевые слова: {KEYWORDS}
- Тон: профессиональный, уверенный, но не агрессивный

ИЗБЕГАЙ:
- Повторения информации из резюме
- Общих фраз типа "командный игрок"
- Упоминания зарплатных ожиданий
- Негативных комментариев о предыдущих работодателях

СТРУКТУРА:
1. Обращение и введение (1-2 предложения)
2. Релевантный опыт с метриками (1-2 абзаца)
3. Соответствие культуре компании (1 абзац)
4. Призыв к действию и заключение (1-2 предложения)

САМОПРОВЕРКА ПЕРЕД ОТВЕТОМ:
- Правильно ли указано название компании?
- Есть ли конкретные метрики?
- Использованы ли ключевые слова?
- Соответствует ли длина требованиям?
```

#### 3.2 Пользовательский промпт (структурированный)

```
ИНФОРМАЦИЯ О КАНДИДАТЕ:
{RESUME}

ОПИСАНИЕ ВАКАНСИИ:
{JOB_DESCRIPTION}

КОМПАНИЯ: {COMPANY_NAME}
КЛЮЧЕВЫЕ НАВЫКИ ИЗ ВАКАНСИИ: {SKILLS}
ТИП ИНДУСТРИИ: {INDUSTRY}
КУЛЬТУРА КОМПАНИИ: {CULTURE_TYPE}

ДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ:
- Имя рекрутера: {HIRING_MANAGER}
- Размер компании: {COMPANY_SIZE}
- Особенности вакансии: {SPECIAL_REQUIREMENTS}
```

### Этап 4: Система валидации

#### 4.1 Автоматические проверки

```python
class ValidationChecks:
    def check_length(self, text: str) -> bool:
        words = len(text.split())
        return 250 <= words <= 400

    def check_structure(self, text: str) -> bool:
        paragraphs = text.split('\n\n')
        return 3 <= len(paragraphs) <= 5

    def check_metrics(self, text: str) -> int:
        # Поиск числовых значений, процентов, временных рамок
        import re
        metrics = re.findall(r'\d+%|\d+\s*(лет|год|месяц|млн|тыс)', text)
        return len(metrics)

    def check_keywords(self, text: str, keywords: List[str]) -> float:
        text_lower = text.lower()
        found = sum(1 for kw in keywords if kw.lower() in text_lower)
        return found / len(keywords) if keywords else 0
```

#### 4.2 Качественная оценка через LLM

```python
async def assess_quality_with_llm(self, cover_letter: str, criteria: str) -> QualityAssessment:
    # Используем отдельный промпт для оценки качества
    # Возвращаем балл и рекомендации по улучшению
```

### Этап 5: Интеграция с ботом

#### 5.1 Обновление bot.py

```python
# Замена простого метода на класс
cover_letter_generator = CoverLetterGenerator(client)

async def generate_cover_letter(resume: str, job_description: str) -> str:
    try:
        result = await cover_letter_generator.generate(
            resume=resume,
            job_description=job_description
        )

        if result.quality_score >= 0.8:
            return result.cover_letter
        else:
            # Попытка улучшения или возврат с предупреждением
            return f"{result.cover_letter}\n\n⚠️ Рекомендуется дополнительная проверка"

    except Exception as e:
        raise Exception(f"Ошибка генерации: {str(e)}")
```

#### 5.2 Добавление опциональных параметров

```python
# Возможность указать дополнительную информацию
@dp.message(Command("generate_advanced"))
async def generate_advanced_handler(message: types.Message):
    # Запрос названия компании, имени рекрутера и т.д.
```

## Структура файлов

```
lucidum/
├── bot.py                              # Основной файл бота
├── cover_letter/                       # Новая папка для функционала
│   ├── __init__.py
│   ├── generator.py                    # CoverLetterGenerator
│   ├── analyzer.py                     # JobAnalyzer
│   ├── validator.py                    # CoverLetterValidator
│   ├── prompt_builder.py              # PromptBuilder
│   ├── models.py                      # Dataclasses для результатов
│   └── roles.py                       # Роли из ROLES.md
├── docs/
│   └── ... (существующие файлы)
└── tests/                             # Тесты для нового функционала
    └── test_cover_letter/
```

## Метрики успеха

1. **Качество результата**:

   - Соответствие критериям из `COVER_LETTER_CRETERIA.md`
   - Уникальность (отсутствие повторов из резюме)
   - Персонализация под вакансию

2. **Пользовательский опыт**:

   - Время генерации (должно остаться < 30 сек)
   - Удовлетворенность пользователей
   - Количество редактирований пользователем

3. **Техническая надежность**:
   - Покрытие тестами > 80%
   - Обработка edge cases
   - Логирование для отладки

## Дальнейшее развитие

1. **A/B тестирование разных ролей** для разных типов вакансий
2. **Обучение на обратной связи** пользователей
3. **Поддержка английского языка** с адаптацией промптов
4. **Интеграция с LinkedIn API** для автоматического получения информации о компании
5. **Генерация нескольких вариантов** с разными подходами

Этот план обеспечит создание высококачественных, персонализированных сопроводительных писем, соответствующих международным стандартам и лучшим практикам HR-индустрии.
