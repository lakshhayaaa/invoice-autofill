
from backend.app.db.base import InvoiceOCRData


def build_label_studio_tasks(db):
    tasks = []

    invoices = (
        db.query(InvoiceOCRData.invoice_id)
        .distinct()
        .all()
    )

    for (invoice_id,) in invoices:
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

        words = []
        for r in rows:
            words.append({
            "text": r.text,
            "x": r.x,
            "y": r.y,
            "width": r.width,
            "height": r.height
        })


        task = {
            "data": {
                "invoice_id": invoice_id,
                "words": words
            }
        }

        tasks.append(task)

    return tasks

def build_training_invoices(ocr_rows, ls_annotations):
    invoices = []

    for invoice_id in ls_annotations:
        words = []
        boxes = []
        labels = []

        ocr_words = ocr_rows[invoice_id]      # ordered OCR rows
        ls_labels = ls_annotations[invoice_id]  # ordered LS labels

        for ocr, label in zip(ocr_words, ls_labels):
            words.append(ocr["text"])
            boxes.append([
                ocr["x"],
                ocr["y"],
                ocr["x"] + ocr["width"],
                ocr["y"] + ocr["height"],
            ])
            labels.append(label if label else "O")

        invoices.append({
            "words": words,
            "boxes": boxes,
            "labels": labels
        })

    return invoices

import json
from collections import defaultdict

def load_labelstudio_annotations(path):
    """
    Returns:
    {
      invoice_id: [label1, label2, label3, ...]  # in token order
    }
    """
    with open(path, "r") as f:
        data = json.load(f)

    annotations_by_invoice = defaultdict(list)

    for task in data:
        invoice_id = task["data"]["invoice_id"]

        # Label Studio stores results inside annotations → result
        results = task["annotations"][0]["result"]

        # IMPORTANT: keep order as labeled
        for r in results:
            label = r["value"]["labels"][0]
            annotations_by_invoice[invoice_id].append(label)

    return annotations_by_invoice

from collections import defaultdict
from backend.app.db.base import InvoiceOCRData

def load_ocr_rows_grouped_by_invoice(db):
    """
    Returns:
    {
      invoice_id: [
        {
          "text": str,
          "x": int,
          "y": int,
          "width": int,
          "height": int
        },
        ...
      ]
    }
    """
    rows = (
        db.query(InvoiceOCRData)
        .order_by(
            InvoiceOCRData.invoice_id,
            InvoiceOCRData.page_number,
            InvoiceOCRData.y,
            InvoiceOCRData.x
        )
        .all()
    )

    ocr_rows = defaultdict(list)

    for r in rows:
        ocr_rows[r.invoice_id].append({
            "text": r.text,
            "x": r.x,
            "y": r.y,
            "width": r.width,
            "height": r.height
        })

    return ocr_rows
