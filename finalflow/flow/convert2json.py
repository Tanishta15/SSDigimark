import os
import json
import re


def clean_answer_content(content: str) -> str:
    # Remove lines with instructions, formatting notes, or repeated 'Extracted Text:'
    lines = content.split('\n')
    filtered = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove lines with instructions or formatting notes
        if (
            'extract only the text' in line.lower() or
            'as per the instructions' in line.lower() or
            'here is the extracted text' in line.lower() or
            'the image contains' in line.lower() or
            'without adding any descriptions' in line.lower() or
            'formatting notes' in line.lower() or
            'extracted text:' in line.lower()
        ):
            continue
        filtered.append(line)
    return '\n'.join(filtered)


def extract_answers(text: str):
    """Extract answers from text with flexible Q/Answer format, cleaning extra context."""
    answers = {}
    try:
        # Match Q 1.1: ... A: ... (answer may span multiple lines until next Q or end)
        pattern = r'(?:-?\s*Q\s*([\d\.A-Za-z]+):.*?A:\s*)(.*?)(?=(?:-?\s*Q\s*[\d\.A-Za-z]+:)|$)'
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            number = match.group(1)
            content = match.group(2).strip()
            content = clean_answer_content(content)
            content = re.sub(r'\s+', ' ', content)
            answers[number] = content
        return answers
    except Exception as e:
        print(f"Error extracting answers: {e}")
        return {}


# New function for direct JSON saving
def save_answers_to_json(text: str, output_json_path: str, document_id: str = "", filename: str = ""):
    """Extract answers from text and save to JSON."""
    answers = extract_answers(text)
    result = [{
        "document_id": document_id,
        "filename": filename,
        "answers": answers
    }]
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved extracted answers to {output_json_path}")


# Deprecated: process_file and process_parquet_directory
if __name__ == "__main__":
    # Example usage
    sample_text = """
    Q 1: What is AI? A: Artificial Intelligence is the simulation of human intelligence processes by machines.
    Q 2: Define ML. A: Machine Learning is a subset of AI focused on building systems that learn from data.
    """
    save_answers_to_json(sample_text, "output.json", document_id="demo", filename="demo.txt")
