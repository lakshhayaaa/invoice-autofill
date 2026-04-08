from fastapi import FastAPI
from backend.app.api.routes.upload import router as upload_router
  # adjust import to your router path
from backend.app.db.session import engine
from backend.app.db import Base
from backend.app.api.routes.ocr import router as ocr_router
from backend.app.api.routes.view_uploaded_invoices import router as view_invoices_router
from backend.app.api.routes.text_standard_router import router as text_standard_router
from backend.app.api.routes.delete_invoices import router as delete_invoices_router

# Create all tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Invoice Processing API",
    version="1.0.0"
)

# Include your router
app.include_router(upload_router, prefix="/invoice")
app.include_router(view_invoices_router, prefix="/invoice") 
app.include_router(ocr_router, prefix="/invoice")
app.include_router(text_standard_router, prefix="/invoice")
app.include_router(delete_invoices_router, prefix="/invoice")

# Optional root endpoint
@app.get("/")
def root():
    return {"message": "Invoice Upload API is running"}
