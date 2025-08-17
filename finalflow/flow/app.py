import sys
import os
import io
import json
import base64
import asyncio
import logging

from dotenv import load_dotenv
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pdf2image import convert_from_path
import fitz

import convert2json
import wat
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

sys.path.append(os.path.abspath('/Users/tanishta/Desktop/UPSC_grading'))

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("ibm_watsonx_ai").setLevel(logging.WARNING)
logging.getLogger("ibm_watsonx_ai.foundation_models").setLevel(logging.WARNING)
# Load environment variables
load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
SERVICE_URL = os.getenv("IBM_SERVICE_URL")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

# Setup IBM Watson Client
credentials = Credentials(url=SERVICE_URL, api_key=API_KEY)
client = APIClient(credentials=credentials)
client.set.default_project(PROJECT_ID)

model_id = "meta-llama/llama-3-2-90b-vision-instruct"
params = {"decoding_method": "greedy", "max_new_tokens": 500}

model = ModelInference(
    model_id=model_id,
    credentials=credentials,
    project_id=PROJECT_ID,
    params=params
)

class HandwritingRecognizer:
    def __init__(self):
        self.extraction_prompt = (
            "You are an expert in handwriting recognition and text extraction. "
            "Your task is to extract only the text exactly as it appears in the image. "
            "Do not add any descriptions, explanations, or formatting notes. "
            "Strictly maintain: Original structure (paragraphs, sections, equations), subscripts, superscripts, and mathematical symbols as they appear. "
            "If any part is scribbled or unreadable, simply ignore it. "
            "Do not include anything written in hindi or any other language. "
            "Do not fix spelling or grammar errors. "
            "Only return the extracted text, formatted exactly as it appears and please do maintain the structure."
        )
        # Token count for prompt
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("meta-llama/llama-3-8b")
            num_tokens = len(tokenizer(self.extraction_prompt)["input_ids"])
            print(f"Prompt token count: {num_tokens}")
        except Exception as e:
            print(f"Could not count tokens: {e}")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def process_image(self, image_path):
        try:
            image_base64 = self.encode_image(image_path)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.extraction_prompt},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_base64}}
                    ]
                }
            ]
            response = await asyncio.to_thread(model.chat, messages=messages)
            return response["choices"][0]["message"]["content"] if response else None
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

class PDFHandwritingExtractor:
    def __init__(self):
        self.recognizer = HandwritingRecognizer()

    async def convert_pdf_to_images(self, pdf_path, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            doc = await asyncio.to_thread(fitz.open, pdf_path)
            image_paths = []

            logger.info(f"Processing PDF: {pdf_path} ({len(doc)} pages)")

            if len(doc) == 0:
                logger.error(f"No pages found in PDF: {pdf_path}")
                return []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                image_path = os.path.join(output_dir, f'page_{page_num + 1}.png')
                await asyncio.to_thread(pix.save, image_path)
                image_paths.append(image_path)
                logger.info(f"Saved page {page_num + 1}")

            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []

    async def extract_text_from_images(self, image_paths):
        extracted_texts = []
        for i, path in enumerate(image_paths, start=1):
            result = await self._extract_single_image_text(i, path)
            extracted_texts.append(result)
        return extracted_texts

    async def _extract_single_image_text(self, i, image_path):
        try:
            text = await self.recognizer.process_image(image_path)
            logger.info(f'Extracted text from page {i}')
            return (i, text or "[No Text Extracted]")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return (i, "[Error in Extraction]")

    async def create_text_pdf(self, extracted_texts, output_pdf_path):
        try:
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

            doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            text_style = ParagraphStyle(
                'CustomStyle',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceBefore=12,
                spaceAfter=12
            )

            for page_num, text in extracted_texts:
                story.append(Paragraph(f"<b>Page {page_num}</b>", styles['Heading2']))
                for para in text.split('\n'):
                    if para.strip():
                        story.append(Paragraph(para, text_style))

            await asyncio.to_thread(doc.build, story)
            logger.info(f'Successfully created output PDF: {output_pdf_path}')
            return True
        except Exception as e:
            logger.error(f"Error creating output PDF: {str(e)}")
            return False

# New function: process_extracted_texts_to_json

def process_extracted_texts_to_json(extracted_texts, output_json_path, document_id="", filename=""):
    """Process extracted texts and save answers in JSON format."""
    # Join all extracted texts into one string
    full_text = "\n".join([text for _, text in extracted_texts])
    answers = convert2json.extract_answers(full_text)
    result = [{
        "document_id": document_id,
        "filename": filename,
        "answers": answers
    }]
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved extracted answers to {output_json_path}")

async def main(
    input_pdf_answersheet,
    input_pdf_answerkey,
    extracted_text_pdf,
    temp_image_dir,
    output_json_answersheet,
    output_json_answerkey,
    result_dir,
    difficulty,
    total_marks,
    thresholds
):
    print("PDF conversion completed!")
    extractor = PDFHandwritingExtractor()

    # Convert PDF to images
    logger.info("Converting Answer Sheet PDF to images...")
    image_paths_answer_sheet = await extractor.convert_pdf_to_images(input_pdf_answersheet, temp_image_dir)
    logger.info("Converting Answer Key PDF to images...")
    image_paths_answer_key = await extractor.convert_pdf_to_images(input_pdf_answerkey, temp_image_dir)

    if not image_paths_answer_sheet or not image_paths_answer_key:
        logger.error("No images were created from one or both PDFs")
        return

    # Extract text from images
    logger.info("Extracting text from Answer Sheet images...")
    extracted_texts_answersheet = await extractor.extract_text_from_images(image_paths_answer_sheet)
    logger.info("Extracting text from Answer Key images...")
    extracted_texts_answerkey = await extractor.extract_text_from_images(image_paths_answer_key)

    if not extracted_texts_answersheet or not extracted_texts_answerkey:
        logger.error("No text was extracted from one or both sets of images")
        return

    # Create output PDF with extracted text (optional)
    logger.info("Creating output PDF for Answer Sheet...")
    await extractor.create_text_pdf(extracted_texts_answersheet, extracted_text_pdf)

    # Save extracted answers directly to JSON
    logger.info("Saving extracted answers to JSON...")
    process_extracted_texts_to_json(extracted_texts_answerkey, output_json_answerkey, document_id="answerkey", filename=os.path.basename(input_pdf_answerkey))
    process_extracted_texts_to_json(extracted_texts_answersheet, output_json_answersheet, document_id="answersheet", filename=os.path.basename(input_pdf_answersheet))

    # Compare JSONs with Cosine Similarity
    try:
        logger.info("Comparing Jsons with Cosine Similarity...")
        wat.compare_jsons(
            os.path.dirname(output_json_answersheet),
            os.path.dirname(output_json_answerkey),
            result_dir
        )
    except Exception as e:
        logger.error(f"Error comparing: {e}")


def trigger_grading(
    input_pdf_answersheet,
    input_pdf_answerkey,
    extracted_text_pdf,
    temp_image_dir,
    output_json_answersheet,
    output_json_answerkey,
    result_dir,
    difficulty,
    total_marks,
    thresholds
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(
        input_pdf_answersheet,
        input_pdf_answerkey,
        extracted_text_pdf,
        temp_image_dir,
        output_json_answersheet,
        output_json_answerkey,
        result_dir,
        difficulty,
        total_marks,
        thresholds
    ))