from app.core.config import  BASE_DIR
from app.utils.pdf_utils import pdf_to_images, extract_words_from_pdf
from pathlib import Path
from app.db.base import InvoiceFile
from sqlalchemy.orm import Session
import os
from app.utils.image_utils import image_preprocessing
from app.utils.ocr_utils import extract_bounding_boxes,merge_ocr_results,score
from app.db.base import InvoiceOCRData
import pdfplumber
from app.utils.text_normalization import get_normalized_ocr_words

def process_invoice_ocr(db: Session,invoice_id: int):
    # Fetch the invoice file record from the database
    invoice_file = db.query(InvoiceFile).filter(InvoiceFile.id == invoice_id).first()
    if not invoice_file:
        raise ValueError(f"Invoice file with ID {invoice_id} not found.")
    invoice_file.status="processing"
    db.commit() 
    extension=os.path.splitext(invoice_file.original_filename)[1].lower()
    try:
        if extension==".pdf":
            result=_process_pdf_invoice(db,invoice_file)
        #elif extension in [".png",".jpg",".jpeg"]:
            #result=_process_image_invoice(db,invoice_file)
        else:
            raise ValueError(f"Unsupported file type: {extension}") 
        response = {"invoice_id": invoice_file.id,"status": invoice_file.status}
        if isinstance(result, dict):
            response.update(result)
        return response

    except Exception as e:
        invoice_file.status="error"
        db.commit()
        return{
            "invoice_id":invoice_file.id,
            "status":invoice_file.status,
            "error":str(e)
        }
    

def _process_pdf_invoice(db: Session,invoice_file: InvoiceFile):
    pdf_path = Path(invoice_file.file_path)
    #case 1: digital pdf, text extracted directly
    ocr_results=[]
    ocr_results=extract_words_from_pdf(pdf_path)
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
    
    if ocr_results:
        invoice_file.status = "ocr completed"
        db.commit()
        save_ocr_results(db, invoice_file, ocr_results, source="digital")

        return {
            "ocr_type": "digital",
            "pages_processed": total_pages,
            "message": "Digital PDF extracted: table cells + non-table words saved"
        }
    
    #case 2: scanned pdf, convert to images and preprocess each image
''' output_path=BASE_DIR/"storage/temp"/str(invoice_file.id) #temporary folder for pdf pages
    output_path.mkdir(parents=True, exist_ok=True)
    image_paths=pdf_to_images(pdf_path,output_path)
    for index,img_path in enumerate(image_paths,start=1):
        preprocessed_path=(BASE_DIR / "storage/pre-processed" / f"{invoice_file.id}_page_{index}.png")
        success= image_preprocessing(img_path,preprocessed_path)
        if not success:
            raise RuntimeError(f"Failed to write processed image for page {index}")
    invoice_file.status="preprocessed"
    db.commit()
    #perform ocr on each preprocessed image and aggregate text
    for index,img_path in enumerate(image_paths,start=1):
        preprocessed_path=(BASE_DIR / "storage/pre-processed" / f"{invoice_file.id}_page_{index}.png")
        prep_ocr_results=extract_bounding_boxes(preprocessed_path)
        raw_ocr_results=extract_bounding_boxes(img_path)
        # Save OCR results to database
        merged_ocr_results=merge_ocr_results(raw_ocr_results,prep_ocr_results)
        save_ocr_results(db=db,invoice_file=invoice_file,ocr_results=merged_ocr_results,page_number=index,source="merged")
    return{
        "ocr_type":"ocr",
        "pages_processed": len(image_paths),
        "message": "Scanned PDF processed with OCR successfully"
    }

def _process_image_invoice(db: Session,invoice_file: InvoiceFile):
    raw_image_path = invoice_file.file_path
    img = cv2.imread(str(raw_image_path))
    if img is None:
        raise ValueError(f"Failed to read image: {raw_image_path}")
    preprocessed_path=(BASE_DIR / "storage/pre-processed" / f"{invoice_file.id}.png") #single image
    success= image_preprocessing(raw_image_path,preprocessed_path)
    if not success:
        raise RuntimeError("Failed to write processed image")
    invoice_file.status="preprocessed"
    db.commit()
    #perform ocr on preprocessed image
    prep_ocr_results=extract_bounding_boxes(preprocessed_path)
    raw_ocr_results=extract_bounding_boxes(raw_image_path)
     #Save OCR results to database
    merged_ocr_results=merge_ocr_results(raw_ocr_results,prep_ocr_results)
    save_ocr_results(db=db,invoice_file=invoice_file,ocr_results=merged_ocr_results,source="merged")
    return{
        "ocr_type":"ocr",
        "pages_processed": 1,
        "message": "Image processed with OCR successfully"
    }'''

def save_ocr_results(db: Session,invoice_file: InvoiceFile,ocr_results:list,source:str,page_number:int=1):
    for result in ocr_results:
        ocr_data = InvoiceOCRData(
            invoice_id=invoice_file.id,
            page_number=result["page"],
            x=result["x"],
            y=result["y"],
            width=result["width"],
            height=result["height"],
            text=result["text"],
            confidence=result["confidence"],
            source=source
        )
        db.add(ocr_data)
    invoice_file.status="ocr completed"
    db.commit()