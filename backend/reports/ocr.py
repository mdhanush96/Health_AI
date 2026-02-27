import os
import logging
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

logger = logging.getLogger('health_ai')


def extract_text_from_file(file_path: str, report_type: str) -> str:
    """Extract text from uploaded file based on type."""
    try:
        if report_type == 'PDF':
            return _extract_from_pdf(file_path)
        elif report_type == 'IMAGE':
            return _extract_from_image(file_path)
        elif report_type == 'CSV':
            return _extract_from_csv(file_path)
        else:
            return ''
    except Exception as e:
        logger.error(f'OCR extraction failed for {file_path}: {e}')
        return ''


def _extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF + Tesseract for scanned PDFs."""
    text_parts = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
            else:
                # Scanned PDF - use OCR
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img, config='--psm 6')
                text_parts.append(ocr_text)
        doc.close()
    except Exception as e:
        logger.error(f'PDF extraction error: {e}')
    return '\n'.join(text_parts)


def _extract_from_image(file_path: str) -> str:
    """Extract text from image using Tesseract OCR."""
    try:
        img = Image.open(file_path)
        # Use LSTM OCR engine with auto page segmentation
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        return text
    except Exception as e:
        logger.error(f'Image OCR error: {e}')
        return ''


def _extract_from_csv(file_path: str) -> str:
    """Extract text representation from CSV."""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    except Exception as e:
        logger.error(f'CSV extraction error: {e}')
        return ''


def detect_report_type(file_name: str) -> str:
    """Determine report type from file extension."""
    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.pdf':
        return 'PDF'
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return 'IMAGE'
    elif ext == '.csv':
        return 'CSV'
    return 'IMAGE'
