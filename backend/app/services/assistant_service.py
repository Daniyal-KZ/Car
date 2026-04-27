import base64
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.security import decrypt_secret
from app.models import Car, DamageReport, Invoice, MaintenanceRule, ServiceBookEntry, ServiceOrder, AssistantChat, AssistantMessage, User

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash",
]

MODEL_EXCLUDE_PATTERNS = (
    "-tts",
    "tts-",
    "preview-tts",
    "imagen",
    "gemma",
)

SYSTEM_PROMPT = """You are an assistant for a car service web app.
Respond in Russian.
Service name: CAR API.
You must use the provided user context as the source of truth.
You must respect the current user's role and data scope.
Never invent counts, totals, statuses, vehicle names, owners, or other facts.
If the user asks about data or actions, output only JSON with an intent/data/action plan; keep reply empty.
Output JSON only with this schema:
{
  "reply": "short helper text or empty string",
  "intent": "none|list_cars|list_orders|list_invoices|list_damage_reports|list_service_book|list_maintenance_rules|count_entities|get_car_attribute|get_price|create_booking|booking_status|sum_paid_invoices|show_page|show_capabilities",
  "data": {},
  "action": null or {"type": "navigate", "route": "/path"}
}
Rules:
- Only use facts available in context.
- Never answer with guessed numbers or guessed lists.
- For count/list/status/booking requests, return intent/data only; the backend will build the exact answer.
- Understand natural language time expressions and map them into structured fields when possible.
- Do not trigger damage flow unless the user explicitly wants to create/open a damage request.
- If the request is unclear, ask one short clarifying question.
- The app has capabilities registry below; use it to choose the right intent, entity, and route.
- Do not add markdown fences.
"""

PRIVILEGED_ROLES = {"admin", "dev"}

ENTITY_PATTERNS: dict[str, tuple[str, ...]] = {
    "cars": (
        r"\bмашин[аы]?\b",
        r"\bавтомобил[ьяеиов]*\b",
        r"\bавто\b",
        r"\bcars?\b",
    ),
    "orders": (
        r"\bзаявк[аи]?\b",
        r"\bзаказ[а-я]*\b",
        r"\bзапис[ьяи]?\b",
        r"\bbookings?\b",
    ),
    "invoices": (
        r"\bсч[её]т[а-я]*\b",
        r"\binvoices?\b",
    ),
    "damage_reports": (
        r"\bповрежден[а-я]*\b",
        r"\bдефект[а-я]*\b",
        r"\bцарапин[а-я]*\b",
        r"\bвмятин[а-я]*\b",
        r"\bскол[а-я]*\b",
        r"\bтрещин[а-я]*\b",
    ),
    "service_book": (
        r"\bсервисн[а-я]*\b",
        r"\bкнижк[а-я]*\b",
        r"\bжурнал[а-я]*\b",
        r"\bсервис\s+запис[ьяи]\b",
    ),
    "maintenance_rules": (
        r"\bрегламент[а-я]*\b",
        r"\bправил[а-я]*\b",
        r"\bmaintenance\s+rule[s]?\b",
        r"\bmaintenance\b",
    ),
}

ENTITY_LABELS = {
    "cars": "машин",
    "orders": "заявок",
    "invoices": "счетов",
    "damage_reports": "повреждений",
    "service_book": "записей сервиса",
    "maintenance_rules": "регламентов",
}

COUNT_REQUEST_TOKENS = ("сколько", "количество", "число", "count")
COUNT_REQUEST_PATTERNS = (
    r"\bс?кольк[оа]?\b",  # "сколько" + частая опечатка "колько"
    r"\bколичеств[оа]?\b",
    r"\bчисл[оа]?\b",
    r"\bcount\b",
)
LIST_REQUEST_TOKENS = ("список", "покажи", "покажи мне", "перечисли", "какие", "что есть", "что у меня")
ALLOWED_INTENTS = {
    "none",
    "count_entities",
    "get_car_attribute",
    "list_cars",
    "list_orders",
    "list_invoices",
    "list_damage_reports",
    "list_service_book",
    "list_maintenance_rules",
    "get_price",
    "create_booking",
    "booking_status",
    "sum_paid_invoices",
    "show_page",
    "show_capabilities",
}

SITE_CAPABILITIES: dict[str, dict[str, Any]] = {
    "cars": {
        "label": "Машины",
        "routes": ["/cars"],
        "operations": ["count", "list", "get", "create", "update", "delete", "upload_images", "get_attribute"],
        "access": "own data for user, all data for admin/dev",
    },
    "orders": {
        "label": "Заявки на сервис",
        "routes": ["/service-orders/my", "/service-orders/{id}", "/user/booking"],
        "operations": ["count", "list", "get", "create", "status", "navigate"],
        "access": "own data for user, all queue for mechanic/admin/dev",
    },
    "invoices": {
        "label": "Счета",
        "routes": ["/invoices/my", "/invoices/{id}", "/user/invoices"],
        "operations": ["count", "list", "get", "mark_paid", "sum_paid"],
        "access": "own data for user, broader access for mechanic/admin/dev",
    },
    "damage_reports": {
        "label": "Отчеты о повреждениях",
        "routes": ["/damage-reports/my", "/damage-reports/{id}", "/user/damages"],
        "operations": ["count", "list", "get", "create", "upload_photos", "analyze"],
        "access": "own data for user, analysis/queue for mechanic/admin/dev",
    },
    "service_book": {
        "label": "Сервисная книжка",
        "routes": ["/service-book/bookings/my", "/service-book/{car_id}", "/user/booking"],
        "operations": ["count", "list", "get", "create_booking_entry"],
        "access": "own cars for user, admin has broader access",
    },
    "maintenance_rules": {
        "label": "Регламенты обслуживания",
        "routes": ["/maintenance-rules", "/maintenance-rules/{id}", "/maintenance-rules/car/{car_id}/executions"],
        "operations": ["count", "list", "get", "create", "update", "executions"],
        "access": "active rules for all users, admin/dev full access",
    },
}

