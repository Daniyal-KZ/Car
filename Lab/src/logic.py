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
