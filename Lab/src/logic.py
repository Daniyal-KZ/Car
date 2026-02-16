import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')


def load_rules():
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_rules(car):
    rules = load_rules()

    # --- 1. HARD FILTER ---
    if rules["critical_rules"]["must_be_diagnosed"] and not car["is_diagnosed"]:
        return "⛔️ Критическая ошибка: Автомобиль не прошел диагностику"

    results = []

    # --- 2. РЕГЛАМЕНТ ТО ПО ПРОБЕГУ ---
    mileage = car["mileage"]
    mileage_rules = rules["mileage_rules"]

    if mileage >= mileage_rules["oil_change"]:
        results.append("🛢 Требуется замена масла")

    if mileage >= mileage_rules["brake_service"]:
        results.append("🛑 Проверка тормозной системы")

    if mileage >= mileage_rules["suspension_check"]:
        results.append("🔧 Осмотр подвески")

    # --- 3. КЛАССИФИКАЦИЯ ПРОБЛЕМ ---
    detected_problems = []
    for symptom in car["symptoms"]:
        if symptom in rules["symptom_mapping"]:
            detected_problems.append(
                f"❗ Симптом '{symptom}' → {rules['symptom_mapping'][symptom]}"
            )

    if not results and not detected_problems:
        return "✅ Автомобиль не требует обслуживания"

    return "\n".join(results + detected_problems)


# ======================== ЛР №4: CHAT BOT ========================

def process_text_message(text, knowledge_graph):
    """
    Обрабатывает текстовое сообщение пользователя и ищет ответ в Базе Знаний.
    
    Args:
        text: Текстовая строка запроса пользователя
        knowledge_graph: Объект KnowledgeGraph (граф знаний)
        
    Returns:
        Строка с ответом бота
    """
    if not text or not knowledge_graph:
        return "⚠️ Пустой запрос или график не загружен."
    
    text_lower = text.lower().strip()
    
    # ========== ЛЮБЕЗНЫЕ ПРИВЕТСТВИЯ ==========
    greetings = ["привет", "привееет", "привет!", "hi", "hello", "hey", "помощь", "help"]
    if any(greeting in text_lower for greeting in greetings):
        if "помощь" in text_lower or "help" in text_lower:
            return (
                "📚 **Список команд:**\n\n"
                "**Компоненты:** Двигатель, Тормозная система, Подвеска, Масло двигателя, Колеса, Аккумулятор, Тормозные колодки, Роторы, Амортизаторы, Фильтры\n\n"
                "**Симптомы:** Скрип, Вибрация, Стуки, Запах горелого, Слабый пуск двигателя\n\n"
                "**Проблемы:** Износ тормозных колодок, Дисбаланс колес, Утечка масла, Люфт в подвеске, Разряженный аккумулятор\n\n"
                "**Задачи ТО:** ТО-1, ТО-2, ТО-3, ТО-4, ТО-5\n\n"
                "Введите название или несколько ключевых слов (например: 'Двигатель Скрип ТО-1')"
            )
        return "👋 Привет! Я AI-ассистент диагностики автомобилей. Спросите меня о компонентах, симптомах, проблемах или задачах ТО. Напишите 'помощь' для списка команд."
    
    # ========== ПОЛУЧАЕМ ВСЕ УЗЛЫ ИЗ ГРАФА ==========
    all_nodes = knowledge_graph.get_all_nodes()
    all_node_names = []
    for node_list in all_nodes.values():
        all_node_names.extend(node_list)
    
    # ========== ОБРАБОТКА НЕСКОЛЬКИХ КЛЮЧЕВЫХ СЛОВ ==========
    # Разбиваем ввод по пробелам и запятым
    keywords = []
    for item in text.replace(',', ' ').split():
        item_clean = item.strip()
        if item_clean and len(item_clean) > 1:  # Отфильтровываем пустые и односимвольные
            keywords.append(item_clean)
    
    found_nodes = {}  # {node_name: match_score}
    
    # Точный поиск для каждого ключевого слова
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # 1. Точное совпадение (case-insensitive)
        for node_name in all_node_names:
            if keyword_lower == node_name.lower():
                found_nodes[node_name] = found_nodes.get(node_name, 0) + 10
        
        # 2. Совпадение в начале названия узла
        for node_name in all_node_names:
            if node_name.lower().startswith(keyword_lower):
                found_nodes[node_name] = found_nodes.get(node_name, 0) + 5
        
        # 3. Совпадение в середине названия узла
        for node_name in all_node_names:
            if keyword_lower in node_name.lower():
                found_nodes[node_name] = found_nodes.get(node_name, 0) + 2
    
    # ========== ЕСЛИ НАЙДЕНЫ УЗЛЫ ==========
    if found_nodes:
        # Сортируем по релевантности
        sorted_nodes = sorted(found_nodes.items(), key=lambda x: x[1], reverse=True)
        
        response = f"Найдено {len(sorted_nodes)} результат(ов):\n\n"
        
        for idx, (node_name, score) in enumerate(sorted_nodes, 1):
            result = knowledge_graph.find_related_entities(node_name)
            
            if result:
                response += f"{idx}. {result['node_name']} ({result['entity_type']})\n"
                response += f"   {result['description']}\n"
                
                if result['related']:
                    response += "   Связи:\n"
                    for related in result['related']:
                        response += f"   - {related['name']} ({related['type']}) — {related['relation']}\n"
                
                response += "\n"
        
        return response
    
    # ========== ПОМОЩЬ ЕСЛИ НИ ЧТО НЕ НАЙДЕНО ==========
    return (
        "❌ Я не нашел такого термина в базе знаний.\n\n"
        "📚 Попробуйте ввести:\n"
        "• Название компонента (Двигатель, Тормозная система, Колеса...)\n"
        "• Симптом (Скрип, Вибрация, Стуки...)\n"
        "• Проблему (Износ тормозов, Дисбаланс колес...)\n"
        "• Задачу ТО (ТО-1, ТО-2, ТО-3...)\n\n"
        "Или напишите 'помощь' для списка команд."
    )
