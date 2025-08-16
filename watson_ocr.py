import os
import sys
import json
import base64
import asyncio
import logging
import fitz  # PyMuPDF
from dotenv import load_dotenv
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Add current directory to path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    WATSON_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Watson import error: {e}")
    WATSON_IMPORTS_AVAILABLE = False
    # Don't raise error here, let the class handle it
    pass

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class WatsonOCR:
    def __init__(self):
        """Initialize Watson OCR with credentials from environment variables."""
        if not WATSON_IMPORTS_AVAILABLE:
            raise ImportError("IBM Watson AI libraries not installed. Please run: pip install ibm-watsonx-ai")
            
        self.api_key = os.getenv("IBM_API_KEY")
        self.service_url = os.getenv("IBM_SERVICE_URL")
        self.project_id = os.getenv("IBM_PROJECT_ID")
        
        if not all([self.api_key, self.service_url, self.project_id]):
            raise ValueError("Missing IBM Watson credentials. Please check your .env file.")
        
        # Setup IBM Watson Client
        self.credentials = Credentials(url=self.service_url, api_key=self.api_key)
        self.client = APIClient(credentials=self.credentials)
        self.client.set.default_project(self.project_id)
        
        # Model configuration
        self.model_id = "meta-llama/llama-3-2-90b-vision-instruct"
        self.params = {"decoding_method": "greedy", "max_new_tokens": 500}
        
        self.model = ModelInference(
            model_id=self.model_id,
            credentials=self.credentials,
            project_id=self.project_id,
            params=self.params
        )
        
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

    def encode_image(self, image_path):
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def process_image(self, image_path):
        """Process a single image and extract text using Watson."""
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
            response = await asyncio.to_thread(self.model.chat, messages=messages)
            return response["choices"][0]["message"]["content"] if response else None
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    async def convert_pdf_to_images(self, pdf_path, output_dir):
        """Convert PDF pages to images."""
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
        """Extract text from multiple images."""
        extracted_texts = await asyncio.gather(
            *(self._extract_single_image_text(i, path) for i, path in enumerate(image_paths, start=1))
        )
        return extracted_texts

    async def _extract_single_image_text(self, i, image_path):
        """Extract text from a single image."""
        try:
            text = await self.process_image(image_path)
            logger.info(f'Extracted text from page {i}')
            return (i, text or "[No Text Extracted]")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return (i, "[Error in Extraction]")

    def extract_answers(self, text):
        """Extract answers from text with flexible Q/Answer format."""
        import re
        answers = {}
        try:
            # Clean the text first
            lines = text.split('\n')
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
            
            cleaned_text = '\n'.join(filtered)
            
            # Match Q 1.1: ... A: ... (answer may span multiple lines until next Q or end)
            pattern = r'(?:-?\s*Q\s*([\d\.A-Za-z]+):.*?A:\s*)(.*?)(?=(?:-?\s*Q\s*[\d\.A-Za-z]+:)|$)'
            matches = re.finditer(pattern, cleaned_text, re.DOTALL)
            for match in matches:
                number = match.group(1)
                content = match.group(2).strip()
                content = re.sub(r'\s+', ' ', content)
                answers[number] = content
            return answers
        except Exception as e:
            logger.error(f"Error extracting answers: {e}")
            return {}

    async def process_pdf_to_json(self, pdf_path, output_json_path, temp_dir, document_id="", filename=""):
        """Process PDF to extract answers and save as JSON."""
        try:
            # Convert PDF to images
            image_paths = await self.convert_pdf_to_images(pdf_path, temp_dir)
            if not image_paths:
                logger.error("No images were created from PDF")
                return False

            # Extract text from images
            extracted_texts = await self.extract_text_from_images(image_paths)
            if not extracted_texts:
                logger.error("No text was extracted from images")
                return False

            # Combine all extracted texts
            full_text = "\n".join([text for _, text in extracted_texts])
            
            # Extract answers
            answers = self.extract_answers(full_text)
            
            # Save to JSON
            result = [{
                "document_id": document_id,
                "filename": filename,
                "answers": answers
            }]
            
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved extracted answers to {output_json_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return False

def extract_text_from_image(image_path):
    """Synchronous wrapper for image text extraction."""
    try:
        watson = WatsonOCR()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(watson.process_image(image_path))
        return result or ""
    except Exception as e:
        logger.error(f"Error in synchronous image extraction: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_path, temp_dir="./temp"):
    """Synchronous wrapper for PDF text extraction."""
    try:
        watson = WatsonOCR()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create temp directory
        os.makedirs(temp_dir, exist_ok=True)
        
        # Convert PDF to images and extract text
        image_paths = loop.run_until_complete(watson.convert_pdf_to_images(pdf_path, temp_dir))
        if not image_paths:
            return ""
            
        extracted_texts = loop.run_until_complete(watson.extract_text_from_images(image_paths))
        
        # Combine all extracted texts
        full_text = "\n".join([text for _, text in extracted_texts])
        return full_text
        
    except Exception as e:
        logger.error(f"Error in synchronous PDF extraction: {str(e)}")
        return ""

if __name__ == "__main__":
    # Test the Watson OCR
    print("Watson OCR module loaded successfully!")
    print("Make sure to set your IBM Watson credentials in the .env file:")
    print("- IBM_API_KEY")
    print("- IBM_SERVICE_URL")  
    print("- IBM_PROJECT_ID")
