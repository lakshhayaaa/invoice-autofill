from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from backend.app.db.init_db import get_db
from backend.app.services.upload_service import upload_invoice_service

router = APIRouter()

@router.post("/upload-invoice")
def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return upload_invoice_service(file, db)

