import pdfplumber
import camelot
import fitz
import cv2
import pytesseract
import numpy as np
import json
import sys
import os
import shutil
import glob
import time
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def is_section(line):
    line = line.strip()
    words = line.split()
    if not words:
        return False
    
    if len(words) <= 6 and line.isupper():
        return True
    
    if re.match(r'^\d+(\.\d+)*\s', line):
        if len(words) <= 10: 
            return True

    return False

def is_subsection(line):
    line = line.strip()
    words = line.split()
    if not words:
        return False

    if len(words) <= 10 and line.istitle():
        return True
    
    if line.endswith(':'):
        return True
    
    if re.match(r'^[A-Z]\.\s|^[a-z]\.\s|^\d+\.\s|^\([a-z]\)\s|^\([0-9]\)\s', line):
        return True

    return False

def extract_pdf_content(pdf_path):
    final_data = {"pages": []}
    current_section = None
    current_subsection = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_content = []
                
                text = page.extract_text()
                if text:
                    cleaned_text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
                    paragraphs = []
                    buffer = ""
                    for line in cleaned_text.split("\n"):
                        line = line.strip()
                        if not line and buffer:
                            paragraphs.append(buffer.strip())
                            buffer = ""
                        else:
                            buffer += " " + line
                    if buffer:
                        paragraphs.append(buffer.strip())

                    for para in paragraphs:
                        if is_section(para):
                            current_section = para
                            current_subsection = None
                        elif is_subsection(para):
                            current_subsection = para
                        else:
                            if para.strip():
                                page_content.append({
                                    "type": "paragraph",
                                    "section": current_section,
                                    "sub_section": current_subsection,
                                    "text": para
                                })

                try:
                    tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='stream')
                    for table in tables:
                        table_data = table.df.values.tolist()
                        if table_data:
                            page_content.append({
                                "type": "table",
                                "section": current_section,
                                "sub_section": current_subsection,
                                "description": "Extracted table",
                                "table_data": table_data
                            })
                except Exception as e:
                    print(f"Error extracting tables on page {page_num}: {e}", file=sys.stderr)
                    pass

                final_data["pages"].append({
                    "page_number": page_num,
                    "content": page_content
                })
    finally:
        pass

    doc = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images(full=True)

            for img_index, img in enumerate(images, start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                np_arr = np.frombuffer(image_bytes, np.uint8)
                img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

                ocr_text = pytesseract.image_to_string(gray, lang='eng')
                
                section_for_chart = None
                subsection_for_chart = None
                if page_num -1 < len(final_data["pages"]):
                    for item in final_data["pages"][page_num -1]["content"]:
                        if "section" in item and item["section"] is not None:
                            section_for_chart = item["section"]
                        if "sub_section" in item and item["sub_section"] is not None:
                            subsection_for_chart = item["sub_section"]
                
                if page_num -1 < len(final_data["pages"]):
                    final_data["pages"][page_num -1]["content"].append({
                        "type": "chart",
                        "section": section_for_chart,
                        "sub_section": subsection_for_chart,
                        "description": f"Chart extracted. OCR text: {ocr_text.strip() or 'No OCR text detected'}"
                    })
    finally:
        if doc:
            doc.close()

    return final_data

def remove_temp_dirs():
    temp_path = os.environ.get('TEMP')
    if not temp_path:
        return

    temp_dir_pattern = os.path.join(temp_path, 'camelot*')
    temp_dirs = glob.glob(temp_dir_pattern)
    
    for temp_dir in temp_dirs:
        if os.path.isdir(temp_dir):
            for attempt in range(5):
                try:
                    shutil.rmtree(temp_dir)
                    break
                except OSError as e:
                    if e.winerror == 32:
                        time.sleep(1)
                    else:
                        break
                except Exception:
                    break

def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_pdf.py <input.pdf> <output.json>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} not found.")
        sys.exit(1)
    
    try:
        print("Starting PDF content extraction...")
        data = extract_pdf_content(pdf_path)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Data extracted and saved to {output_path}")

    finally:
        remove_temp_dirs()
        print("Temporary files cleaned up.")

if __name__ == "__main__":
    main()