from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import engine
from app.models import Car, Base
from app.dependencies import get_db
from app.schemas import CarCreate, CarUpdate, CarOut

router = APIRouter(prefix="/cars", tags=["cars"])

@router.get("/", response_model=list[CarOut])
def get_cars(db: Session = Depends(get_db)):
    return db.query(Car).all()

@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(404, "Car not found")
    return car

@router.post("/", response_model=CarOut, status_code=201)
def create_car(data: CarCreate, db: Session = Depends(get_db)):
    car = Car(
        brand=data.brand,
        model=data.model,
        year=data.year,
        mileage=data.mileage,
        last_service=0  # при создании новое авто
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

@router.put("/{car_id}", response_model=CarOut)
def update_car(car_id: int, data: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(404, "Car not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(404, "Car not found")
    db.delete(car)
    db.commit()
    return None


