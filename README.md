
# 📄 PDF Parsing and Structured JSON Extraction

This project provides a Python script that parses a **PDF file**, extracts its **text, tables, and charts**, and organizes the content into a **structured JSON format** while maintaining the document’s hierarchy.

---

## 🎯 Objective

The goal of this program is to build a robust tool for extracting content from a PDF document and converting it into a **machine-readable JSON format**, preserving the document's **inherent structure** (pages, sections, sub-sections).

---

## ⚙️ Requirements

- **Input**: A PDF file.  
- **Output**: A JSON file with structured content.  
- **Content Types**:
  - Paragraphs  
  - Tables  
  - Charts (via OCR if needed)  
- **Hierarchy**: Output JSON preserves **page-level hierarchy**, including **section and sub-section names**.

---

## 🛠️ Installation

Install all required dependencies with:

```bash
pip install pdfplumber camelot-py[cv] "PyMuPDF>=1.22.0" opencv-python pytesseract numpy pandas
````

### 🔍 Note on Tesseract OCR

This script uses **pytesseract** for **optical character recognition (OCR)** to extract text from images (charts).
You must install and configure the **Tesseract OCR engine** on your system.

* **Windows**
  Download and install Tesseract from [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki).
  Then set the path in your script:

  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

* **macOS**

  ```bash
  brew install tesseract
  ```

* **Linux (Ubuntu/Debian)**

  ```bash
  sudo apt-get install tesseract-ocr
  ```

---

## ▶️ Usage

The script is a **command-line tool** that requires two arguments:

1. Path to the input **PDF file**.
2. Path to the output **JSON file**.

### Example Command:

```bash
python parse_pdf.py "sample.pdf" "output.json"
```

If successful, the script will output:

```
✅ Data extraction complete. Output saved to: output.json
```

---

## 📂 Example Output Structure

```json
{
  "pages": [
    {
      "page_number": 1,
      "sections": [
        {
          "title": "Introduction",
          "content": [
            {
              "type": "paragraph",
              "text": "This is a sample introduction text..."
            },
            {
              "type": "table",
              "data": [["Header1", "Header2"], ["Row1Col1", "Row1Col2"]]
            },
            {
              "type": "chart",
              "description": "Bar chart extracted via OCR",
              "text": "Chart labels and values..."
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 📌 Notes

* Tables are extracted using **Camelot**.
* Text is extracted using **pdfplumber** and **PyMuPDF**.
* Charts/diagrams are parsed using **PyMuPDF + OpenCV + pytesseract**.
* The JSON preserves **page-level structure** for easy downstream processing.

---

