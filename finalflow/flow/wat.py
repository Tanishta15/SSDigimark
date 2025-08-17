import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from itertools import product
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class SentenceTransformerEmbeddings:
    def __init__(self):
        """Initialize Sentence Transformer Model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_text(self, text):
        """Generate embedding for a single text"""
        return self.model.encode(text)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def compare_jsons(folder1, folder2, output_folder):
    """Compares JSON answer files in two folders regardless of filenames."""
    files1 = [f for f in os.listdir(folder1) if f.endswith(".json")]
    files2 = [f for f in os.listdir(folder2) if f.endswith(".json")]
    os.makedirs(output_folder, exist_ok=True)

    try:
        embedding_model = SentenceTransformerEmbeddings()
    except Exception as e:
        logger.error(f"Error loading SentenceTransformer model: {e}")
        return

    for file1, file2 in product(files1, files2):
        json_path1 = os.path.join(folder1, file1)
        json_path2 = os.path.join(folder2, file2)

        try:
            with open(json_path1, "r", encoding="utf-8") as f1:
                data1 = json.load(f1)
            with open(json_path2, "r", encoding="utf-8") as f2:
                data2 = json.load(f2)

            if not isinstance(data1, list) or not isinstance(data2, list) or not data1 or not data2:
                logger.warning(f"Skipping comparison of {file1} and {file2} - invalid JSON structure")
                continue

            answers_dict1 = data1[0].get("answers", {})
            answers_dict2 = data2[0].get("answers", {})

            similarity_results = []

            # Use all keys from answerkey (answers_dict1)
            all_keys = sorted(set(answers_dict1.keys()), key=natural_sort_key)

            for key in all_keys:
                answer1 = answers_dict1.get(key, "")
                answer2 = answers_dict2.get(key, "")

                if not answer2:
                    similarity_score = 0.0  # Missing answer in answersheet
                else:
                    try:
                        embedding1 = embedding_model.embed_text(answer1)
                        embedding2 = embedding_model.embed_text(answer2)
                        similarity_score = float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
                    except Exception as e:
                        logger.error(f"Error processing question {key} when comparing {file1} and {file2}: {e}")
                        similarity_score = 0.0

                similarity_results.append({
                    "question_number": key,
                    "answer1": answer1,
                    "answer2": answer2,
                    "similarity_score": similarity_score
                })

            if similarity_results:
                # Always save as similarity_extracted_text_pd.json for frontend compatibility
                output_filename = "similarity_extracted_text_pd.json"
                output_path = os.path.join(output_folder, output_filename)

                similarity_results.sort(key=lambda x: natural_sort_key(x["question_number"]))

                with open(output_path, "w", encoding="utf-8") as outf:
                    json.dump({
                        "file1": {
                            "path": json_path1,
                            "document_id": data1[0].get("document_id", ""),
                            "filename": data1[0].get("filename", "")
                        },
                        "file2": {
                            "path": json_path2,
                            "document_id": data2[0].get("document_id", ""),
                            "filename": data2[0].get("filename", "")
                        },
                        "comparisons": similarity_results
                    }, outf, indent=4, ensure_ascii=False)
                logger.info(f"Saved comparison results to {output_path}")

        except Exception as e:
            logger.error(f"Error comparing {file1} and {file2}: {e}")

if __name__ == "__main__":
    try:
        logger.info("Comparing JSONs with Cosine Similarity...")
        folder1 = "/Users/tanishta/Desktop/UPSC_grading/finalflow/input_folder/AnswerKey/Json_with_answers"
        folder2 = "/Users/tanishta/Desktop/UPSC_grading/finalflow/input_folder/AnswerSheet/Json_with_answers"
        output_folder = "/Users/tanishta/Desktop/UPSC_grading/finalflow/results"
        compare_jsons(folder1, folder2, output_folder)
    except Exception as e:
        logger.error(f"Error during cosine similarity comparison: {str(e)}")