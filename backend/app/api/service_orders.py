from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.core.i18n import normalize_i18n_map, normalize_lang
from app.dependencies import get_db
from app.models import (
    Car,
    Invoice,
    InvoiceItem,
    MaintenanceRule,
    ServiceBookEntry,
    ServiceExecutionLog,
    ServiceOrder,
    User,
)
from app.schemas import (
    InvoiceOut,
    ServiceOrderAccept,
    ServiceOrderComplete,
    ServiceOrderCreate,
    ServiceOrderDetailsOut,
)

router = APIRouter(prefix="/service-orders", tags=["service-orders"])


@router.get("/catalog")
def get_service_catalog(
    x_lang: str | None = Header(default=None),
    accept_language: str | None = Header(default=None),
):
    lang = normalize_lang(x_lang, accept_language)

    names = {
        "maintenance_rule": {"ru": "Регламентное ТО", "en": "Scheduled Maintenance", "kz": "Жоспарлы техникалық қызмет"},
        "diagnostics": {"ru": "Диагностика", "en": "Diagnostics", "kz": "Диагностика"},
        "technical_inspection": {"ru": "Технический осмотр", "en": "Technical Inspection", "kz": "Техникалық байқау"},
        "damage_assessment": {"ru": "Осмотр повреждений", "en": "Damage Assessment", "kz": "Зақымдарды тексеру"},
    }

    descriptions = {
        "maintenance_rule": {
            "ru": "Плановое обслуживание по регламенту",
            "en": "Scheduled maintenance by service intervals",
            "kz": "Регламент бойынша жоспарлы қызмет",
        },
        "diagnostics": {
            "ru": "Комплексная диагностика автомобиля",
            "en": "Full vehicle diagnostics",
            "kz": "Көліктің кешенді диагностикасы",
        },
        "technical_inspection": {
            "ru": "Проверка автомобиля по требованиям техосмотра",
            "en": "Vehicle check for inspection requirements",
            "kz": "Техбайқау талаптарына сай тексеру",
        },
        "damage_assessment": {
            "ru": "Осмотр, фотофиксация и оценка повреждений",
            "en": "Inspection, photo capture and damage estimate",
            "kz": "Зақымдарды қарау, фотофиксация және бағалау",
        },
    }

    return [
        {
            "code": "maintenance_rule",
            "name": names["maintenance_rule"].get(lang, names["maintenance_rule"]["ru"]),
            "description": descriptions["maintenance_rule"].get(lang, descriptions["maintenance_rule"]["ru"]),
        },
        {
            "code": "diagnostics",
            "name": names["diagnostics"].get(lang, names["diagnostics"]["ru"]),
            "description": descriptions["diagnostics"].get(lang, descriptions["diagnostics"]["ru"]),
        },
        {
            "code": "technical_inspection",
            "name": names["technical_inspection"].get(lang, names["technical_inspection"]["ru"]),
            "description": descriptions["technical_inspection"].get(lang, descriptions["technical_inspection"]["ru"]),
        },
        {
            "code": "damage_assessment",
            "name": names["damage_assessment"].get(lang, names["damage_assessment"]["ru"]),
            "description": descriptions["damage_assessment"].get(lang, descriptions["damage_assessment"]["ru"]),
        },
    ]


def _detect_service_kind(name: str) -> str:
    lowered = name.lower()
    if "регламент" in lowered or "то" in lowered:
        return "maintenance_rule"
    if "диагност" in lowered:
        return "diagnostics"
    if "повреж" in lowered or "дефект" in lowered:
        return "damage_assessment"
    if "осмотр" in lowered or "inspection" in lowered or "техосмотр" in lowered:
        return "technical_inspection"
    return "other_service"


def _default_estimate_for(kind: str, name: str) -> list[dict]:
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


def _find_rule_for_car(db: Session, car: Car):
    query = db.query(MaintenanceRule).filter(
        MaintenanceRule.status == "active",
        MaintenanceRule.brand.ilike(car.brand.strip()),
        MaintenanceRule.model.ilike(car.model.strip()),
    )

    if car.year:
        query = query.filter(
            or_(MaintenanceRule.year_from.is_(None), MaintenanceRule.year_from <= car.year),
            or_(MaintenanceRule.year_to.is_(None), MaintenanceRule.year_to >= car.year),
        )

    # Do not hard-filter by mileage_to here. Older interval rules should remain
    # visible/applicable so overdue work does not disappear from UI flows.

    return query.order_by(MaintenanceRule.id.desc()).first()


