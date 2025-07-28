function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to selected tab
    event.target.classList.add('active');
}

async function generateCoverLetter() {
    const button = event.target;
    button.disabled = true;
    button.textContent = '⏳ Generating...';
    
    const data = {
        resume: document.getElementById('resume').value,
        job_description: document.getElementById('jobDescription').value,
        company_name: document.getElementById('companyName').value,
        hiring_manager: document.getElementById('hiringManager').value,
        special_requirements: document.getElementById('specialRequirements').value,
        use_fallback: document.getElementById('useFallback').checked,
        model_name: document.getElementById('modelName').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        max_tokens: parseInt(document.getElementById('maxTokens').value)
    };
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(result, false);
        } else {
            showResult(result, true);
        }
    } catch (error) {
        showResult({error: error.message}, true);
    } finally {
        button.disabled = false;
        button.textContent = '🚀 Generate Cover Letter';
    }
}

async function loadCurrentPrompts() {
    try {
        const response = await fetch('/prompts');
        const prompts = await response.json();
        
        // Load into traditional prompt tab fields if they exist
        const keywordPrompt = document.getElementById('keywordPrompt');
        const systemPrompt = document.getElementById('systemPrompt');
        const fallbackPrompt = document.getElementById('fallbackPrompt');
        
        if (keywordPrompt) keywordPrompt.value = prompts.keyword_extraction_prompt;
        if (systemPrompt) systemPrompt.value = prompts.system_prompt;
        if (fallbackPrompt) fallbackPrompt.value = prompts.fallback_prompt;
        
        // Also load into quick edit fields if they exist
        const quickKeywordPrompt = document.getElementById('quickKeywordPrompt');
        const quickSystemPrompt = document.getElementById('quickSystemPrompt');
        
        if (quickKeywordPrompt) quickKeywordPrompt.placeholder = 'Default: ' + prompts.keyword_extraction_prompt.substring(0, 50) + '...';
        if (quickSystemPrompt) quickSystemPrompt.placeholder = 'Default: ' + prompts.system_prompt.substring(0, 50) + '...';
        
    } catch (error) {
        console.error('Error loading prompts:', error);
    }
}

async function testWithCustomPrompts() {
    const button = event.target;
    button.disabled = true;
    button.textContent = '⏳ Testing...';
    
    const data = {
        resume: document.getElementById('resume').value,
        job_description: document.getElementById('jobDescription').value,
        company_name: document.getElementById('companyName').value,
        hiring_manager: document.getElementById('hiringManager').value,
        special_requirements: document.getElementById('specialRequirements').value,
        custom_system_prompt: document.getElementById('systemPrompt').value,
        custom_keyword_prompt: document.getElementById('keywordPrompt').value,
        use_fallback: false,
        model_name: document.getElementById('modelName').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        max_tokens: parseInt(document.getElementById('maxTokens').value)
    };
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(result, false);
            // Switch back to generate tab to see result
            switchTab('generate');
            document.querySelector('.tab[onclick*="generate"]').classList.add('active');
        } else {
            showResult(result, true);
        }
    } catch (error) {
        showResult({error: error.message}, true);
    } finally {
        button.disabled = false;
        button.textContent = '🧪 Test with Custom Prompts';
    }
}

function loadExampleData() {
    document.getElementById('resume').value = `Иван Петров
Senior Python Developer

ОПЫТ РАБОТЫ:
• Яндекс (2020-2024) - Senior Python Developer
  - Разработка микросервисов на Django/FastAPI
  - Оптимизация производительности (улучшение на 40%)
  - Ментор для 5 разработчиков

• Mail.ru Group (2018-2020) - Python Developer  
  - Разработка API для 1M+ пользователей
  - Интеграция с внешними сервисами
  - Покрытие тестами 85%

НАВЫКИ:
Python, Django, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, Git`;
    
    document.getElementById('jobDescription').value = `Компания: TechCorp
Вакансия: Senior Python Developer

Требования:
• Опыт Python разработки 5+ лет
• Django/FastAPI
• Опыт с микросервисами
• PostgreSQL, Redis
• Docker, Kubernetes
• Опыт ментора

Обязанности:
• Разработка backend сервисов
• Архитектурные решения
• Менторинг junior разработчиков
• Code review`;
    
    document.getElementById('companyName').value = 'TechCorp';
}

