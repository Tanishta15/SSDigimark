import re
from checker import process_text
from utils.ocr_reader import extract_text_from_image as blip2_ocr
from csv_mode import process_csv

USE_IMAGE = True
USE_BLIP2 = True

image_path = "images/sample_input.png"
output_csv = "input_answers.csv"

qna_list = []

if USE_IMAGE:
    print("🔍 Using image OCR...")

    if USE_BLIP2:
        full_text = blip2_ocr(image_path)
        print(f"📜 BLIP2 Extracted Text:\n\n{full_text}\n")

        # Smart splitting by questions
        blocks = re.split(r"(?:^|\n)\s*(Q[0-9]+[\):.-]?)", full_text, flags=re.IGNORECASE)
        
        current_q = None
        current_text = ""

        for part in blocks:
            part = part.strip()
            if re.match(r"^Q[0-9]+", part, flags=re.IGNORECASE):
                if current_q and current_text:
                    qna_list.append((current_q, current_text.strip()))
                    current_text = ""
                current_q = part
            else:
                current_text += " " + part

        if current_q and current_text:
            qna_list.append((current_q, current_text.strip()))
    else:
        print("⚠️ Non-BLIP2 mode not implemented here.")

# Save to CSV
if not qna_list:
    print("❌ No valid QnA found from image.")
    exit()

with open(output_csv, "w", encoding="utf-8") as f:
    f.write("AnswerID,AnswerText\n")
    for qid, ans in qna_list:
        f.write(f"{qid},{ans.replace(',', ' ')}\n")

print(f"✅ Saved {len(qna_list)} extracted answers to '{output_csv}'")

# Grammar analysis step
process_csv(output_csv, "output_results.csv")
print("✅ Grammar check completed. Final result saved to 'output_results.csv'")
