from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import json

from app.dependencies import get_db
from app.models import ServiceBookEntry, ServiceOrder, Car, User
from app.schemas import ServiceBookCreate, ServiceBookOut, ServiceInspectionCreate
from app.api.auth import get_current_user
from app.api.deps import require_roles

router = APIRouter(prefix="/service-book", tags=["service-book"])


def _service_kind_from_description(description: str) -> str:
    lowered = description.lower()
    if "регламент" in lowered or "то" in lowered:
        return "maintenance_rule"
    if "осмотр" in lowered or "inspection" in lowered:
        return "technical_inspection"
    return "other_service"


def _extract_part(label: str, text: str) -> str | None:
    match = re.search(rf"{label}:\\s*([^|]+)", text)
    if not match:
        return None
    return match.group(1).strip()


# ADMIN ENDPOINTS (must be before parametrized routes)
@router.get("/admin/all", response_model=list[ServiceBookOut])
def get_all_entries_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    return db.query(ServiceBookEntry).order_by(
        ServiceBookEntry.created_at.desc()
    ).all()


@router.get("/admin/inspection", response_model=list[ServiceBookOut])
def get_all_inspections_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    return (
        db.query(ServiceBookEntry)
        .options(joinedload(ServiceBookEntry.car))
        .filter(ServiceBookEntry.type == "technical_inspection")
        .order_by(ServiceBookEntry.created_at.desc())
        .all()
    )


@router.get("/admin/entry/{entry_id}", response_model=ServiceBookOut)
def get_entry_admin(
    entry_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    entry = (
        db.query(ServiceBookEntry)
        .options(joinedload(ServiceBookEntry.car))
        .filter(ServiceBookEntry.id == entry_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("/admin/inspection", response_model=ServiceBookOut, status_code=201)
def create_inspection_admin(
    data: ServiceInspectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    car = db.query(Car).filter(Car.id == data.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    payload = {
        "checklist_passed": data.checklist_passed,
        "checklist_failed": data.checklist_failed,
        "conclusion": data.conclusion,
        "comment": data.comment or "",
    }

    entry = ServiceBookEntry(
        car_id=car.id,
        type="technical_inspection",
        mileage=data.mileage if data.mileage is not None else int(car.mileage or 0),
        description=json.dumps(payload, ensure_ascii=False),
        order_number=data.order_number,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/admin/entry/{entry_id}", response_model=ServiceBookOut)
def update_inspection_admin(
    entry_id: int,
    data: ServiceInspectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    entry = db.query(ServiceBookEntry).filter(ServiceBookEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    car = db.query(Car).filter(Car.id == data.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    payload = {
        "checklist_passed": data.checklist_passed,
        "checklist_failed": data.checklist_failed,
        "conclusion": data.conclusion,
        "comment": data.comment or "",
    }

    entry.car_id = car.id
    entry.type = "technical_inspection"
    entry.mileage = data.mileage if data.mileage is not None else int(car.mileage or 0)
    entry.description = json.dumps(payload, ensure_ascii=False)
    entry.order_number = data.order_number

    db.commit()
    db.refresh(entry)
    return entry

@router.get("/admin/car/{car_id}", response_model=list[ServiceBookOut])
def get_car_entries_admin(
    car_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return db.query(ServiceBookEntry).filter(
        ServiceBookEntry.car_id == car_id
    ).order_by(ServiceBookEntry.created_at.desc()).all()


@router.get("/bookings/my", response_model=list[ServiceBookOut])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(ServiceBookEntry)
        .options(joinedload(ServiceBookEntry.car))
        .join(Car, Car.id == ServiceBookEntry.car_id)
        .filter(
            Car.owner_id == current_user.id,
            ServiceBookEntry.type == "booking"
        )
        .order_by(ServiceBookEntry.created_at.desc())
        .all()
    )


@router.get("/entry/{entry_id}", response_model=ServiceBookOut)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = (
        db.query(ServiceBookEntry)
        .options(joinedload(ServiceBookEntry.car))
        .join(Car, Car.id == ServiceBookEntry.car_id)
        .filter(
            ServiceBookEntry.id == entry_id,
            Car.owner_id == current_user.id,
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


# USER ENDPOINTS
@router.post("/", response_model=ServiceBookOut)
def create_entry(
    data: ServiceBookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == data.car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    entry = ServiceBookEntry(
        car_id=data.car_id,
        type=data.type,
        mileage=data.mileage,
        description=data.description,
        order_number=data.order_number
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    if data.type == "booking":
        service_name = _extract_part("Запись на сервис", data.description) or "Сервис"
        date_part = _extract_part("Дата", data.description)
        time_part = _extract_part("Время", data.description)

        scheduled_at = None
        if date_part and time_part:
            try:
                scheduled_at = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
            except ValueError:
                scheduled_at = None

        order = ServiceOrder(
            car_id=car.id,
            requested_by=current_user.id,
            service_kind=_service_kind_from_description(data.description),
            service_name=service_name,
            status="new",
            requested_comment=_extract_part("Комментарий", data.description),
            scheduled_at=scheduled_at,
        )
        db.add(order)
        db.commit()

    return entry

@router.get("/{car_id}", response_model=list[ServiceBookOut])
def get_car_entries(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return db.query(ServiceBookEntry).filter(
        ServiceBookEntry.car_id == car_id
    ).order_by(ServiceBookEntry.created_at.desc()).all()

@router.get("/{car_id}/type/{entry_type}", response_model=list[ServiceBookOut])
def get_by_type(
    car_id: int,
    entry_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return db.query(ServiceBookEntry).filter(
        ServiceBookEntry.car_id == car_id,
        ServiceBookEntry.type == entry_type
    ).order_by(ServiceBookEntry.created_at.desc()).all()