function showResult(result, isError) {
    const resultDiv = document.getElementById('result');
    
    if (isError) {
        resultDiv.innerHTML = `
            <div class="result error">
                <h3>❌ Error</h3>
                <p>${result.error || result.detail || 'Unknown error'}</p>
            </div>
        `;
    } else {
        const metadata = result.metadata || {};
        const fallbackText = metadata.fallback_used ? ' | <strong>Fallback Used:</strong> Yes' : '';
        resultDiv.innerHTML = `
            <div class="result success">
                <h3>✅ Generated Cover Letter</h3>
                <div style="white-space: pre-wrap; margin: 15px 0; padding: 15px; background: white; border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">${result.cover_letter}</div>
                <div class="metadata">
                    <strong>Quality Score:</strong> ${(result.quality_score * 100).toFixed(1)}% | 
                    <strong>Keywords Found:</strong> ${result.keywords_found} | 
                    <strong>Generation Time:</strong> ${result.generation_time.toFixed(2)}s | 
                    <strong>Word Count:</strong> ${metadata.word_count || 'N/A'}
                    ${fallbackText}
                </div>
            </div>
        `;
    }
}

// Temperature slider handler
document.addEventListener('DOMContentLoaded', function() {
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperatureValue');
    
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', function() {
            temperatureValue.textContent = this.value;
        });
    }
});

// New functions for enhanced UI

function toggleCollapsible(sectionId) {
    const content = document.getElementById(sectionId + '-content');
    const indicator = document.getElementById(sectionId + '-indicator');
    
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        indicator.textContent = '▼';
    } else {
        content.classList.add('active');
        indicator.textContent = '▲';
    }
}

async function autoFillParameters() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    
    if (!jobDescription) {
        alert('Please enter a job description first');
        return;
    }
    
    const button = event.target;
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = '🔍 Analyzing...';
    
    try {
        const response = await fetch('/analyze-job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: jobDescription })
        });
        
        const analysis = await response.json();
        
        if (response.ok) {
            // Fill in extracted data
            console.log('Analysis result:', analysis);
            
            if (analysis.company_name) {
                document.getElementById('companyName').value = analysis.company_name;
                console.log('Set company name:', analysis.company_name);
            }
            if (analysis.hiring_manager) {
                document.getElementById('hiringManager').value = analysis.hiring_manager;
                console.log('Set hiring manager:', analysis.hiring_manager);
            }
            if (analysis.key_requirements && analysis.key_requirements.length > 0) {
                const requirements = 'Key requirements mentioned: ' + analysis.key_requirements.join(', ');
                document.getElementById('specialRequirements').value = requirements;
                console.log('Set special requirements:', requirements);
            } else {
                console.log('No key requirements found in analysis');
            }
            
            // Show position title if available
            if (analysis.position_title) {
                console.log('Position detected:', analysis.position_title);
            }
            
            // Show confidence indicator
            const confidence = (analysis.confidence_score * 100).toFixed(0);
            button.textContent = `✅ Auto-filled (${confidence}% confidence)`;
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
            }, 3000);
        } else {
            throw new Error(analysis.detail || 'Analysis failed');
        }
    } catch (error) {
        alert('Error analyzing job description: ' + error.message);
        button.textContent = originalText;
        button.disabled = false;
    }
}

function clearCustomPrompts() {
    document.getElementById('quickSystemPrompt').value = '';
    document.getElementById('quickKeywordPrompt').value = '';
}

function loadCurrentPromptsToQuick() {
    // Load current prompts into the quick edit fields
    fetch('/prompts')
        .then(response => response.json())
        .then(prompts => {
            document.getElementById('quickSystemPrompt').value = prompts.system_prompt;
            document.getElementById('quickKeywordPrompt').value = prompts.keyword_extraction_prompt;
        })
        .catch(error => {
            console.error('Error loading prompts:', error);
        });
}

// Load current prompts on page load
window.onload = function() {
    loadCurrentPrompts();
}; 