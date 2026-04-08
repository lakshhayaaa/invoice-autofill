import unicodedata
from sqlalchemy.orm import Session
from backend.app.db.base import InvoiceOCRData
import re
from typing import List, Dict

def get_normalized_ocr_words(db: Session, invoice_id: int)-> list[dict]:
    rows = (
        db.query(InvoiceOCRData)
        .filter(InvoiceOCRData.invoice_id == invoice_id)
        .order_by(
            InvoiceOCRData.page_number,
            InvoiceOCRData.y,
            InvoiceOCRData.x
        )
        .all()
    )

    normalized_words = []

    for row in rows:
        normalized_text = normalize_unicode(row.text)

        

        normalized_words.append({
            "text":normalized_text ,
            "x": row.x,
            "y": row.y,
            "width": row.width,
            "height": row.height,
            "confidence": row.confidence,
            "page": row.page_number,
        })
    return normalized_words


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode OCR artifacts safely.
    Fixes ligatures, full-width chars, and compatibility symbols.
    """
    if not text:
        return ""
    # Unicode compatibility normalization
    text = unicodedata.normalize("NFKC", text)
    # Rare OCR ligatures that sometimes survive NFKC
    LIGATURE_FIXES = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }
    for k, v in LIGATURE_FIXES.items():
        text = text.replace(k, v)
    
    # whitespace cleanup
    text=re.sub(r"[\t\r\n]+"," ",text)
    text=re.sub(r"\s{2,}"," ",text)
    text=text.strip()

    return text

ROLE_PRIORITY = [
    ("DELIVERY_AT", ["SHIP TO", "SHIPPING ADDRESS", "DELIVERY AT", "CONSIGNEE"]),
    ("BILLED_TO", ["BILL TO", "BILLING ADDRESS", "BUYER"]),
    ("SELLER", ["SOLD BY", "SELLER", "SUPPLIER"]),
    ("INVOICE_META", ["INVOICE NO", "INVOICE DATE", "ORDER NO"]),
    ("BANK", ["BANK", "A/C", "ACCOUNT", "IFSC", "BRANCH"]),
]
def tag_words_with_role(words):
    current_role = None

    for w in words:
        text = w["text"].upper()

        # 🔑 priority-based override
        for role, triggers in ROLE_PRIORITY:
            if any(t in text for t in triggers):
                current_role = role
                break

        w["role"] = current_role

    return words