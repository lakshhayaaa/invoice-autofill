from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.base import InvoiceFile
from backend.app.db.init_db import get_db

router=APIRouter()
@router.get("/view-invoices")
def view_uploaded_invoice(db: Session = Depends(get_db)):
    result=[]
    invoices=db.query(InvoiceFile).all()
    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found.")
    for invoice in invoices:
        result.append({
            "id": invoice.id,
            "original_filename": invoice.original_filename,
            "stored_filename": invoice.stored_filename,
            "file_type": invoice.file_type,
            "status": invoice.status,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        })
    return result