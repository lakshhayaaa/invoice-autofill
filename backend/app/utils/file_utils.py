import os
import uuid
from backend.app.core.config import ALLOWED_MIME_TYPES
import shutil

#get file size in bytes
def get_file_size_bytes(file):
    file.file.seek(0, 2)      # move to end of file
    size_bytes = file.file.tell()
    file.file.seek(0)         # move back to start

    return size_bytes 

#check if file type is allowed
def is_allowed_file(content_type:str)->bool:
    return content_type in ALLOWED_MIME_TYPES

#get file category based on content type
def get_file_category(content_type: str) -> str:
    return ALLOWED_MIME_TYPES.get(content_type)

#generate a safe unique filename
def generate_safe_filename(original_filename):
    extension = os.path.splitext(original_filename)[1] #os.path.splitext returns a tuple (root, ext), we take the extension part
    new_name = str(uuid.uuid4())
    return new_name + extension

#save file to destination
def save_file(file, destination):
    with open(destination, "wb") as f:
        shutil.copyfileobj(file.file, f) #write file to memory part by part and save to disk, reducing memory usage and handles large files better
