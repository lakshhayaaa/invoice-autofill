from pdf2image import convert_from_path
from pathlib import Path
import pdfplumber

#read text directly from digital pdfs
def extract_words_from_pdf(pdf_path:Path)->list:
    with pdfplumber.open(pdf_path) as pdf:
        pages_words=[]
        for page_number, page in enumerate(pdf.pages, start=1):
            words=page.extract_words()
            for word in words:
                bbox=(word['x0'], word['top'], word['x1'], word['bottom'])
                x0,y0,x1,y1=normalize_bbox(bbox, page.width, page.height)
                
                pages_words.append({
                "page":page_number,
                "text":word['text'],
                "x": x0,
                "y": y0,
                "width": x1 - x0,
                "height": y1 - y0,
                "confidence": int(word.get('confidence',100)),  #pdfplumber does not provide confidence, using doctop as a placeholder
            })
    return pages_words
def normalize_bbox(bbox:tuple, page_width:float, page_height:float)->tuple:
    """
    Normalize bounding box coordinates to LayoutLM format as integers in [0,1000] range.
    bbox: (x0, y0, x1, y1)
    """
    x0, y0, x1, y1 = bbox

    return (
        max(0,min(1000,int(1000*x0 / page_width))),
        max(0,min(1000,int(1000*y0 / page_height))),
        max(0,min(1000,int(1000*x1 / page_width))),
        max(0,min(1000,int(1000*y1 / page_height)))
    )

#convert pdf to images page by page
def pdf_to_images(pdf_path:Path, output_folder:Path): 
    output_folder.mkdir(parents=True, exist_ok=True) # Create output folder if it doesn't exist
    
    # Convert PDF to images, each page as a separate image
    images = convert_from_path(str(pdf_path),dpi=300)
   
    # Save each image to the output folder
    image_paths = []
    
    for index, image in enumerate(images,start=1):  #enumerate to get page number, starting from 1
        image_path = output_folder / f"page_{index}.png" #compose image path
        image.save(image_path, 'PNG')                     #save image as PNG
        image_paths.append(image_path)                    #store image path
    
    #return list of image paths
    return image_paths