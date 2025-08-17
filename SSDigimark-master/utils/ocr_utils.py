import re
from .ocr_reader import extract_text_from_image  # Import BLIP2-based extractor

def extract_text_from_image_and_split(image_path, use_blip=True):
    try:
        # === Step 1: Extract text using BLIP2 ===
        if use_blip:
            full_text = extract_text_from_image(image_path)
        else:
            # fallback or legacy mode - Tesseract
            import cv2
            import pytesseract
            import numpy as np

            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            image = cv2.imread(image_path)

            if image is None:
                raise FileNotFoundError(f"Unable to read image at {image_path}")

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 31, 2
            )
            full_text = pytesseract.image_to_string(gray)

        # === Step 2: Split into Q1, Q2, Q3... ===
        question_blocks = re.split(r"\bQ[0-9]+[\).:-]?", full_text, flags=re.IGNORECASE)
        questions = []

        for i, block in enumerate(question_blocks[1:], 1):  # skip anything before Q1
            clean_text = block.strip()
            if clean_text:
                questions.append((f"Q{i}", clean_text))

        return questions  # ➕ Your format remains untouched
    except Exception as e:
        return f"[ERROR] {str(e)}"
