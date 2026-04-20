from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.dependencies import get_db
from app.core.i18n import normalize_i18n_map
from app.models import MaintenanceRule, MaintenanceRuleTask, ServiceExecutionLog, ServiceBookEntry, Car, User
from app.schemas import (
    MaintenanceRuleCreate,
    MaintenanceRuleOut,
    MaintenanceRuleUpdate,
    MaintenanceTaskCreate,
    MaintenanceTaskOut,
    MaintenanceRuleForCarOut,
    ServiceExecutionCreate,
    ServiceExecutionOut,
)

router = APIRouter(prefix="/maintenance-rules", tags=["maintenance-rules"])
OVERDUE_DAYS = 180


def _attach_rule_execution_info(rule: MaintenanceRule, executions: list[ServiceExecutionLog]):
    if executions:
        last_execution = executions[0]
        rule.last_execution_at = last_execution.performed_at
        rule.last_execution_by = last_execution.performed_by_name
        is_overdue_by_time = last_execution.performed_at < (datetime.utcnow() - timedelta(days=OVERDUE_DAYS))
        rule.execution_status = "overdue" if is_overdue_by_time else "performed"
    else:
        rule.last_execution_at = None
        rule.last_execution_by = None
        rule.execution_status = "not_performed"
    rule.executions = executions
    return rule


@router.get("/", response_model=list[MaintenanceRuleOut])
def get_active_rules(db: Session = Depends(get_db)):
    rules = (
        db.query(MaintenanceRule)
        .options(joinedload(MaintenanceRule.tasks))
        .filter(MaintenanceRule.status == "active")
        .order_by(MaintenanceRule.id.desc())
        .all()
    )

    for rule in rules:
        executions = (
            db.query(ServiceExecutionLog)
            .options(joinedload(ServiceExecutionLog.performed_by_user))
            .filter(ServiceExecutionLog.rule_id == rule.id)
            .order_by(ServiceExecutionLog.performed_at.desc())
            .all()
        )
        _attach_rule_execution_info(rule, executions)

    return rules


@router.get("/admin/all", response_model=list[MaintenanceRuleOut])
def get_all_rules_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rules = (
        db.query(MaintenanceRule)
        .options(joinedload(MaintenanceRule.tasks))
        .order_by(MaintenanceRule.id.desc())
        .all()
    )

    for rule in rules:
        executions = (
            db.query(ServiceExecutionLog)
            .options(joinedload(ServiceExecutionLog.performed_by_user))
            .filter(ServiceExecutionLog.rule_id == rule.id)
            .order_by(ServiceExecutionLog.performed_at.desc())
            .all()
        )
        _attach_rule_execution_info(rule, executions)

    return rules


@router.get("/{rule_id}", response_model=MaintenanceRuleOut)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = (
        db.query(MaintenanceRule)
        .options(joinedload(MaintenanceRule.tasks))
        .filter(MaintenanceRule.id == rule_id)
        .first()
    )

    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    executions = (
        db.query(ServiceExecutionLog)
        .options(joinedload(ServiceExecutionLog.performed_by_user))
        .filter(ServiceExecutionLog.rule_id == rule_id)
        .order_by(ServiceExecutionLog.performed_at.desc())
        .all()
    )

    return _attach_rule_execution_info(rule, executions)


