"""
Gradio интерфейс для маркетингового агента.
Запуск: python app.py
"""

import gradio as gr
from marketing_agent import MarketingAgent, TOOLS_SCHEMA
from typing import Generator, List, Tuple


# Создаём агента
agent = MarketingAgent(max_iterations=8)


# ==================== СТИЛИ ====================

CUSTOM_CSS = """
/* Основные цвета */
:root {
    --primary: #FF6B35;
    --primary-dark: #E55A2B;
    --secondary: #004E89;
    --accent: #1A936F;
    --bg-dark: #0D1117;
    --bg-card: #161B22;
    --bg-input: #21262D;
    --text-primary: #F0F6FC;
    --text-secondary: #8B949E;
    --border: #30363D;
}

/* Основной контейнер */
.gradio-container {
    background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1f2e 50%, var(--bg-dark) 100%) !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
}

/* Текстовые поля */
textarea, input[type="text"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2) !important;
}

/* Лейблы */
label, .label-wrap {
    color: var(--text-secondary) !important;
}

/* Кнопки */
.primary-btn {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4) !important;
}

.secondary-btn {
    background: transparent !important;
    border: 2px solid var(--secondary) !important;
    border-radius: 8px !important;
    color: var(--secondary) !important;
    font-weight: 600 !important;
}

.secondary-btn:hover {
    background: var(--secondary) !important;
    color: white !important;
}

/* Результат */
.result-box {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    min-height: 500px !important;
}

.result-box .prose {
    color: var(--text-primary) !important;
}

.result-box h1, .result-box h2, .result-box h3 {
    color: var(--primary) !important;
}

.result-box strong {
    color: var(--accent) !important;
}

/* Прогресс */
.progress-box textarea {
    background: var(--bg-card) !important;
    color: var(--accent) !important;
    font-size: 0.85rem !important;
}

/* Аккордеон */
.accordion {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* Примеры */
.examples-table button {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    border-radius: 6px !important;
}

.examples-table button:hover {
    border-color: var(--primary) !important;
    color: var(--text-primary) !important;
}

/* Скроллбар */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
}
"""


# ==================== ФУНКЦИИ ====================

def format_tools_info() -> str:
    """Форматирует информацию об инструментах"""
    tools_md = "### 🛠️ Доступные инструменты\n\n"
    
    tool_icons = {
        "analyze_target_audience": "👥",
        "estimate_roi": "📊",
        "analyze_seasonality": "📅",
        "channel_effectiveness": "📢",
        "competitor_benchmark": "🏆",
        "budget_allocator": "💰",
        "estimate_budget": "💵",
        "estimate_campaign_duration": "⏱️"
    }
    
    for tool in TOOLS_SCHEMA:
        icon = tool_icons.get(tool["name"], "🔧")
        tools_md += f"**{icon} {tool['name']}**\n"
        tools_md += f"> {tool['description']}\n\n"
    
    return tools_md


def run_agent(query: str) -> Generator[Tuple[str, str], None, None]:
    """Запускает агента и возвращает результаты в реальном времени."""
    if not query.strip():
        yield "⚠️ Пожалуйста, введите запрос", ""
        return
    
    yield "🚀 Запускаю анализ...", ""
    
    try:
        final_result = ""
        step_count = 0
        
        for progress, result in agent.run_stream(query):
            step_count = len(progress.split("\n")) if progress else 0
            
            if result:
                # Финальный результат
                final_result = f"""## 📋 Результат анализа

{result}

---
*Анализ выполнен Marketing Agent за {step_count} шагов*
"""
                yield progress, final_result
            else:
                # Промежуточный прогресс
                yield progress, ""
        
    except Exception as e:
        yield f"❌ Ошибка: {str(e)}", f"Произошла ошибка: {str(e)}"


def clear_all():
    """Очищает все поля"""
    return "", "", ""


# ==================== ИНТЕРФЕЙС ====================

EXAMPLES = [
    ["Мы — стартап в сфере EdTech, запускаем онлайн-курсы по программированию. Бюджет 300,000₽ на 2 месяца. Цель — набрать первых 100 платящих студентов."],
    ["IT-компания, B2B SaaS для автоматизации HR-процессов. Квартальный бюджет 1,000,000₽. Нужен план по привлечению enterprise-клиентов."],
    ["Небольшой интернет-магазин одежды, бюджет 150,000₽. Хотим увеличить продажи в предновогодний сезон."],
    ["Финтех-приложение для инвестиций, таргет — молодёжь 20-30 лет. Бюджет 500,000₽ на awareness кампанию."],
]

WELCOME_TEXT = """### 👋 Добро пожаловать!

Этот агент поможет вам:

1. **Проанализировать целевую аудиторию** для вашего продукта
2. **Оценить эффективность** различных маркетинговых каналов
3. **Рассчитать ожидаемый ROI** для каждого мероприятия
4. **Учесть сезонность** и рыночные бенчмарки
5. **Оптимально распределить бюджет** между каналами

Опишите вашу задачу слева и нажмите **"Запустить анализ"** ✨"""


with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Base(), title="Marketing Agent") as demo:
    
    # Заголовок
    gr.Markdown("""
# 🎯 Marketing Agent
### Автономный AI-ассистент для планирования маркетинговых мероприятий
    """)
    
    with gr.Row():
        # Левая колонка - ввод
        with gr.Column(scale=1):
            query_input = gr.Textbox(
                label="📝 Опишите вашу задачу",
                placeholder="Опишите ваш бизнес, цели и бюджет...",
                lines=6
            )
            
            with gr.Row():
                submit_btn = gr.Button(
                    "🚀 Запустить анализ", 
                    variant="primary",
                    elem_classes=["primary-btn"]
                )
                clear_btn = gr.Button(
                    "🗑️ Очистить", 
                    variant="secondary",
                    elem_classes=["secondary-btn"]
                )
            
            progress_output = gr.Textbox(
                label="📊 Прогресс выполнения",
                lines=4,
                interactive=False,
                elem_classes=["progress-box"]
            )
            
            gr.Examples(
                examples=EXAMPLES,
                inputs=query_input,
                label="💡 Примеры запросов"
            )
        
        # Правая колонка - результат
        with gr.Column(scale=2):
            result_output = gr.Markdown(
                value=WELCOME_TEXT,
                elem_classes=["result-box"]
            )
    
    # Информация об инструментах
    with gr.Accordion("🛠️ Доступные инструменты агента", open=False, elem_classes=["accordion"]):
        gr.Markdown(format_tools_info())
    
    # Футер
    gr.Markdown("---\n*Powered by DeepSeek V3 🤖 | Built with Gradio 🎨*", elem_classes=["footer"])
    
    # Привязка событий
    submit_btn.click(
        fn=run_agent,
        inputs=[query_input],
        outputs=[progress_output, result_output]
    )
    
    query_input.submit(
        fn=run_agent,
        inputs=[query_input],
        outputs=[progress_output, result_output]
    )
    
    clear_btn.click(
        fn=clear_all,
        outputs=[query_input, progress_output, result_output]
    )


# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
