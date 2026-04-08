from backend.app.utils.text_normalization import get_normalized_ocr_words, tag_words_with_role
from sqlalchemy.orm import Session
from backend.app.utils.linereconstruction_utils import reconstruct_lines
from backend.app.utils.groupblocks_utils import run_phase_2
#from app.utils.groupblocks_utils import assign_spans_to_sections
def extract_processing_of_word(db: Session, invoice_id: int):
    normalized_words = get_normalized_ocr_words(db, invoice_id)
    #roletagged_words = tag_words_with_role(normalized_words)
    lines = reconstruct_lines(normalized_words)
    blocks= run_phase_2(lines)
    #spans=assign_spans_to_sections(lines)
    return blocks
