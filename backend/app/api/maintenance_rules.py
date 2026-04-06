from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.dependencies import get_db
from app.models import MaintenanceRule, MaintenanceRuleTask, Car, User
from app.schemas import MaintenanceRuleCreate, MaintenanceRuleOut, MaintenanceRuleUpdate, MaintenanceTaskCreate, MaintenanceTaskOut, MaintenanceRuleForCarOut

router = APIRouter(prefix="/maintenance-rules", tags=["maintenance-rules"])


@router.get("/", response_model=list[MaintenanceRuleOut])
def get_active_rules(db: Session = Depends(get_db)):
    return (
        db.query(MaintenanceRule)
        .options(joinedload(MaintenanceRule.tasks))
        .filter(MaintenanceRule.status == "active")
        .order_by(MaintenanceRule.id.desc())
        .all()
    )


@router.get("/admin/all", response_model=list[MaintenanceRuleOut])
def get_all_rules_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    return (
        db.query(MaintenanceRule)
        .options(joinedload(MaintenanceRule.tasks))
        .order_by(MaintenanceRule.id.desc())
        .all()
    )


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

    return rule


@router.post("/", response_model=MaintenanceRuleOut, status_code=201)
def create_rule(
    data: MaintenanceRuleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    rule = MaintenanceRule(
        title=data.title,
        brand=data.brand,
        model=data.model,
        year_from=data.year_from,
        year_to=data.year_to,
        mileage_from=data.mileage_from,
        mileage_to=data.mileage_to,
        status=data.status,
        notes=data.notes,
    )

    for index, task_data in enumerate(data.tasks or [], start=1):
        task = MaintenanceRuleTask(
            rule_id=rule.id,
            position=task_data.position if task_data.position is not None else index,
            mileage_interval=task_data.mileage_interval,
            title=task_data.title,
            description=task_data.description,
            duration_minutes=task_data.duration_minutes,
        )
        rule.tasks.append(task)

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


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

    for field, value in payload.items():
        setattr(rule, field, value)

    if tasks_data is not None:
        rule.tasks.clear()
        for index, task_data in enumerate(tasks_data, start=1):
            task = MaintenanceRuleTask(
                position=task_data.position if task_data.position is not None else index,
                title=task_data.title,
                description=task_data.description,
                duration_minutes=task_data.duration_minutes,
                price=task_data.price,
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

    # Находим подходящие регламенты по марке/модели и диапазону пробега
    rules_query = db.query(MaintenanceRule).filter(
        MaintenanceRule.brand == car.brand,
        MaintenanceRule.model == car.model,
        MaintenanceRule.status == "active"
    )

    # Фильтруем по году выпуска, если указан
    if car.year:
        rules_query = rules_query.filter(
            or_(MaintenanceRule.year_from.is_(None), MaintenanceRule.year_from <= car.year),
            or_(MaintenanceRule.year_to.is_(None), MaintenanceRule.year_to >= car.year)
        )

    # Фильтруем по пробегу, если указан
    if car.mileage is not None:
        rules_query = rules_query.filter(
            or_(MaintenanceRule.mileage_from.is_(None), MaintenanceRule.mileage_from <= car.mileage),
            or_(MaintenanceRule.mileage_to.is_(None), MaintenanceRule.mileage_to >= car.mileage)
        )

    rules = rules_query.options(joinedload(MaintenanceRule.tasks)).all()

    # Фильтруем задачи по пробегу машины и возвращаем результат
    result = []
    for rule in rules:
        # Фильтруем задачи: показываем только те, чей mileage_interval <= текущего пробега машины
        if car.mileage is not None:
            filtered_tasks = [task for task in rule.tasks if task.mileage_interval <= car.mileage]
        else:
            filtered_tasks = rule.tasks

        if filtered_tasks:  # Показываем регламент только если есть подходящие задачи
            result.append(MaintenanceRuleForCarOut(
                id=rule.id,
                title=rule.title,
                brand=rule.brand,
                model=rule.model,
                status=rule.status,
                tasks=filtered_tasks
            ))

    return result
