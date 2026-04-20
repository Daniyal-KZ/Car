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
from sqlalchemy.orm import Session, joinedload

from app.core.security import decrypt_secret
from app.models import Car, Invoice, ServiceOrder, AssistantChat, AssistantMessage, User

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
You must use the provided user context as the source of truth.
You must not say you have no access to the user's data if it is present in the context.
Output JSON only with this schema:
{
  "reply": "short helpful answer in Russian",
    "intent": "none|list_cars|list_orders|get_price|create_booking|booking_status|show_page",
  "data": {},
  "action": null or {"type": "navigate", "route": "/path"}
}
Rules:
- If the user asks about cars, orders, invoices, or schedule, use the context.
- If action is needed, set intent and data clearly.
- If there is not enough data, ask one short clarifying question.
- Do not add markdown fences.
"""


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
    cars = (
        db.query(Car)
        .filter(Car.owner_id == current_user.id)
        .order_by(Car.id.desc())
        .limit(10)
        .all()
    )

    orders = (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.car))
        .filter(ServiceOrder.requested_by == current_user.id)
        .order_by(ServiceOrder.created_at.desc())
        .limit(10)
        .all()
    )

    invoices = (
        db.query(Invoice)
        .join(ServiceOrder, ServiceOrder.id == Invoice.order_id)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(ServiceOrder.requested_by == current_user.id)
        .order_by(Invoice.created_at.desc())
        .limit(10)
        .all()
    )

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

    return (
        f"User context:\n"
        f"- User ID: {current_user.id}\n"
        f"- Username: {current_user.username}\n"
        f"- Role: {current_user.role}\n\n"
        f"Cars:\n" + "\n".join(car_lines) + "\n\n"
        f"Orders:\n" + "\n".join(order_lines) + "\n\n"
        f"Invoices:\n" + "\n".join(invoice_lines)
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
    cars = (
        db.query(Car)
        .filter(Car.owner_id == current_user.id)
        .order_by(Car.id.desc())
        .all()
    )
    if not cars:
        return "У вас пока нет машин в гараже.", None

    lines = []
    for car in cars:
        lines.append(
            f"{car.brand} {car.model}, {car.year} год, пробег {int(car.mileage or 0):,} км, VIN {car.vin or 'не указан'}"
            .replace(",", " ")
        )
    return "У вас есть: " + "; ".join(lines) + ".", {"cars": [car.id for car in cars]}


def _create_booking(db: Session, current_user: User, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    car_id = data.get("car_id")
    cars = db.query(Car).filter(Car.owner_id == current_user.id).order_by(Car.id.asc()).all()
    car: Car | None = None

    if car_id is not None:
        car = db.query(Car).filter(Car.id == int(car_id), Car.owner_id == current_user.id).first()
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


def _list_user_orders(db: Session, current_user: User) -> tuple[str, dict[str, Any] | None]:
    orders = (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.car))
        .filter(ServiceOrder.requested_by == current_user.id)
        .order_by(ServiceOrder.created_at.desc())
        .limit(10)
        .all()
    )
    if not orders:
        return "У вас пока нет заявок в сервис.", None

    lines: list[str] = []
    for order in orders:
        car_name = f"{order.car.brand} {order.car.model}" if order.car else f"car #{order.car_id}"
        when = order.scheduled_at.strftime("%d.%m.%Y %H:%M") if order.scheduled_at else "время не указано"
        lines.append(f"ORD-{order.id}: {order.service_name}, {order.status}, {car_name}, {when}")

    return "Ваши заявки: " + "; ".join(lines) + ".", {"order_ids": [order.id for order in orders]}


def _booking_status(db: Session, current_user: User, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    order_id = data.get("order_id")
    if order_id is None:
        return _list_user_orders(db, current_user)

    order = (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.car))
        .filter(ServiceOrder.id == int(order_id), ServiceOrder.requested_by == current_user.id)
        .first()
    )
    if not order:
        return "Не нашел такую заявку. Проверьте номер заказа.", None

    car_name = f"{order.car.brand} {order.car.model}" if order.car else f"car #{order.car_id}"
    when = order.scheduled_at.strftime("%d.%m.%Y %H:%M") if order.scheduled_at else "время не указано"
    return (
        f"Заявка ORD-{order.id}: статус {order.status}, услуга {order.service_name}, авто {car_name}, дата {when}.",
        {"order_id": order.id, "status": order.status, "route": f"/user/booking/{order.id}"},
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

    return None


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

    if any(token in lowered for token in ("мои машины", "мой гараж", "какие машины", "список машин")):
        return {"intent": "list_cars", "data": {}, "reply": "", "action": None}

    if any(token in lowered for token in ("мои заявки", "мои записи", "список заявок", "статус заявок")):
        return {"intent": "list_orders", "data": {}, "reply": "", "action": {"type": "navigate", "route": "/user/booking"}}

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

    if chat and _has_pending_booking(chat):
        date_part = _parse_relative_date(lowered) or _parse_relative_date(context_text)
        time_part = _try_parse_time(lowered) or _try_parse_time(context_text)

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

    if any(token in lowered for token in ("поврежден", "повреждение", "вмятина", "царапина", "трещина", "скол")):
        return {
            "intent": "none",
            "data": {},
            "reply": "Открыл форму заявки на повреждение. Заполните данные и прикрепите хотя бы одно фото, я помогу дальше.",
            "action": {"type": "navigate", "route": _build_damage_prefill_route(text)},
        }

    return None


def _handle_command(db: Session, current_user: User, intent: str, data: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    normalized = (intent or "none").strip().lower()
    if normalized == "list_cars":
        return _list_user_cars(db, current_user)
    if normalized == "list_orders":
        return _list_user_orders(db, current_user)
    if normalized == "get_price":
        service_kind = data.get("service_kind")
        service_name = data.get("service_name")
        return _catalog_price_text(service_kind, service_name), {"type": "price", "service_kind": service_kind, "service_name": service_name}
    if normalized == "create_booking":
        return _create_booking(db, current_user, data)
    if normalized == "booking_status":
        return _booking_status(db, current_user, data)
    if normalized == "show_page":
        return _show_page_action(data)
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

    user_message = AssistantMessage(
        chat_id=chat.id,
        role="user",
        content=message.strip(),
    )
    db.add(user_message)
    db.flush()

    api_key = current_user.ai_api_key_encrypted
    if not api_key:
        raise HTTPException(status_code=400, detail="AI API key is not configured")
    decrypted_key = decrypt_secret(api_key)
    if not decrypted_key:
        raise HTTPException(status_code=500, detail="AI API key decrypt failed")

    user_context = _build_user_context(db, current_user)
    history = _message_history(chat)
    prompt = SYSTEM_PROMPT + "\n\n" + user_context

    plan, model_name = _build_model_response(decrypted_key, prompt, history, message.strip())
    rule_plan = _rule_based_plan(db, current_user, message.strip(), chat=chat)
    if rule_plan:
        plan = {**plan, **rule_plan}
    intent = str(plan.get("intent") or "none").strip().lower()
    data = plan.get("data") or {}
    action = plan.get("action")
    reply = str(plan.get("reply") or "").strip()

    command_reply = ""
    command_action = None
    if intent != "none":
        command_reply, command_action = _handle_command(db, current_user, intent, data if isinstance(data, dict) else {})
        if command_reply:
            reply = command_reply
        if command_action is not None:
            action = command_action

    if not reply:
        reply = "Не смог сформировать ответ. Попробуйте переформулировать вопрос."

    assistant_message = AssistantMessage(
        chat_id=chat.id,
        role="assistant",
        content=reply,
        intent=intent if intent != "none" else None,
        action_json=json.dumps(action, ensure_ascii=False) if action else None,
    )
    db.add(assistant_message)

    chat.title = chat.title if chat.title != "Новый чат" else (message.strip()[:40] or "Новый чат")
    chat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(chat)
    return {
        "chat": chat,
        "answer": reply,
        "intent": intent if intent != "none" else None,
        "action_json": json.dumps(action, ensure_ascii=False) if action else None,
        "provider": "gemini",
        "model": model_name,
    }