@router.post("/", response_model=ServiceOrderDetailsOut, status_code=201)
def create_service_order(
    data: ServiceOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    car = db.query(Car).filter(Car.id == data.car_id, Car.owner_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    service_kind = data.service_kind or _detect_service_kind(data.service_name)

    order = ServiceOrder(
        car_id=car.id,
        requested_by=current_user.id,
        service_kind=service_kind,
        service_name=data.service_name,
        service_name_i18n=normalize_i18n_map(data.service_name_i18n, data.service_name),
        status="new",
        requested_comment=data.requested_comment,
        requested_comment_i18n=normalize_i18n_map(data.requested_comment_i18n, data.requested_comment)
        if data.requested_comment is not None else data.requested_comment_i18n,
        scheduled_at=data.scheduled_at,
    )

    db.add(order)
    db.commit()

    order = (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.car),
            joinedload(ServiceOrder.requester),
            joinedload(ServiceOrder.mechanic),
        )
        .filter(ServiceOrder.id == order.id)
        .first()
    )
    return order


@router.get("/my", response_model=list[ServiceOrderDetailsOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.car),
            joinedload(ServiceOrder.requester),
            joinedload(ServiceOrder.mechanic),
        )
        .filter(ServiceOrder.requested_by == current_user.id)
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )


@router.get("/mechanic/queue", response_model=list[ServiceOrderDetailsOut])
def get_mechanic_queue(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("mechanic", "admin", "dev")),
):
    return (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.car),
            joinedload(ServiceOrder.requester),
            joinedload(ServiceOrder.mechanic),
        )
        .filter(ServiceOrder.status.in_(["new", "accepted", "in_progress"]))
        .order_by(ServiceOrder.created_at.asc())
        .all()
    )


@router.get("/{order_id}", response_model=ServiceOrderDetailsOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.car),
            joinedload(ServiceOrder.requester),
            joinedload(ServiceOrder.mechanic),
        )
        .filter(ServiceOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    is_owner = order.requested_by == current_user.id
    is_worker = current_user.role in {"mechanic", "admin", "dev"}
    if not is_owner and not is_worker:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Если это заявка на регламентное ТО, найти и приложить регламент
    if order.service_kind == "maintenance_rule" and order.car:
        rule = _find_rule_for_car(db, order.car)
        if rule:
            # Загрузить задачи в правило
            db.refresh(rule, ["tasks"])

            car_mileage = int(order.car.mileage or 0)
            due_tasks = [task for task in rule.tasks if task.mileage_interval <= car_mileage]

            executed_task_ids = {
                task_id
                for (task_id,) in (
                    db.query(ServiceExecutionLog.task_id)
                    .filter(
                        ServiceExecutionLog.rule_id == rule.id,
                        ServiceExecutionLog.related_object_type == "car",
                        ServiceExecutionLog.related_object_id == order.car.id,
                        ServiceExecutionLog.task_id.isnot(None),
                    )
                    .all()
                )
                if task_id is not None
            }

            # Для механика показываем только актуальные невыполненные пункты.
            if current_user.role in {"mechanic", "admin", "dev"}:
                rule.tasks = [task for task in due_tasks if task.id not in executed_task_ids]

            order.maintenance_rule = rule

    return order


@router.post("/{order_id}/accept", response_model=ServiceOrderDetailsOut)
def accept_order(
    order_id: int,
    _: ServiceOrderAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("mechanic", "admin", "dev")),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Order already completed")

    if order.accepted_by and order.accepted_by != current_user.id and current_user.role not in {"admin", "dev"}:
        raise HTTPException(status_code=409, detail="Order already accepted by another mechanic")

    order.accepted_by = current_user.id
    order.accepted_at = order.accepted_at or datetime.utcnow()
    order.status = "accepted"

    db.commit()

    return (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.car),
            joinedload(ServiceOrder.requester),
            joinedload(ServiceOrder.mechanic),
        )
        .filter(ServiceOrder.id == order_id)
        .first()
    )


