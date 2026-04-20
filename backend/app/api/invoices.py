from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.api.auth import get_current_user
from app.api.deps import require_roles
from app.dependencies import get_db
from app.models import Invoice, InvoiceItem, ServiceOrder, User
from app.schemas import InvoiceAdminUpdate, InvoiceOut

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/my", response_model=list[InvoiceOut])
def get_my_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Invoice)
        .join(ServiceOrder, ServiceOrder.id == Invoice.order_id)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(ServiceOrder.requested_by == current_user.id)
        .filter(Invoice.status.in_(["sent", "unpaid", "paid"]))
        .order_by(Invoice.created_at.desc())
        .all()
    )


@router.get("/admin/all", response_model=list[InvoiceOut])
def get_all_invoices_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "dev")),
):
    return (
        db.query(Invoice)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .order_by(Invoice.created_at.desc())
        .all()
    )


@router.get("/admin/{invoice_id}", response_model=InvoiceOut)
def get_invoice_admin(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "dev")),
):
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/admin/{invoice_id}", response_model=InvoiceOut)
def update_invoice_admin(
    invoice_id: int,
    data: InvoiceAdminUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "dev")),
):
    invoice = (
        db.query(Invoice)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # После отправки/оплаты смета должна быть неизменяемой.
    if invoice.status in {"sent", "paid"}:
        raise HTTPException(status_code=409, detail="Invoice is locked and cannot be edited")

    if data.items:
        invoice.items.clear()

        subtotal = 0.0
        for row in data.items:
            qty = float(row.quantity or 1)
            unit = float(row.unit_price or 0)
            total = qty * unit
            subtotal += total

            invoice.items.append(
                InvoiceItem(
                    title=row.title,
                    quantity=qty,
                    unit_price=unit,
                    total_price=total,
                )
            )

        invoice.subtotal = subtotal
        invoice.total = subtotal

    if data.status:
        invoice.status = data.status

    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/admin/{invoice_id}/send", response_model=InvoiceOut)
def send_invoice_to_user(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "dev")),
):
    invoice = db.query(Invoice).options(joinedload(Invoice.items), joinedload(Invoice.order)).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")
    if invoice.status == "sent":
        raise HTTPException(status_code=400, detail="Invoice already sent")
    if not invoice.items:
        raise HTTPException(status_code=400, detail="Invoice has no items")

    invoice.status = "sent"
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .join(ServiceOrder, ServiceOrder.id == Invoice.order_id)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if current_user.role not in {"admin", "dev", "mechanic"} and invoice.order.requested_by != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return invoice


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceOut)
def mark_invoice_paid(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .join(ServiceOrder, ServiceOrder.id == Invoice.order_id)
        .options(joinedload(Invoice.items), joinedload(Invoice.order))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    is_admin = current_user.role in {"admin", "dev"}
    is_owner = bool(invoice.order and invoice.order.requested_by == current_user.id)
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Forbidden")

    if invoice.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")
    if invoice.status == "draft":
        raise HTTPException(status_code=400, detail="Invoice must be sent before payment")

    invoice.status = "paid"
    invoice.paid_at = datetime.utcnow()

    db.commit()
    db.refresh(invoice)
    return invoice
