import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.init_db import get_db
from backend.app.db.base import InvoiceFile, InvoiceOCRData

router = APIRouter()

@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    # Check invoice exists
    invoice = db.query(InvoiceFile).filter(InvoiceFile.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete OCR data first (foreign key constraint)
    db.query(InvoiceOCRData).filter(InvoiceOCRData.invoice_id == invoice_id).delete()
    
    # Delete the physical file
    if os.path.exists(invoice.file_path):
        os.remove(invoice.file_path)
    
    # Delete the DB record
    db.delete(invoice)
    db.commit()
    
    return {"message": f"Invoice {invoice_id} deleted successfully"}