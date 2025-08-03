from utils.ocr_utils import preprocess_image, extract_text_from_image, split_text_questionwise
from checker import process_text

def analyze_image(image_path):
    print(f"🔍 Processing Image: {image_path}")
    image = preprocess_image(image_path)
    raw_text = extract_text_from_image(image)
    question_map = split_text_questionwise(raw_text)

    for q_no, answer_text in question_map.items():
        print(f"\n📌 {q_no} - Answer:")
        result = process_text(answer_text)
        
        print(f"\n📌 Original Answer:\n{result['original']}")
        for error in result['errors']:
            print(f"\n🔍 Incorrect Line:\n{error['highlighted']}")
            print(f"✅ Corrected:\n{error['corrected']}")
        print(f"\n📝 Grammar Score: {result['score']}/100 ({result['remark']})")

if __name__ == "__main__":
    # Replace this with your actual file name inside /images/
    analyze_image("images/sample_answer.jpg")
