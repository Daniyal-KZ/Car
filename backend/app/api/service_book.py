from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import ServiceBookEntry, Car, User
from app.schemas import ServiceBookCreate, ServiceBookOut
from app.api.auth import get_current_user
from app.api.deps import require_roles

router = APIRouter(prefix="/service-book", tags=["service-book"])


# ADMIN ENDPOINTS (must be before parametrized routes)
@router.get("/admin/all", response_model=list[ServiceBookOut])
def get_all_entries_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    return db.query(ServiceBookEntry).order_by(
        ServiceBookEntry.created_at.desc()
    ).all()

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