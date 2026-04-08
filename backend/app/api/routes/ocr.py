from backend.app.db.init_db import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.services.ocr_service import process_invoice_ocr

router=APIRouter()
@router.post("/process-invoice-ocr/{invoice_id}")
def invoice_ocr(invoice_id:int,db:Session=Depends(get_db)):
    return process_invoice_ocr(db,invoice_id)


