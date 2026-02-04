from transformers import LayoutLMv3ForTokenClassification, LayoutLMv3Processor
from backend.app.db.init_db import get_db_session

from training.build_dataset import (
    build_training_invoices,
    load_labelstudio_annotations,
    load_ocr_rows_grouped_by_invoice
)


import torch

LABEL_LIST = [
    "O",
    "SELLER_NAME",
    "SELLER_ADDRESS",
    "SELLER_GSTIN",

    "BILLED_TO_NAME",
    "BILLED_TO_ADDRESS",
    "BILLED_TO_GSTIN",

    "INVOICE_NUMBER",
    "INVOICE_DATE",

    "ITEM_DESC",
    "ITEM_QTY",
    "ITEM_RATE",
    "ITEM_AMOUNT"
]

model = LayoutLMv3ForTokenClassification.from_pretrained(
    "microsoft/layoutlmv3-base",
    num_labels=len(LABEL_LIST)
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

processor = LayoutLMv3Processor.from_pretrained(
    "microsoft/layoutlmv3-base",
    apply_ocr=False
)


label2id = {label: i for i, label in enumerate(LABEL_LIST)}
id2label = {i: label for label, i in label2id.items()}

model.config.label2id = label2id
model.config.id2label = id2label


import torch
from torch.utils.data import Dataset

class InvoiceDataset(Dataset):
    def __init__(self, invoices, processor, label2id):
        self.invoices = invoices
        self.processor = processor
        self.label2id = label2id

    def __len__(self):
        return len(self.invoices)

    def __getitem__(self, idx):
        invoice = self.invoices[idx]

        words  = invoice["words"]
        boxes  = invoice["boxes"]
        labels = invoice["labels"]   # word-level labels

        encoding = self.processor(
            words,
            boxes=boxes,
            truncation=True,
            padding="max_length",
            return_offsets_mapping=True,
            return_tensors="pt"
        )

        offsets = encoding.pop("offset_mapping")

        token_labels = []
        word_idx = 0

        for offset in offsets[0]:
            if offset[0] == 0 and offset[1] == 0:
                token_labels.append(-100)          # padding
            elif offset[0] == 0:
                if word_idx >= len(labels):   # 🔒 GUARD
                    token_labels.append(-100)
                else:
                    token_labels.append(self.label2id[labels[word_idx]])
                    word_idx += 1
            else:
                token_labels.append(-100)          # sub-token

        encoding["labels"] = torch.tensor(token_labels)

        # remove batch dim added by processor
        return {k: v.squeeze(0) for k, v in encoding.items()}



from torch.utils.data import DataLoader
from sqlalchemy.orm import Session
db = get_db_session() 
# 1. Load OCR rows from DB
ocr_rows = load_ocr_rows_grouped_by_invoice(db)

# 2. Load Label Studio export
ls_annotations = load_labelstudio_annotations("label_studio_export.json")

# 3. BUILD FINAL TRAINING INVOICES (THIS IS THE MISSING STEP)
invoices = build_training_invoices(ocr_rows, ls_annotations)


dataset = InvoiceDataset(invoices, processor, label2id)

dataloader = DataLoader(
    dataset,
    batch_size=2,
    shuffle=True
)


from torch.optim import AdamW

optimizer = AdamW(model.parameters(), lr=5e-5)
model.train()

for epoch in range(5):
    total_loss = 0

    for batch in dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}

        optimizer.zero_grad()
        outputs = model(**batch)
        loss = outputs.loss

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1} | Loss: {total_loss:.4f}")


model.save_pretrained("models/layoutlm-invoice")
processor.save_pretrained("models/layoutlm-invoice")