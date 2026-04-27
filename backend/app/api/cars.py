import os
import uuid
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.models import User, Car, CarImage
from app.dependencies import get_db
from app.schemas import CarCreate, CarUpdate, CarOut, CarImageOut

router = APIRouter(prefix="/cars", tags=["cars"])

UPLOAD_DIR = "uploads/cars"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_model=list[CarOut])
def get_my_cars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Car)
        .options(joinedload(Car.owner), joinedload(Car.images))
        .filter(Car.owner_id == current_user.id)
        .all()
    )


@router.get("/admin/all", response_model=list[CarOut])
def admin_get_all_cars(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    return (
        db.query(Car)
        .options(joinedload(Car.owner), joinedload(Car.images))
        .order_by(Car.id.desc())
        .all()
    )


@router.get("/admin/{car_id}", response_model=CarOut)
def admin_get_car(
    car_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin"))
):
    car = (
        db.query(Car)
        .options(joinedload(Car.owner), joinedload(Car.images))
        .filter(Car.id == car_id)
        .first()
    )

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.get("/{car_id}", response_model=CarOut)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = (
        db.query(Car)
        .options(joinedload(Car.owner), joinedload(Car.images))
        .filter(Car.id == car_id, Car.owner_id == current_user.id)
        .first()
    )

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.post("/", response_model=CarOut, status_code=201)
def create_car(
    data: CarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = Car(
        brand=data.brand,
        model=data.model,
        vin=data.vin,
        year=data.year,
        mileage=data.mileage,
        owner_id=current_user.id
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


@router.put("/{car_id}", response_model=CarOut)
def update_car(
    car_id: int,
    data: CarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=204)
def delete_car(
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

    db.delete(car)
    db.commit()


@router.post("/{car_id}/images", response_model=list[CarImageOut], status_code=201)
def upload_car_images(
    car_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    created_images = []

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not an image")

        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image = CarImage(
            car_id=car.id,
            file_path=f"/uploads/cars/{unique_name}",
            file_name=file.filename
        )

        db.add(image)
        created_images.append(image)

    db.commit()

    for image in created_images:
        db.refresh(image)

    return created_images


@router.get("/{car_id}/images", response_model=list[CarImageOut])
def get_car_images(
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

    return db.query(CarImage).filter(CarImage.car_id == car_id).order_by(CarImage.id.desc()).all()


@router.delete("/{car_id}/images/{image_id}", status_code=204)
def delete_car_image(
    car_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    car = db.query(Car).filter(
        Car.id == car_id,
        Car.owner_id == current_user.id
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    image = db.query(CarImage).filter(
        CarImage.id == image_id,
        CarImage.car_id == car_id
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_on_disk = image.file_path.lstrip("/")
    if os.path.exists(file_on_disk):
        os.remove(file_on_disk)

    db.delete(image)
    db.commit()