CAR_ATTRIBUTE_PATTERNS: dict[str, tuple[str, ...]] = {
    "mileage": (r"\bпробег\b", r"\bmileage\b"),
    "vin": (r"\bvin\b", r"\bвин\b"),
    "year": (r"\bгод\b", r"\byear\b"),
    "brand": (r"\bбренд\b", r"\bмарк[а-я]*\b", r"\bbrand\b"),
    "model": (r"\bмодель\b", r"\bmodel\b"),
}


def _is_privileged_user(current_user: User) -> bool:
    return current_user.role in PRIVILEGED_ROLES


def _match_any_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _request_contains_count_question(text: str) -> bool:
    lowered = text.lower()
    if any(token in lowered for token in COUNT_REQUEST_TOKENS):
        return True
    return any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in COUNT_REQUEST_PATTERNS)


def _request_contains_list_question(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in LIST_REQUEST_TOKENS)


def _request_contains_help_question(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in (
            "что ты умеешь",
            "что можешь",
            "помощь",
            "возможности",
            "что доступно",
            "что я могу сделать",
        )
    )


def _detect_requested_entities(text: str) -> list[str]:
    return [entity for entity, patterns in ENTITY_PATTERNS.items() if _match_any_pattern(text, patterns)]


def _scoped_car_query(db: Session, current_user: User):
    query = db.query(Car)
    if not _is_privileged_user(current_user):
        query = query.filter(Car.owner_id == current_user.id)
    return query


def _detect_car_attribute(text: str) -> str | None:
    lowered = text.lower()
    for attribute, patterns in CAR_ATTRIBUTE_PATTERNS.items():
        if _match_any_pattern(lowered, patterns):
            return attribute
    return None


def _match_scoped_car_from_text(db: Session, current_user: User, text: str) -> Car | None:
    lowered = text.lower()
    cars = _scoped_car_query(db, current_user).all()
    for car in cars:
        brand = (car.brand or "").strip().lower()
        model = (car.model or "").strip().lower()
        vin = (car.vin or "").strip().lower()
        if (brand and brand in lowered) or (model and model in lowered) or (vin and vin in lowered):
            return car
    if len(cars) == 1:
        return cars[0]
    return None


def _scoped_order_query(db: Session, current_user: User):
    query = db.query(ServiceOrder).options(joinedload(ServiceOrder.car))
    if not _is_privileged_user(current_user):
        query = query.filter(ServiceOrder.requested_by == current_user.id)
    return query


def _scoped_invoice_query(db: Session, current_user: User):
    query = db.query(Invoice).join(ServiceOrder, ServiceOrder.id == Invoice.order_id).options(joinedload(Invoice.items), joinedload(Invoice.order))
    if not _is_privileged_user(current_user):
        query = query.filter(ServiceOrder.requested_by == current_user.id)
    return query


def _scoped_damage_query(db: Session, current_user: User):
    query = db.query(DamageReport).options(joinedload(DamageReport.car))
    if not _is_privileged_user(current_user):
        query = query.filter(DamageReport.requested_by == current_user.id)
    return query


def _scoped_service_book_query(db: Session, current_user: User):
    query = db.query(ServiceBookEntry).join(Car, Car.id == ServiceBookEntry.car_id).options(joinedload(ServiceBookEntry.car))
    if not _is_privileged_user(current_user):
        query = query.filter(Car.owner_id == current_user.id)
    return query


def _scoped_maintenance_rules_query(db: Session, current_user: User):
    query = db.query(MaintenanceRule).options(joinedload(MaintenanceRule.tasks))
    if not _is_privileged_user(current_user):
        query = query.filter(MaintenanceRule.status == "active")
    return query


def _entity_count(db: Session, current_user: User, entity: str) -> int:
    if entity == "cars":
        return int(_scoped_car_query(db, current_user).with_entities(func.count(Car.id)).scalar() or 0)
    if entity == "orders":
        return int(_scoped_order_query(db, current_user).with_entities(func.count(ServiceOrder.id)).scalar() or 0)
    if entity == "invoices":
        return int(_scoped_invoice_query(db, current_user).with_entities(func.count(Invoice.id)).scalar() or 0)
    if entity == "damage_reports":
        return int(_scoped_damage_query(db, current_user).with_entities(func.count(DamageReport.id)).scalar() or 0)
    if entity == "service_book":
        return int(_scoped_service_book_query(db, current_user).with_entities(func.count(ServiceBookEntry.id)).scalar() or 0)
    if entity == "maintenance_rules":
        return int(_scoped_maintenance_rules_query(db, current_user).with_entities(func.count(MaintenanceRule.id)).scalar() or 0)
    return 0


def _describe_count_entities(db: Session, current_user: User, entities: list[str]) -> tuple[str, dict[str, Any] | None]:
    unique_entities: list[str] = []
    for entity in entities:
        if entity in ENTITY_LABELS and entity not in unique_entities:
            unique_entities.append(entity)

    if not unique_entities:
        return "", None

    counts = {entity: _entity_count(db, current_user, entity) for entity in unique_entities}
    if len(unique_entities) == 1:
        entity = unique_entities[0]
        return str(counts[entity]), {"entity": entity, "count": counts[entity]}

    parts = [f"{ENTITY_LABELS.get(entity, entity).capitalize()}: {counts[entity]}" for entity in unique_entities]
    return "; ".join(parts), {"counts": counts}


def _maybe_count_request(text: str, current_user: User) -> list[str] | None:
    if not _request_contains_count_question(text):
        return None
    entities = _detect_requested_entities(text)
    return entities or None


def _maybe_list_request(text: str) -> str | None:
    lowered = text.lower()
    if not _request_contains_list_question(text):
        return None
    entities = _detect_requested_entities(lowered)
    return entities[0] if entities else None


def _build_site_capabilities_context() -> str:
    lines = []
    for key, meta in SITE_CAPABILITIES.items():
        routes = ", ".join(meta.get("routes", []))
        operations = ", ".join(meta.get("operations", []))
        lines.append(f"- {meta['label']} ({key}): ops=[{operations}], routes=[{routes}]")
    return "Site capabilities:\n" + "\n".join(lines)


