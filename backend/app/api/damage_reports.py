import os
import shutil
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.dependencies import get_db
from app.models import (
    Car,
    DamageReport,
    DamageReportImage,
    Invoice,
    InvoiceItem,
    ServiceBookEntry,
    ServiceOrder,
    User,
)
from app.schemas import DamageReportAnalyze, DamageReportCreate, DamageReportOut

router = APIRouter(prefix="/damage-reports", tags=["damage-reports"])

UPLOAD_DIR = "uploads/damages"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _query_report_with_relations(db: Session):
    return db.query(DamageReport).options(
        joinedload(DamageReport.photos),
        joinedload(DamageReport.car),
        joinedload(DamageReport.requester),
        joinedload(DamageReport.analyst),
    )


def _ensure_user_access(report: DamageReport, user: User):
    if user.role in {"admin", "dev", "mechanic"}:
        return
    if report.requested_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/", response_model=DamageReportOut, status_code=201)
def create_damage_report(
    data: DamageReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    car = db.query(Car).filter(Car.id == data.car_id, Car.owner_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    order = ServiceOrder(
        car_id=car.id,
        requested_by=current_user.id,
        service_kind="damage_assessment",
        service_name="Осмотр повреждений",
        status="new",
        requested_comment=data.description,
        scheduled_at=None,
    )
    db.add(order)
    db.flush()

    report = DamageReport(
        car_id=car.id,
        requested_by=current_user.id,
        service_order_id=order.id,
        title=data.title,
        damage_type=data.damage_type,
        description=data.description,
        status="new",
    )

    db.add(report)
    db.commit()

    created = _query_report_with_relations(db).filter(DamageReport.id == report.id).first()
    return created


@router.get("/my", response_model=list[DamageReportOut])
def get_my_damage_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        _query_report_with_relations(db)
        .filter(DamageReport.requested_by == current_user.id)
        .order_by(DamageReport.created_at.desc())
        .all()
    )


@router.get("/mechanic/queue", response_model=list[DamageReportOut])
def get_damage_reports_queue(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("mechanic", "admin", "dev")),
):
    return (
        _query_report_with_relations(db)
        .filter(DamageReport.status.in_(["in_review", "analyzed"]))
        .order_by(DamageReport.created_at.asc())
        .all()
    )


@router.get("/{report_id}", response_model=DamageReportOut)
def get_damage_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _query_report_with_relations(db).filter(DamageReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Damage report not found")

    _ensure_user_access(report, current_user)
    return report


@router.post("/{report_id}/photos", response_model=list[str], status_code=201)
def upload_damage_report_photos(
    report_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(DamageReport).filter(DamageReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Damage report not found")

    _ensure_user_access(report, current_user)

    stored: list[str] = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not an image")

        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        rel_path = f"/uploads/damages/{unique_name}"
        db.add(
            DamageReportImage(
                report_id=report.id,
                file_path=rel_path,
                file_name=file.filename,
            )
        )
        stored.append(rel_path)

    if report.status == "new":
        report.status = "in_review"

    db.commit()
    return stored


@router.put("/{report_id}/analysis", response_model=DamageReportOut)
def analyze_damage_report(
    report_id: int,
    data: DamageReportAnalyze,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("mechanic", "admin", "dev")),
):
    report = db.query(DamageReport).filter(DamageReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Damage report not found")

    has_photos = (
        db.query(DamageReportImage.id)
        .filter(DamageReportImage.report_id == report.id)
        .first()
    )
    if not has_photos:
        raise HTTPException(status_code=400, detail="At least one photo is required")

    first_analysis = report.status != "analyzed"

    report.status = "analyzed"
    report.severity = data.severity
    report.mechanic_analysis = data.mechanic_analysis
    report.recommendation = data.recommendation
    report.estimated_cost = data.estimated_cost
    report.analyzed_by = current_user.id
    report.analyzed_at = datetime.utcnow()

    order = None
    if report.service_order_id is not None:
        order = db.query(ServiceOrder).filter(ServiceOrder.id == report.service_order_id).first()

    if order:
        order.status = "completed"
        order.accepted_by = order.accepted_by or current_user.id
        order.accepted_at = order.accepted_at or datetime.utcnow()
        order.completed_at = datetime.utcnow()
        order.completion_comment = data.mechanic_analysis

    invoice = None
    if order:
        invoice = db.query(Invoice).filter(Invoice.order_id == order.id).first()

    if not invoice and order:
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

    if invoice:
        existing_items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        for existing in existing_items:
            db.delete(existing)

        rows = data.estimate_items
        if not rows:
            amount = float(data.estimated_cost or 0)
            rows = [
                {
                    "title": "Восстановление повреждений",
                    "quantity": 1,
                    "unit_price": amount,
                }
            ]
        else:
            rows = [item.model_dump() for item in rows]

        subtotal = 0.0
        for row in rows:
            qty = float(row.get("quantity", 1) or 1)
            unit = float(row.get("unit_price", 0) or 0)
            total = qty * unit
            subtotal += total
            db.add(
                InvoiceItem(
                    invoice_id=invoice.id,
                    title=str(row.get("title", "Работа")),
                    quantity=qty,
                    unit_price=unit,
                    total_price=total,
                )
            )

        invoice.subtotal = subtotal
        invoice.total = subtotal

    if first_analysis:
        conclusion = data.recommendation
        if data.severity:
            conclusion = f"{data.severity}: {data.recommendation}"

        db.add(
            ServiceBookEntry(
                car_id=report.car_id,
                type="damage_assessment",
                mileage=0,
                description=f"Осмотрено: {conclusion}",
                order_number=f"DR-{report.id}",
            )
        )

    db.commit()

    updated = _query_report_with_relations(db).filter(DamageReport.id == report.id).first()
    return updated
