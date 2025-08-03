import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grammar_checker import check_grammar
from utils.ocr_reader import extract_text_from_image

image_path = "images/sample_input.png"
text = extract_text_from_image(image_path)

print("📸 Extracted Text from Image:\n")
print(text)
print("\n")

# Check grammar
errors = check_grammar(text)

if not errors:
    corrected_text = text.strip()
else:
    corrected_text = list(text)
    for error in reversed(errors):
        corrected_text[error['offset']:error['offset'] + error['length']] = error['better']
    corrected_text = ''.join(corrected_text)

print("✅ Corrected Text:\n")
print(corrected_text)