@router.post("/{order_id}/complete", response_model=InvoiceOut)
def complete_order(
    order_id: int,
    data: ServiceOrderComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("mechanic", "admin", "dev")),
):
    order = (
        db.query(ServiceOrder)
        .options(joinedload(ServiceOrder.car), joinedload(ServiceOrder.invoice))
        .filter(ServiceOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "completed":
        raise HTTPException(status_code=400, detail="Order already completed")

    if order.accepted_by and order.accepted_by != current_user.id and current_user.role not in {"admin", "dev"}:
        raise HTTPException(status_code=409, detail="Order assigned to another mechanic")

    order.accepted_by = order.accepted_by or current_user.id
    order.accepted_at = order.accepted_at or datetime.utcnow()
    order.status = "completed"
    order.completed_at = datetime.utcnow()
    order.completion_comment = data.completion_comment
    if data.completion_comment is not None or data.completion_comment_i18n is not None:
        order.completion_comment_i18n = normalize_i18n_map(data.completion_comment_i18n, data.completion_comment)

    car = order.car
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    estimate_items = data.estimate_items or []
    if not estimate_items:
        estimate_items = _default_estimate_for(order.service_kind, order.service_name)
    else:
        estimate_items = [item.model_dump() for item in estimate_items]

    selected_task_ids = {
        int(row.get("task_id"))
        for row in estimate_items
        if row.get("task_id") is not None
    }

    if order.service_kind == "maintenance_rule":
        rule = _find_rule_for_car(db, car)
        executed_count = 0

        if rule:
            db.refresh(rule, ["tasks"])
            valid_task_ids = {task.id for task in rule.tasks}
            selected_task_ids = {task_id for task_id in selected_task_ids if task_id in valid_task_ids}

            already_executed_task_ids = {
                task_id
                for (task_id,) in (
                    db.query(ServiceExecutionLog.task_id)
                    .filter(
                        ServiceExecutionLog.rule_id == rule.id,
                        ServiceExecutionLog.related_object_type == "car",
                        ServiceExecutionLog.related_object_id == car.id,
                        ServiceExecutionLog.task_id.isnot(None),
                    )
                    .all()
                )
                if task_id is not None
            }

            for task_id in sorted(selected_task_ids - already_executed_task_ids):
                db.add(
                    ServiceExecutionLog(
                        rule_id=rule.id,
                        task_id=task_id,
                        performed_by=current_user.id,
                        performed_by_name=current_user.username,
                        service_type="maintenance_rule",
                        related_object_type="car",
                        related_object_id=car.id,
                        comment=data.completion_comment or f"Работа по регламенту выполнена по заявке #{order.id}",
                    )
                )
                executed_count += 1

            if executed_count == 0:
                db.add(
                    ServiceExecutionLog(
                        rule_id=rule.id,
                        task_id=None,
                        performed_by=current_user.id,
                        performed_by_name=current_user.username,
                        service_type="maintenance_rule",
                        related_object_type="car",
                        related_object_id=car.id,
                        comment=data.completion_comment or f"Регламентное ТО выполнено по заявке #{order.id}",
                    )
                )

        service_book_type = "maintenance_rule_execution"
    elif order.service_kind == "technical_inspection":
        service_book_type = "technical_inspection"
        executed_count = 0
    else:
        service_book_type = "service_completed"
        executed_count = 0

    service_book_description = f"Заявка #{order.id}: {order.service_name}"
    if order.service_kind == "maintenance_rule" and executed_count > 0:
        service_book_description += f" | Выполнено работ: {executed_count}"
    if data.completion_comment:
        service_book_description += f" | Комментарий: {data.completion_comment}"

    db.add(
        ServiceBookEntry(
            car_id=car.id,
            type=service_book_type,
            mileage=int(car.mileage or 0),
            description=service_book_description,
            order_number=f"ORD-{order.id}",
        )
    )

    subtotal = 0.0
    invoice = Invoice(
        order_id=order.id,
        invoice_number=f"INV-TMP-{int(datetime.utcnow().timestamp())}",
        status="draft",
        currency="KZT",
        subtotal=0,
        total=0,
    )
    db.add(invoice)
    db.flush()

    invoice.invoice_number = f"INV-{invoice.id:06d}"

    for row in estimate_items:
        quantity = float(row.get("quantity", 1) or 1)
        unit_price = float(row.get("unit_price", 0) or 0)
        total_price = quantity * unit_price
        subtotal += total_price

        db.add(
            InvoiceItem(
                invoice_id=invoice.id,
                title=str(row.get("title", "Услуга")),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    invoice.subtotal = subtotal
    invoice.total = subtotal

    db.commit()

    result = db.query(Invoice).options(joinedload(Invoice.items)).filter(Invoice.id == invoice.id).first()
    return result
