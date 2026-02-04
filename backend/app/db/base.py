from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.app.db import Base
class InvoiceFile(Base):
    __tablename__ = "invoice_files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False, unique=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # MIME type
    status = Column(String, default="uploaded")  # uploaded, processed, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InvoiceOCRData(Base):
    __tablename__ = "invoice_ocr_data"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice_files.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    x=Column(Integer, nullable=False)
    y=Column(Integer, nullable=False)
    width=Column(Integer, nullable=False)
    height=Column(Integer, nullable=False)
    text=Column(String, nullable=False)
    confidence=Column(Integer, nullable=False)
    source=Column(String, nullable=True)  # digital or ocr
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    