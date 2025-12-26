"""
Тестовый скрипт для отладки агента
"""

import os
import json
import re
from marketing_agent import MarketingAgent, TOOL_FUNCTIONS, TOOLS_SCHEMA

# Создаём агент с подробным логированием
class DebugMarketingAgent(MarketingAgent):
    
    def run(self, user_query: str, progress_callback=None):
        """Версия с подробным дебагом"""
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        print("="*60)
        print("SYSTEM PROMPT (первые 500 символов):")
        print("="*60)
        print(self._get_system_prompt()[:500] + "...")
        print()
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            print(f"\n{'='*60}")
            print(f"ИТЕРАЦИЯ {iteration}")
            print("="*60)
            
            # Получаем ответ от LLM
            print("\n📤 Отправляю запрос к LLM...")
            response = self._call_llm(messages)
            
            if not response:
                print("❌ Ошибка: пустой ответ от LLM")
                return "Ошибка: не удалось получить ответ от LLM"
            
            print(f"\n📥 Ответ LLM ({len(response)} символов):")
            print("-"*40)
            print(response[:1500])  # Первые 1500 символов
            if len(response) > 1500:
                print(f"... (ещё {len(response) - 1500} символов)")
            print("-"*40)
            
            # Проверяем, есть ли финальный ответ
            if "ФИНАЛЬНЫЙ ОТВЕТ:" in response:
                print("\n✅ Найден ФИНАЛЬНЫЙ ОТВЕТ!")
                final_answer = response.split("ФИНАЛЬНЫЙ ОТВЕТ:")[-1].strip()
                return final_answer
            
            # Ищем вызовы инструментов
            tool_calls = self._parse_tool_calls(response)
            print(f"\n🔧 Найдено tool_calls: {len(tool_calls)}")
            
            if not tool_calls:
                print("⚠️ Нет tool calls, добавляю напоминание...")
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user", 
                    "content": "Пожалуйста, используй доступные инструменты для анализа или дай ФИНАЛЬНЫЙ ОТВЕТ: с ранжированным списком мероприятий."
                })
                continue
            
            # Выполняем инструменты
            tool_results = []
            for i, tool_call in enumerate(tool_calls):
                tool_name = tool_call["name"]
                arguments = tool_call["arguments"]
                
                print(f"\n  🔧 Tool #{i+1}: {tool_name}")
                print(f"     Args: {json.dumps(arguments, ensure_ascii=False)}")
                
                result = self._execute_tool(tool_name, arguments)
                print(f"     Result (первые 200 символов): {result[:200]}...")
                
                tool_results.append(f"<tool_result>\n{result}\n</tool_result>")
            
            # Добавляем результаты в историю
            messages.append({"role": "assistant", "content": response})
            
            # Напоминание о финальном ответе
            if iteration >= 4:
                reminder = "\n\n⚠️ ВАЖНО: У тебя осталось мало итераций. Дай ФИНАЛЬНЫЙ ОТВЕТ: с ранжированным списком мероприятий на основе собранных данных!"
            else:
                reminder = "\n\nПроанализируй результаты и либо используй ещё инструменты, либо дай ФИНАЛЬНЫЙ ОТВЕТ:"
            
            messages.append({
                "role": "user", 
                "content": "Результаты инструментов:\n" + "\n".join(tool_results) + reminder
            })
            
            print(f"\n📝 Всего сообщений в истории: {len(messages)}")
        
        print(f"\n❌ Достигнут лимит итераций ({self.max_iterations})")
        return "Достигнут лимит итераций. Пожалуйста, попробуйте уточнить запрос."


if __name__ == "__main__":
    agent = DebugMarketingAgent(max_iterations=8)
    
    test_query = """
    Мы — IT-компания, разрабатывающая SaaS-решение для управления проектами.
    Наш бюджет на маркетинг — 500,000 рублей на квартал.
    Цель — привлечение новых B2B клиентов.
    
    Помоги составить план маркетинговых мероприятий.
    """
    
    print("\n" + "🚀"*30)
    print("ЗАПУСК ТЕСТОВОГО АГЕНТА")
    print("🚀"*30)
    print(f"\nЗапрос: {test_query.strip()}")
    
    result = agent.run(test_query)
    
    print("\n" + "="*60)
    print("ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
    print("="*60)
    print(result)