def _discover_gemini_models(api_key: str) -> list[str]:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models"
        f"?key={urllib.parse.quote(api_key)}"
    )
    req = urllib.request.Request(endpoint, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except Exception:
        return []

    discovered: list[str] = []
    for model in data.get("models", []):
        name = str(model.get("name", ""))
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" not in methods:
            continue
        if name.startswith("models/"):
            name = name.split("/", 1)[1]
        if name:
            discovered.append(name)
    return discovered


def _is_text_model_name(model_name: str) -> bool:
    lowered = model_name.lower()
    return not any(pattern in lowered for pattern in MODEL_EXCLUDE_PATTERNS)


def _supported_model_candidates(discovered_models: list[str]) -> list[str]:
    preferred = [model for model in GEMINI_MODELS if _is_text_model_name(model)]
    discovered = [model for model in discovered_models if _is_text_model_name(model)]

    merged: list[str] = []
    for model in preferred + discovered:
        if model not in merged:
            merged.append(model)

    return merged or preferred


def _is_model_capability_error(details: str) -> bool:
    lowered = details.lower()
    return (
        "multiturn chat is not enabled" in lowered
        or "response modalities" in lowered
        or "not supported by the model" in lowered
        or "accepts the following combination" in lowered
        or "developer instruction is not enabled" in lowered
        or "audio" in lowered and "text" in lowered
    )


def _to_gemini_role(role: str) -> str:
    return "model" if role == "assistant" else "user"


def _build_user_context(db: Session, current_user: User) -> str:
    cars = _scoped_car_query(db, current_user).order_by(Car.id.desc()).limit(10).all()
    orders = _scoped_order_query(db, current_user).order_by(ServiceOrder.created_at.desc()).limit(10).all()
    invoices = _scoped_invoice_query(db, current_user).order_by(Invoice.created_at.desc()).limit(10).all()
    damages = _scoped_damage_query(db, current_user).order_by(DamageReport.created_at.desc()).limit(10).all()
    service_entries = _scoped_service_book_query(db, current_user).order_by(ServiceBookEntry.created_at.desc()).limit(10).all()
    maintenance_rules = _scoped_maintenance_rules_query(db, current_user).order_by(MaintenanceRule.id.desc()).limit(10).all()

    scope_text = "all accessible data" if _is_privileged_user(current_user) else "own data only"

    car_lines = [
        f"- ID {car.id}: {car.brand} {car.model}, year {car.year}, mileage {int(car.mileage or 0):,} km, VIN {car.vin or 'not set'}"
        for car in cars
    ] or ["- No cars found"]

    order_lines = [
        f"- ORD-{order.id}: {order.service_name} ({order.status}), car #{order.car_id}, scheduled {order.scheduled_at.isoformat() if order.scheduled_at else 'n/a'}"
        for order in orders
    ] or ["- No orders found"]

    invoice_lines = [
        f"- INV-{invoice.id}: {invoice.status}, total {int(invoice.total or 0):,} {invoice.currency}, order ORD-{invoice.order_id}"
        for invoice in invoices
    ] or ["- No invoices found"]

    damage_lines = [
        f"- DR-{damage.id}: {damage.title}, {damage.damage_type}, status {damage.status}, car #{damage.car_id}"
        for damage in damages
    ] or ["- No damage reports found"]

    service_book_lines = [
        f"- SB-{entry.id}: {entry.type}, mileage {entry.mileage}, car #{entry.car_id}, {entry.description}"
        for entry in service_entries
    ] or ["- No service book entries found"]

    maintenance_rule_lines = [
        f"- MR-{rule.id}: {rule.title}, {rule.brand} {rule.model}, status {rule.status}"
        for rule in maintenance_rules
    ] or ["- No maintenance rules found"]

    return (
        f"User context:\n"
        f"- User ID: {current_user.id}\n"
        f"- Username: {current_user.username}\n"
        f"- Role: {current_user.role}\n"
        f"- Scope: {scope_text}\n\n"
        f"Counts:\n"
        f"- Cars: {_entity_count(db, current_user, 'cars')}\n"
        f"- Orders: {_entity_count(db, current_user, 'orders')}\n"
        f"- Invoices: {_entity_count(db, current_user, 'invoices')}\n"
        f"- Damage reports: {_entity_count(db, current_user, 'damage_reports')}\n"
        f"- Service book entries: {_entity_count(db, current_user, 'service_book')}\n\n"
        f"- Maintenance rules: {_entity_count(db, current_user, 'maintenance_rules')}\n\n"
        f"Cars:\n" + "\n".join(car_lines) + "\n\n"
        f"Orders:\n" + "\n".join(order_lines) + "\n\n"
        f"Invoices:\n" + "\n".join(invoice_lines) + "\n\n"
        f"Damage reports:\n" + "\n".join(damage_lines) + "\n\n"
        f"Service book:\n" + "\n".join(service_book_lines) + "\n\n"
        f"Maintenance rules:\n" + "\n".join(maintenance_rule_lines)
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
    stripped = re.sub(r"\s*```$", "", stripped)

    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = stripped[start : end + 1]
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed

    return {"reply": stripped, "intent": "none", "data": {}, "action": None}


def _normalize_model_plan(raw_plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(raw_plan, dict):
        return {"reply": "", "intent": "none", "data": {}, "action": None}

    intent = str(raw_plan.get("intent") or "none").strip().lower()
    if intent not in ALLOWED_INTENTS:
        intent = "none"

    data = raw_plan.get("data")
    if not isinstance(data, dict):
        data = {}

    action = raw_plan.get("action")
    if action is not None and not isinstance(action, dict):
        action = None

    reply = str(raw_plan.get("reply") or "").strip()
    return {"reply": reply, "intent": intent, "data": data, "action": action}


def _default_estimate_for(kind: str, name: str) -> list[dict[str, Any]]:
    if kind == "maintenance_rule":
        return [
            {"title": "Работы по регламенту", "quantity": 1, "unit_price": 25000},
            {"title": "Расходники", "quantity": 1, "unit_price": 18000},
        ]
    if kind == "technical_inspection":
        return [{"title": "Технический осмотр", "quantity": 1, "unit_price": 12000}]
    if kind == "diagnostics":
        return [{"title": "Диагностика", "quantity": 1, "unit_price": 10000}]
    if kind == "damage_assessment":
        return [{"title": "Осмотр повреждений", "quantity": 1, "unit_price": 8000}]
    return [{"title": name or "Сервисные работы", "quantity": 1, "unit_price": 15000}]


def _catalog_price_text(service_kind: str | None, service_name: str | None) -> str:
    kind = (service_kind or "").strip().lower()
    if kind == "maintenance_rule":
        total = 25000 + 18000
        return f"Ориентировочно {total:,} ₸ за типовой регламентный пакет".replace(",", " ")
    if kind == "technical_inspection":
        return "Ориентировочно 12 000 ₸"
    if kind == "diagnostics":
        return "Ориентировочно 10 000 ₸"
    if kind == "damage_assessment":
        return "Ориентировочно 8 000 ₸"
    title = service_name or "сервисная работа"
    total = _default_estimate_for(kind or "other", title)[0]["unit_price"]
    return f"Ориентировочно {total:,} ₸".replace(",", " ")


def _resolve_chat_owner(db: Session, chat: AssistantChat, current_user: User) -> None:
    if chat.user_id != current_user.id and current_user.role not in {"admin", "dev"}:
        raise HTTPException(status_code=403, detail="Forbidden")


def _get_or_create_chat(db: Session, current_user: User, chat_id: str | None = None, title: str | None = None) -> AssistantChat:
    if chat_id:
        chat = db.query(AssistantChat).filter(AssistantChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        _resolve_chat_owner(db, chat, current_user)
        return chat

    chat = AssistantChat(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=title.strip() if title and title.strip() else "Новый чат",
        provider="gemini",
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def _message_history(chat: AssistantChat) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for message in chat.messages[-12:]:
        history.append({"role": _to_gemini_role(message.role), "content": message.content})
    return history


def _build_model_response(api_key: str, system_prompt: str, history: list[dict[str, str]], user_message: str) -> tuple[dict[str, Any], str]:
    contents = [
        {"role": item["role"], "parts": [{"text": item["content"][:4000]}]}
        for item in history
        if item.get("content", "").strip()
    ]
    contents.append({"role": "user", "parts": [{"text": user_message[:4000]}]})

    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.25, "maxOutputTokens": 1024},
    }

    discovered_models = _discover_gemini_models(api_key)
    model_candidates = _supported_model_candidates(discovered_models)
    last_error = None
    overload_detected = False

    for model_name in model_candidates:
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model_name}:generateContent?key={urllib.parse.quote(api_key)}"
        )
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                candidates = data.get("candidates") or []
                if not candidates:
                    raise HTTPException(status_code=502, detail="Gemini returned empty response")
                parts = (candidates[0].get("content") or {}).get("parts") or []
                text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
                answer = "\n".join(part for part in text_parts if part).strip()
                if not answer:
                    raise HTTPException(status_code=502, detail="Gemini returned no text")
                parsed = _extract_json_object(answer)
                return parsed, model_name
        except urllib.error.HTTPError as e:
            details = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else str(e)
            last_error = details
            if e.code == 404:
                continue
            if e.code in {429, 503}:
                overload_detected = True
                continue
            if e.code == 400 and _is_model_capability_error(details):
                continue
            if e.code == 400 and "API_KEY_INVALID" in details:
                raise HTTPException(status_code=400, detail="Gemini API key is invalid")
            raise HTTPException(status_code=502, detail=f"Gemini API error: {details[:250]}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Gemini connection error: {str(e)}")

    if overload_detected:
        return (
            {
                "reply": "Gemini сейчас перегружен. Попробуйте еще раз через минуту.",
                "intent": "none",
                "data": {},
                "action": None,
            },
            model_candidates[0] if model_candidates else "gemini",
        )

    return (
        {
            "reply": "Не удалось получить ответ от Gemini. Попробуйте позже.",
            "intent": "none",
            "data": {},
            "action": None,
        },
        model_candidates[0] if model_candidates else "gemini",
    )


def _list_user_cars(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    cars = _scoped_car_query(db, current_user).order_by(Car.id.desc()).all()
    if not cars:
        return "Машин не найдено.", None

    lines = []
    for car in cars:
        lines.append(
            f"{car.brand} {car.model}, {car.year} год, пробег {int(car.mileage or 0):,} км, VIN {car.vin or 'не указан'}"
            .replace(",", " ")
        )
    prefix = "Доступные машины" if _is_privileged_user(current_user) else "У вас есть"
    return prefix + ": " + "; ".join(lines) + ".", {"cars": [car.id for car in cars]}


def _list_user_orders(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    orders = _scoped_order_query(db, current_user).order_by(ServiceOrder.created_at.desc()).limit(10).all()
    if not orders:
        return "Заявок не найдено.", None

    lines: list[str] = []
    for order in orders:
        car_name = f"{order.car.brand} {order.car.model}" if order.car else f"car #{order.car_id}"
        when = order.scheduled_at.strftime("%d.%m.%Y %H:%M") if order.scheduled_at else "время не указано"
        lines.append(f"ORD-{order.id}: {order.service_name}, {order.status}, {car_name}, {when}")

    prefix = "Доступные заявки" if _is_privileged_user(current_user) else "Ваши заявки"
    return prefix + ": " + "; ".join(lines) + ".", {"order_ids": [order.id for order in orders]}


def _list_user_invoices(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    invoices = _scoped_invoice_query(db, current_user).order_by(Invoice.created_at.desc()).limit(10).all()
    if not invoices:
        return "Счетов не найдено.", None

    lines: list[str] = []
    for invoice in invoices:
        status = invoice.status
        total = int(invoice.total or 0)
        lines.append(f"INV-{invoice.id}: {status}, {total:,} {invoice.currency}, order ORD-{invoice.order_id}".replace(",", " "))

    prefix = "Доступные счета" if _is_privileged_user(current_user) else "Ваши счета"
    return prefix + ": " + "; ".join(lines) + ".", {"invoice_ids": [invoice.id for invoice in invoices]}


def _list_user_damage_reports(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    damages = _scoped_damage_query(db, current_user).order_by(DamageReport.created_at.desc()).limit(10).all()
    if not damages:
        return "Отчётов о повреждениях не найдено.", None

    lines: list[str] = []
    for damage in damages:
        lines.append(f"DR-{damage.id}: {damage.title}, {damage.damage_type}, {damage.status}, car #{damage.car_id}")

    prefix = "Доступные отчёты о повреждениях" if _is_privileged_user(current_user) else "Ваши отчёты о повреждениях"
    return prefix + ": " + "; ".join(lines) + ".", {"damage_report_ids": [damage.id for damage in damages]}


def _list_user_service_book_entries(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    entries = _scoped_service_book_query(db, current_user).order_by(ServiceBookEntry.created_at.desc()).limit(10).all()
    if not entries:
        return "Записей сервиса не найдено.", None

    lines: list[str] = []
    for entry in entries:
        lines.append(f"SB-{entry.id}: {entry.type}, mileage {entry.mileage}, car #{entry.car_id}, {entry.description}")

    prefix = "Доступные записи сервиса" if _is_privileged_user(current_user) else "Ваши записи сервиса"
    return prefix + ": " + "; ".join(lines) + ".", {"service_book_ids": [entry.id for entry in entries]}


def _list_user_maintenance_rules(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    rules = _scoped_maintenance_rules_query(db, current_user).order_by(MaintenanceRule.id.desc()).limit(10).all()
    if not rules:
        return "Регламентов не найдено.", None

    lines: list[str] = []
    for rule in rules:
        car_hint = f"{rule.brand} {rule.model}".strip()
        lines.append(f"MR-{rule.id}: {rule.title}, {car_hint}, status {rule.status}")

    prefix = "Доступные регламенты" if _is_privileged_user(current_user) else "Активные регламенты"
    return prefix + ": " + "; ".join(lines) + ".", {"maintenance_rule_ids": [rule.id for rule in rules]}


def _show_capabilities() -> tuple[str, dict[str, Any] | None]:
    parts = []
    for key, meta in SITE_CAPABILITIES.items():
        parts.append(f"{meta['label']}: {', '.join(meta.get('operations', []))}")
    return "Я могу помогать с: " + "; ".join(parts) + ".", {"capabilities": SITE_CAPABILITIES}


def _get_car_attribute_value(db: Session, current_user: User, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    attribute = str(data.get("attribute") or "").strip().lower()
    if attribute not in CAR_ATTRIBUTE_PATTERNS:
        return "Уточните, какой атрибут машины нужен (пробег, VIN, год, бренд, модель).", None

    car: Car | None = None
    car_id = data.get("car_id")
    if car_id is not None:
        try:
            car = _scoped_car_query(db, current_user).filter(Car.id == int(car_id)).first()
        except Exception:
            car = None

    if not car:
        return "Уточните, по какой машине нужен ответ.", {"attribute": attribute}

    if attribute == "mileage":
        value = int(car.mileage or 0)
        return str(value), {"car_id": car.id, "attribute": attribute, "value": value}
    if attribute == "vin":
        value = car.vin or "не указан"
        return value, {"car_id": car.id, "attribute": attribute, "value": value}
    if attribute == "year":
        value = int(car.year)
        return str(value), {"car_id": car.id, "attribute": attribute, "value": value}
    if attribute == "brand":
        value = car.brand
        return value, {"car_id": car.id, "attribute": attribute, "value": value}
    if attribute == "model":
        value = car.model
        return value, {"car_id": car.id, "attribute": attribute, "value": value}

    return "Не смог извлечь значение поля.", None


def _create_booking(db: Session, current_user: User, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    car_id = data.get("car_id")
    cars = _scoped_car_query(db, current_user).order_by(Car.id.asc()).all()
    car: Car | None = None

    if car_id is not None:
        car = _scoped_car_query(db, current_user).filter(Car.id == int(car_id)).first()
    elif len(cars) == 1:
        car = cars[0]
    else:
        return "Уточните, на какую машину записывать: у вас несколько автомобилей.", None

    if not car:
        return "Не нашёл машину для записи. Уточните car_id.", None

    service_name = str(data.get("service_name") or data.get("service") or "").strip() or "Сервисная заявка"
    service_kind = str(data.get("service_kind") or "other_service").strip()
    requested_comment = str(data.get("requested_comment") or data.get("comment") or "").strip() or None

    scheduled_at_raw = data.get("scheduled_at")
    if not scheduled_at_raw:
        date = data.get("date")
        time = data.get("time")
        if date and time:
            scheduled_at_raw = f"{date} {time}"

    if not scheduled_at_raw:
        return "Уточните дату и время записи.", None

    scheduled_at_text = str(scheduled_at_raw).replace("T", " ").strip().strip(".")
    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_text)
    except ValueError:
        try:
            scheduled_at = datetime.strptime(scheduled_at_text, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                scheduled_at = datetime.strptime(scheduled_at_text, "%d.%m.%Y %H:%M")
            except ValueError:
                return "Не смог распознать дату записи. Укажите в формате 2026-04-09 09:20.", None

    order = ServiceOrder(
        car_id=car.id,
        requested_by=current_user.id,
        service_kind=service_kind,
        service_name=service_name,
        status="new",
        requested_comment=requested_comment,
        scheduled_at=scheduled_at,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return (
        f"Записал {car.brand} {car.model} на {service_name} на {scheduled_at.strftime('%d.%m.%Y %H:%M')}.",
        {"order_id": order.id, "car_id": car.id, "route": f"/user/booking/{order.id}"},
    )


def _show_page_action(data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    route = str(data.get("route") or "").strip()
    if not route.startswith("/"):
        return "", None
    label = str(data.get("label") or data.get("page") or route)
    return f"Открываю страницу: {label}", {"type": "navigate", "route": route}


def _booking_status(db: Session, current_user: User, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    order_id = data.get("order_id")
    if order_id is None:
        return _list_user_orders(db, current_user)

    order_query = db.query(ServiceOrder).options(joinedload(ServiceOrder.car))
    if not _is_privileged_user(current_user):
        order_query = order_query.filter(ServiceOrder.requested_by == current_user.id)

    order = order_query.filter(ServiceOrder.id == int(order_id)).first()
    if not order:
        return "Не нашел такую заявку. Проверьте номер заказа.", None

    car_name = f"{order.car.brand} {order.car.model}" if order.car else f"car #{order.car_id}"
    when = order.scheduled_at.strftime("%d.%m.%Y %H:%M") if order.scheduled_at else "время не указано"
    return (
        f"Заявка ORD-{order.id}: статус {order.status}, услуга {order.service_name}, авто {car_name}, дата {when}.",
        {"order_id": order.id, "status": order.status, "route": f"/user/booking/{order.id}"},
    )


def _sum_paid_invoices(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    invoices = _scoped_invoice_query(db, current_user).filter(Invoice.status == "paid").all()
    if not invoices:
        return "Оплаченных счетов не найдено.", {"count": 0, "total": 0}

    total = float(sum(float(invoice.total or 0) for invoice in invoices))
    prefix = "Сумма оплаченных счетов" if _is_privileged_user(current_user) else "Сумма оплаченных счетов"
    return (
        f"{prefix}: {int(total):,} ₸ (всего {len(invoices)}).".replace(",", " "),
        {"count": len(invoices), "total": int(total), "currency": "KZT", "route": "/user/invoices"},
    )


def _try_parse_time(text: str) -> str | None:
    matched = re.search(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b", text)
    if not matched:
        matched = re.search(r"\b([01]?\d|2[0-3])\s+([0-5]\d)\b", text)
    if not matched:
        # "в час", "на час", "в обед", "в 9 вечера"
        phrase = text.lower()
        period_match = re.search(r"\b(\d{1,2})\s*(?:час(?:а|ов)?\s*)?(утра|дня|вечера|ночи)\b", phrase)
        if period_match:
            hour = int(period_match.group(1))
            period = period_match.group(2)
            if period in {"дня", "вечера"} and hour < 12:
                hour += 12
            if period == "ночи" and hour == 12:
                hour = 0
            return f"{hour:02d}:00"

        if re.search(r"\b(в|на)\s+час\b", phrase):
            return "13:00"
        if "в обед" in phrase or "на обед" in phrase:
            return "13:00"
        if "утром" in phrase:
            return "09:00"
        if "днем" in phrase or "днём" in phrase:
            return "14:00"
        if "вечером" in phrase:
            return "21:00"
        return None
    return f"{int(matched.group(1)):02d}:{matched.group(2)}"


def _parse_relative_date(text: str) -> str | None:
    lowered = text.lower()
    now = datetime.now()
    if "послезавтра" in lowered:
        return (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)).strftime("%Y-%m-%d")
    if "завтра" in lowered:
        return (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d")
    if "сегодня" in lowered:
        return now.strftime("%Y-%m-%d")

    explicit_iso = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", lowered)
    if explicit_iso:
        return explicit_iso.group(1)

    explicit_ru = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](20\d{2})\b", lowered)
    if explicit_ru:
        day = int(explicit_ru.group(1))
        month = int(explicit_ru.group(2))
        year = int(explicit_ru.group(3))
        try:
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return None

    explicit_short = re.search(r"\b(\d{1,2})[./-](\d{1,2})\b", lowered)
    if explicit_short:
        day = int(explicit_short.group(1))
        month = int(explicit_short.group(2))
        year = now.year
        try:
            candidate = datetime(year, month, day)
            if candidate.date() < now.date():
                candidate = datetime(year + 1, month, day)
            return candidate.strftime("%Y-%m-%d")
        except ValueError:
            return None

    month_map = {
        "январ": 1,
        "феврал": 2,
        "март": 3,
        "апрел": 4,
        "мая": 5,
        "май": 5,
        "июн": 6,
        "июл": 7,
        "август": 8,
        "сентябр": 9,
        "октябр": 10,
        "ноябр": 11,
        "декабр": 12,
    }
    month_word = re.search(r"\b(\d{1,2})\s+([а-яё]+)(?:\s+(20\d{2}))?\b", lowered)
    if month_word:
        day = int(month_word.group(1))
        raw_month = month_word.group(2)
        raw_year = month_word.group(3)
        month = None
        for stem, idx in month_map.items():
            if raw_month.startswith(stem):
                month = idx
                break
        if month is not None:
            year = int(raw_year) if raw_year else now.year
            try:
                candidate = datetime(year, month, day)
                if raw_year is None and candidate.date() < now.date():
                    candidate = datetime(year + 1, month, day)
                return candidate.strftime("%Y-%m-%d")
            except ValueError:
                return None

    return None


def _is_booking_followup(text: str) -> bool:
    lowered = text.lower()
    followup_tokens = (
        "в ",
        "на ",
        "сегодня",
        "завтра",
        "послезавтра",
        "апрел",
        "мая",
        "июн",
        "июл",
        "август",
        "сентябр",
        "октябр",
        "ноябр",
        "декабр",
        "январ",
        "феврал",
        "март",
        ":",
        ".",
        "час",
        "утра",
        "вечера",
        "дня",
        "ночи",
    )
    has_digits = re.search(r"\d", lowered) is not None
    return has_digits or any(token in lowered for token in followup_tokens)


def _match_user_car_from_text(db: Session, current_user: User, text: str) -> Car | None:
    lowered = text.lower()
    cars = db.query(Car).filter(Car.owner_id == current_user.id).all()
    for car in cars:
        brand = (car.brand or "").strip().lower()
        model = (car.model or "").strip().lower()
        if (brand and brand in lowered) or (model and model in lowered):
            return car
    if len(cars) == 1:
        return cars[0]
    return None


def _infer_service_from_text(text: str) -> tuple[str, str]:
    lowered = text.lower()
    if "диагност" in lowered:
        return "diagnostics", "Диагностика"
    if "техосмотр" in lowered or "техническ" in lowered:
        return "technical_inspection", "Технический осмотр"
    if "повреж" in lowered or "дефект" in lowered:
        return "damage_assessment", "Осмотр повреждений"
    if "регламент" in lowered or re.search(r"\bто\b", lowered):
        return "maintenance_rule", "Регламентное ТО"
    return "other_service", "Сервисная заявка"


def _build_damage_prefill_route(text: str) -> str:
    lowered = text.lower()
    damage_type = "Другое"
    if "царап" in lowered:
        damage_type = "Царапина"
    elif "вмят" in lowered:
        damage_type = "Вмятина"
    elif "скол" in lowered:
        damage_type = "Скол"
    elif "трещ" in lowered:
        damage_type = "Трещина"

    title = "Осмотр повреждений"
    if len(text.strip()) > 10:
        title = text.strip()[:80]

    params = urllib.parse.urlencode(
        {
            "damageType": damage_type,
            "title": title,
            "description": text.strip()[:300],
        }
    )
    return f"/user/damages/new?{params}"


def _has_pending_booking(chat: AssistantChat) -> bool:
    for message in reversed(chat.messages):
        if message.role == "assistant":
            return (message.intent or "") == "create_booking"
    return False


def _recent_user_text(chat: AssistantChat, limit: int = 4) -> str:
    user_messages = [m.content for m in chat.messages if m.role == "user" and m.content]
    if not user_messages:
        return ""
    return " ".join(user_messages[-limit:])


def _rule_based_plan(db: Session, current_user: User, message: str, chat: AssistantChat | None = None) -> dict[str, Any] | None:
    text = message.strip()
    lowered = text.lower()
    context_text = (lowered + " " + _recent_user_text(chat).lower()).strip() if chat else lowered

    # High-confidence fallback only when model output is missing/invalid.
    count_entities = _maybe_count_request(text, current_user)
    if count_entities:
        return {"intent": "count_entities", "data": {"entities": count_entities}, "reply": "", "action": None}

    if _request_contains_list_question(text):
        list_entity = _maybe_list_request(text)
        if list_entity == "cars":
            return {"intent": "list_cars", "data": {}, "reply": "", "action": None}
        if list_entity == "orders":
            return {"intent": "list_orders", "data": {}, "reply": "", "action": {"type": "navigate", "route": "/user/booking"}}
        if list_entity == "invoices":
            return {"intent": "list_invoices", "data": {}, "reply": "", "action": {"type": "navigate", "route": "/user/invoices"}}
        if list_entity == "damage_reports":
            return {"intent": "list_damage_reports", "data": {}, "reply": "", "action": None}
        if list_entity == "service_book":
            return {"intent": "list_service_book", "data": {}, "reply": "", "action": None}

    car_attribute = _detect_car_attribute(text)
    if car_attribute:
        matched_car = _match_scoped_car_from_text(db, current_user, text)
        payload: dict[str, Any] = {"attribute": car_attribute}
        if matched_car:
            payload["car_id"] = matched_car.id
        return {"intent": "get_car_attribute", "data": payload, "reply": "", "action": None}

    if any(token in lowered for token in ("как сервис называется", "название сервиса", "как называется сервис", "имя сервиса")):
        return {"intent": "none", "data": {}, "reply": "Сервис называется CAR API.", "action": None}

    if _request_contains_help_question(text):
        return {"intent": "show_capabilities", "data": {}, "reply": "", "action": None}

    if any(token in lowered for token in ("статус заявки", "статус заказа", "заявка ord-", "заказ ord-")):
        order_match = re.search(r"(?:ord-|заказ\s*#?|заявка\s*#?)(\d+)", lowered)
        payload: dict[str, Any] = {}
        if order_match:
            payload["order_id"] = int(order_match.group(1))
        return {"intent": "booking_status", "data": payload, "reply": "", "action": None}

    booking_tokens = ("запиши", "записать", "запись", "запланируй", "создай запись")
    if any(token in lowered for token in booking_tokens):
        service_kind, service_name = _infer_service_from_text(context_text)

        date_part = _parse_relative_date(lowered)
        time_part = _try_parse_time(lowered)
        car = _match_user_car_from_text(db, current_user, context_text)

        payload = {
            "service_kind": service_kind,
            "service_name": service_name,
        }
        if car:
            payload["car_id"] = car.id
        if date_part:
            payload["date"] = date_part
        if time_part:
            payload["time"] = time_part

        return {
            "intent": "create_booking",
            "data": payload,
            "reply": "",
            "action": {"type": "navigate", "route": "/user/booking"},
        }

    if chat and _has_pending_booking(chat) and _is_booking_followup(lowered):
        date_part = _parse_relative_date(lowered)
        time_part = _try_parse_time(lowered)

        if date_part or time_part:
            service_kind, service_name = _infer_service_from_text(context_text)
            car = _match_user_car_from_text(db, current_user, context_text)

            payload = {
                "service_kind": service_kind,
                "service_name": service_name,
            }
            if car:
                payload["car_id"] = car.id
            if date_part:
                payload["date"] = date_part
            if time_part:
                payload["time"] = time_part

            return {
                "intent": "create_booking",
                "data": payload,
                "reply": "",
                "action": {"type": "navigate", "route": "/user/booking"},
            }

    damage_intent_tokens = ("создай", "оформи", "открой", "заведи", "добавь")
    if any(token in lowered for token in damage_intent_tokens) and any(token in lowered for token in ("поврежден", "повреждение", "вмятина", "царапина", "трещина", "скол")):
        return {
            "intent": "none",
            "data": {},
            "reply": "Открыл форму заявки на повреждение. Заполните данные и прикрепите хотя бы одно фото, я помогу дальше.",
            "action": {"type": "navigate", "route": _build_damage_prefill_route(text)},
        }

    return None


def _handle_command(db: Session, current_user: User, intent: str, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    normalized = (intent or "none").strip().lower()
    if normalized == "count_entities":
        entities = data.get("entities") or []
        if isinstance(entities, str):
            entities = [entities]
        if not isinstance(entities, list):
            entities = []
        return _describe_count_entities(db, current_user, [str(entity) for entity in entities if str(entity).strip()])
    if normalized == "get_car_attribute":
        return _get_car_attribute_value(db, current_user, data)
    if normalized == "list_cars":
        return _list_user_cars(db, current_user)
    if normalized == "list_orders":
        return _list_user_orders(db, current_user)
    if normalized == "list_invoices":
        return _list_user_invoices(db, current_user)
    if normalized == "list_damage_reports":
        return _list_user_damage_reports(db, current_user)
    if normalized == "list_service_book":
        return _list_user_service_book_entries(db, current_user)
    if normalized == "list_maintenance_rules":
        return _list_user_maintenance_rules(db, current_user)
    if normalized == "get_price":
        service_kind = data.get("service_kind")
        service_name = data.get("service_name")
        return _catalog_price_text(service_kind, service_name), {"type": "price", "service_kind": service_kind, "service_name": service_name}
    if normalized == "create_booking":
        return _create_booking(db, current_user, data)
    if normalized == "booking_status":
        return _booking_status(db, current_user, data)
    if normalized == "sum_paid_invoices":
        return _sum_paid_invoices(db, current_user)
    if normalized == "show_page":
        return _show_page_action(data)
    if normalized == "show_capabilities":
        return _show_capabilities()
    return "", None


def create_chat(db: Session, current_user: User, title: str | None = None) -> AssistantChat:
    return _get_or_create_chat(db, current_user, title=title)


def update_chat(db: Session, current_user: User, chat_id: str, title: str | None = None) -> AssistantChat:
    chat = get_chat(db, current_user, chat_id)
    if title is not None:
        trimmed = title.strip()
        if trimmed:
            chat.title = trimmed[:80]
    db.commit()
    db.refresh(chat)
    return chat


def delete_chat(db: Session, current_user: User, chat_id: str) -> None:
    chat = get_chat(db, current_user, chat_id)
    db.delete(chat)
    db.commit()


def list_chats(db: Session, current_user: User) -> list[AssistantChat]:
    return (
        db.query(AssistantChat)
        .filter(AssistantChat.user_id == current_user.id)
        .order_by(AssistantChat.updated_at.desc())
        .all()
    )


def get_chat(db: Session, current_user: User, chat_id: str) -> AssistantChat:
    chat = (
        db.query(AssistantChat)
        .options(joinedload(AssistantChat.messages))
        .filter(AssistantChat.id == chat_id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    _resolve_chat_owner(db, chat, current_user)
    return chat


def send_message(db: Session, current_user: User, chat_id: str, message: str) -> dict[str, Any]:
    chat = get_chat(db, current_user, chat_id)
    if chat.user_id != current_user.id and current_user.role not in {"admin", "dev"}:
        raise HTTPException(status_code=403, detail="Forbidden")

    message_text = message.strip()
    user_message = AssistantMessage(
        chat_id=chat.id,
        role="user",
        content=message_text,
    )
    db.add(user_message)
    db.flush()

    rule_plan = _rule_based_plan(db, current_user, message_text, chat=chat)
    plan: dict[str, Any] | None = None
    model_name = "rule-based"

    api_key = current_user.ai_api_key_encrypted
    if api_key:
        decrypted_key = decrypt_secret(api_key)
        if decrypted_key:
            user_context = _build_user_context(db, current_user)
            capabilities_context = _build_site_capabilities_context()
            history = _message_history(chat)
            prompt = SYSTEM_PROMPT + "\n\n" + capabilities_context + "\n\n" + user_context
            try:
                raw_plan, model_name = _build_model_response(decrypted_key, prompt, history, message_text)
                plan = _normalize_model_plan(raw_plan)
            except HTTPException:
                plan = None
            except Exception:
                plan = None

    if (plan is None or (plan.get("intent") == "none" and not plan.get("reply"))) and rule_plan is not None:
        plan = rule_plan
        model_name = "rule-based"

    if plan is None:
        plan = {"intent": "none", "data": {}, "reply": "", "action": None}

    intent = str(plan.get("intent") or "none").strip().lower()
    data = plan.get("data") or {}
    action = plan.get("action")
    reply = str(plan.get("reply") or "").strip()

    # Repair malformed model payload for count intent to keep answers deterministic.
    if intent == "count_entities":
        detected_entities = _maybe_count_request(message_text, current_user) or []
        detected_entities = [entity for entity in detected_entities if entity in ENTITY_LABELS]

        requested_entities = data.get("entities") if isinstance(data, dict) else None
        if isinstance(requested_entities, str):
            requested_entities = [requested_entities]
        if not isinstance(requested_entities, list):
            requested_entities = []

        # If user text clearly names entities, trust that scope over model expansion.
        if detected_entities:
            valid_entities = list(dict.fromkeys(detected_entities))
        else:
            valid_entities = [str(entity) for entity in requested_entities if str(entity) in ENTITY_LABELS]

        if not valid_entities and _match_any_pattern(message_text, ENTITY_PATTERNS["cars"]):
            valid_entities = ["cars"]

        data = {**data, "entities": valid_entities} if isinstance(data, dict) else {"entities": valid_entities}

    if intent == "get_car_attribute":
        safe_data = data if isinstance(data, dict) else {}
        attribute = str(safe_data.get("attribute") or "").strip().lower()
        if attribute not in CAR_ATTRIBUTE_PATTERNS:
            detected_attribute = _detect_car_attribute(message_text)
            attribute = detected_attribute or ""

        car_id = safe_data.get("car_id")
        if car_id is None:
            matched_car = _match_scoped_car_from_text(db, current_user, message_text)
            if matched_car:
                car_id = matched_car.id

        repaired: dict[str, Any] = dict(safe_data)
        if attribute:
            repaired["attribute"] = attribute
        if car_id is not None:
            repaired["car_id"] = car_id
        data = repaired

    if intent == "list_maintenance_rules":
        safe_data = data if isinstance(data, dict) else {}
        data = safe_data

    if intent == "show_capabilities" and not reply:
        reply = ""

    command_reply = ""
    command_action = None
    if intent != "none":
        command_reply, command_action = _handle_command(db, current_user, intent, data if isinstance(data, dict) else {})
        if command_reply:
            reply = command_reply
        if command_action is not None:
            action = command_action

    if not reply:
        if intent == "none":
            reply = "Уточните, что именно нужно: список, количество, статус заявки, запись или счет."
        else:
            reply = "Не смог обработать запрос. Уточните детали."

    assistant_message = AssistantMessage(
        chat_id=chat.id,
        role="assistant",
        content=reply,
        intent=intent if intent != "none" else None,
        action_json=json.dumps(action, ensure_ascii=False) if action else None,
    )
    db.add(assistant_message)

    chat.title = chat.title if chat.title != "Новый чат" else (message_text[:40] or "Новый чат")
    chat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(chat)
    return {
        "chat": chat,
        "answer": reply,
        "intent": intent if intent != "none" else None,
        "action_json": json.dumps(action, ensure_ascii=False) if action else None,
        "provider": "gemini" if model_name != "rule-based" else "rules",
        "model": model_name,
    }
