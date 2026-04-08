from backend.app.db.init_db import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.services.standard_text_service import extract_processing_of_word

router=APIRouter()
@router.post("/standardise-invoice/{invoice_id}")
def invoice_ocr(invoice_id:int,db:Session=Depends(get_db)):
    return extract_processing_of_word(db,invoice_id)