@router.post("/", response_model=MaintenanceRuleOut, status_code=201)
def create_rule(
    data: MaintenanceRuleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rule = MaintenanceRule(
        title=data.title,
        title_i18n=normalize_i18n_map(data.title_i18n, data.title),
        brand=data.brand,
        model=data.model,
        year_from=data.year_from,
        year_to=data.year_to,
        mileage_from=data.mileage_from,
        mileage_to=data.mileage_to,
        status=data.status,
        notes=data.notes,
        notes_i18n=normalize_i18n_map(data.notes_i18n, data.notes) if data.notes is not None else data.notes_i18n,
    )

    for index, task_data in enumerate(data.tasks or [], start=1):
        task = MaintenanceRuleTask(
            rule_id=rule.id,
            position=task_data.position if task_data.position is not None else index,
            mileage_interval=task_data.mileage_interval,
            title=task_data.title,
            title_i18n=normalize_i18n_map(task_data.title_i18n, task_data.title),
            description=task_data.description,
            description_i18n=normalize_i18n_map(task_data.description_i18n, task_data.description) if task_data.description is not None else task_data.description_i18n,
            duration_minutes=task_data.duration_minutes,
        )
        rule.tasks.append(task)

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}/executions", response_model=list[ServiceExecutionOut])
def get_rule_executions(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(MaintenanceRule).filter(MaintenanceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    executions = (
        db.query(ServiceExecutionLog)
        .options(joinedload(ServiceExecutionLog.performed_by_user))
        .filter(ServiceExecutionLog.rule_id == rule_id)
        .order_by(ServiceExecutionLog.performed_at.desc())
        .all()
    )

    return executions


@router.post("/{rule_id}/executions", response_model=ServiceExecutionOut, status_code=201)
def create_rule_execution(
    rule_id: int,
    data: ServiceExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("mechanic", "admin"))
):
    rule = db.query(MaintenanceRule).filter(MaintenanceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    task = None
    if data.task_id is not None:
        task = db.query(MaintenanceRuleTask).filter(
            MaintenanceRuleTask.id == data.task_id,
            MaintenanceRuleTask.rule_id == rule_id,
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found for this maintenance rule")

    car = None
    if data.related_object_type == "car":
        car = db.query(Car).filter(Car.id == data.related_object_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

    execution = ServiceExecutionLog(
        rule_id=rule_id,
        task_id=data.task_id,
        performed_by=current_user.id,
        performed_by_name=current_user.username,
        service_type="maintenance_rule",
        related_object_type=data.related_object_type,
        related_object_id=data.related_object_id,
        comment=data.comment,
    )

    db.add(execution)

    # Keep service-book history in sync with maintenance execution logs.
    if car is not None:
        details = [f"Выполнен регламент: {rule.title}"]
        if task is not None:
            details.append(f"Работа: {task.title}")
        if data.comment:
            details.append(f"Комментарий: {data.comment}")

        service_book_entry = ServiceBookEntry(
            car_id=car.id,
            type="maintenance_rule_execution",
            mileage=int(car.mileage or 0),
            description=" | ".join(details),
            order_number=None,
        )
        db.add(service_book_entry)

    db.commit()
    db.refresh(execution)
    return execution


@router.get("/car/{car_id}/executions", response_model=list[ServiceExecutionOut])
def get_car_executions(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if current_user.role != "admin" and car.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Car not found")

    executions = (
        db.query(ServiceExecutionLog)
        .options(joinedload(ServiceExecutionLog.performed_by_user))
        .filter(
            ServiceExecutionLog.related_object_type == "car",
            ServiceExecutionLog.related_object_id == car_id,
            ServiceExecutionLog.service_type == "maintenance_rule"
        )
        .order_by(ServiceExecutionLog.performed_at.desc())
        .all()
    )

    return executions


@router.put("/{rule_id}", response_model=MaintenanceRuleOut)
def update_rule(
    rule_id: int,
    data: MaintenanceRuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rule = db.query(MaintenanceRule).filter(MaintenanceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    payload = data.model_dump(exclude_unset=True)
    tasks_data = payload.pop('tasks', None)

    allowed_fields = {
        "title",
        "title_i18n",
        "brand",
        "model",
        "year_from",
        "year_to",
        "mileage_from",
        "mileage_to",
        "status",
        "notes",
        "notes_i18n",
    }
    for field, value in payload.items():
        if field in allowed_fields:
            setattr(rule, field, value)

    if payload.get("title") is not None or payload.get("title_i18n") is not None:
        rule.title_i18n = normalize_i18n_map(payload.get("title_i18n"), rule.title)

    if payload.get("notes") is not None or payload.get("notes_i18n") is not None:
        rule.notes_i18n = normalize_i18n_map(payload.get("notes_i18n"), rule.notes)

    if tasks_data is not None:
        rule.tasks.clear()
        for index, task_data in enumerate(tasks_data, start=1):
            task = MaintenanceRuleTask(
                position=task_data.get("position") if task_data.get("position") is not None else index,
                title=task_data.get("title"),
                title_i18n=normalize_i18n_map(task_data.get("title_i18n"), task_data.get("title")),
                description=task_data.get("description"),
                description_i18n=normalize_i18n_map(task_data.get("description_i18n"), task_data.get("description")) if task_data.get("description") is not None else task_data.get("description_i18n"),
                duration_minutes=task_data.get("duration_minutes"),
                unit_price=task_data.get("unit_price", 0),
            )
            rule.tasks.append(task)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rule = db.query(MaintenanceRule).filter(MaintenanceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    db.delete(rule)
    db.commit()


# Task management endpoints
@router.post("/{rule_id}/tasks", response_model=MaintenanceTaskOut)
def add_task_to_rule(
    rule_id: int,
    task_data: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rule = db.query(MaintenanceRule).filter(MaintenanceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Maintenance rule not found")

    # Calculate position if not provided
    if task_data.position is None:
        max_position = db.query(func.max(MaintenanceRuleTask.position)).filter(
            MaintenanceRuleTask.rule_id == rule_id
        ).scalar() or 0
        task_data.position = max_position + 1

    task = MaintenanceRuleTask(
        rule_id=rule_id,
        **task_data.model_dump()
    )
    task.title_i18n = normalize_i18n_map(task_data.title_i18n, task_data.title)
    task.description_i18n = normalize_i18n_map(task_data.description_i18n, task_data.description) if task_data.description is not None else task_data.description_i18n

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{rule_id}/tasks/{task_id}")
def remove_task_from_rule(
    rule_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    task = db.query(MaintenanceRuleTask).filter(
        MaintenanceRuleTask.id == task_id,
        MaintenanceRuleTask.rule_id == rule_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


@router.put("/{rule_id}/tasks/{task_id}", response_model=MaintenanceTaskOut)
def update_task_in_rule(
    rule_id: int,
    task_id: int,
    task_data: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    task = db.query(MaintenanceRuleTask).filter(
        MaintenanceRuleTask.id == task_id,
        MaintenanceRuleTask.rule_id == rule_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    task.title_i18n = normalize_i18n_map(task_data.title_i18n, task.title)
    if task_data.description is not None or task_data.description_i18n is not None:
        task.description_i18n = normalize_i18n_map(task_data.description_i18n, task.description)

    db.commit()
    db.refresh(task)
    return task


@router.get("/car/{car_id}", response_model=list[MaintenanceRuleForCarOut])
def get_rules_for_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if current_user.role != "admin" and car.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Car not found")

    brand = car.brand.strip().lower()
    model = car.model.strip().lower()

    # Находим подходящие регламенты по марке/модели.
    # Если строгого совпадения среди active нет, используем мягкий fallback,
    # чтобы старые/измененные данные все равно отображались пользователю.
    def _base_query(include_only_active: bool = True):
        q = db.query(MaintenanceRule).filter(
            func.lower(func.trim(MaintenanceRule.brand)) == brand,
            func.lower(func.trim(MaintenanceRule.model)) == model,
        )
        if include_only_active:
            q = q.filter(MaintenanceRule.status == "active")
        return q

    rules_query = _base_query(include_only_active=True)

    # Фильтруем по году выпуска, если указан
    if car.year:
        rules_query = rules_query.filter(
            or_(MaintenanceRule.year_from.is_(None), MaintenanceRule.year_from <= car.year),
            or_(MaintenanceRule.year_to.is_(None), MaintenanceRule.year_to >= car.year)
        )

    # Не фильтруем по mileage_to на этапе выборки регламентов:
    # регламент и его история должны оставаться видимыми даже после
    # превышения верхней границы пробега.

    rules = rules_query.options(joinedload(MaintenanceRule.tasks)).all()

    if not rules:
        fallback_query = _base_query(include_only_active=False)

        if car.year:
            fallback_query = fallback_query.filter(
                or_(MaintenanceRule.year_from.is_(None), MaintenanceRule.year_from <= car.year),
                or_(MaintenanceRule.year_to.is_(None), MaintenanceRule.year_to >= car.year)
            )

        # Аналогично, во fallback не скрываем регламент по mileage_to.

        rules = fallback_query.options(joinedload(MaintenanceRule.tasks)).all()

    # Возвращаем все задачи регламента, а статус считаем по текущему пробегу и истории фиксаций.
    result = []
    for rule in rules:
        if not rule.tasks:
            continue

        due_tasks = []
        if car.mileage is not None:
            due_tasks = [task for task in rule.tasks if task.mileage_interval <= car.mileage]

        executions = (
            db.query(ServiceExecutionLog)
            .options(joinedload(ServiceExecutionLog.performed_by_user))
            .filter(
                ServiceExecutionLog.rule_id == rule.id,
                ServiceExecutionLog.related_object_type == "car",
                ServiceExecutionLog.related_object_id == car_id,
            )
            .order_by(ServiceExecutionLog.performed_at.desc())
            .all()
        )

        executed_task_ids = {execution.task_id for execution in executions if execution.task_id is not None}
        pending_due_tasks = [task for task in due_tasks if task.id not in executed_task_ids]
        has_mileage_overdue = (
            car.mileage is not None
            and any(task.mileage_interval < car.mileage for task in pending_due_tasks)
        )

        if executions:
            last_execution = executions[0]
            last_execution_at = last_execution.performed_at
            last_execution_by = last_execution.performed_by_name
            if pending_due_tasks:
                is_overdue_by_time = last_execution.performed_at < (datetime.utcnow() - timedelta(days=OVERDUE_DAYS))
                execution_status = "overdue" if (is_overdue_by_time or has_mileage_overdue) else "not_performed"
            else:
                execution_status = "performed"
        elif pending_due_tasks:
            execution_status = "overdue" if has_mileage_overdue else "not_performed"
            last_execution_at = None
            last_execution_by = None
        else:
            execution_status = "planned"
            last_execution_at = None
            last_execution_by = None

        result.append(MaintenanceRuleForCarOut(
            id=rule.id,
            title=rule.title,
            brand=rule.brand,
            model=rule.model,
            status=rule.status,
            tasks=rule.tasks,
            last_execution_at=last_execution_at,
            last_execution_by=last_execution_by,
            execution_status=execution_status,
        ))

    return result
