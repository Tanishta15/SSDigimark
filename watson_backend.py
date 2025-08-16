"""
Simplified Integrated Backend - Watson OCR Only
Focused backend that only uses IBM Watson for OCR processing
"""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path
import asyncio
import re
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Watson OCR module
try:
    # Test IBM Watson AI imports first
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    
    # Then import our Watson OCR wrapper
    from watson_ocr import WatsonOCR
    WATSON_AVAILABLE = True
    logger.info("Watson OCR module loaded successfully")
except ImportError as e:
    logger.warning(f"Watson OCR module not available: {e}")
    WATSON_AVAILABLE = False
    WatsonOCR = None
    WatsonOCR = None

class Backend:
    def __init__(self):
        self.watson_ocr = None
        if WATSON_AVAILABLE:
            try:
                self.watson_ocr = WatsonOCR()
                logger.info("Watson OCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Watson OCR: {e}")
                self.watson_ocr = None

    def is_available(self):
        """Check if Watson OCR is available and configured"""
        return self.watson_ocr is not None

    def get_available_engines(self):
        """Get list of available OCR engines"""
        engines = []
        if self.watson_ocr:
            engines.append({"name": "IBM Watson", "status": "Available"})
        else:
            engines.append({"name": "IBM Watson", "status": "Not configured - check .env file"})
        return engines

    def check_status(self):
        """Check the status of all engines"""
        engines = self.get_available_engines()
        total_available = len([e for e in engines if "Available" in e["status"]])
        
        return {
            'total_engines': total_available,
            'engines': engines,
            'watson_available': self.watson_ocr is not None
        }

    async def extract_text_from_files(self, file_paths, engine="Watson"):
        """Extract text from multiple files using Watson OCR"""
        if not self.watson_ocr:
            raise Exception("Watson OCR not available. Please check your .env configuration.")

        results = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                file_extension = file_path.split('.')[-1].lower()
                
                logger.info(f"Processing {file_name} with Watson OCR...")
                
                if file_extension == 'pdf':
                    extracted_text = await asyncio.to_thread(
                        self.watson_ocr.extract_text_from_pdf, 
                        file_path, 
                        temp_dir
                    )
                else:
                    extracted_text = await asyncio.to_thread(
                        self.watson_ocr.extract_text_from_image, 
                        file_path
                    )
                
                results.append({
                    'file': file_name,
                    'text': extracted_text,
                    'engine': 'Watson'
                })
                
        except Exception as e:
            logger.error(f"Error during text extraction: {e}")
            raise
        finally:
            # Cleanup temp directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return results

    def evaluate_answer_sheets(self, answer_key_path, answer_sheet_paths, mode="auto", engine="Watson"):
        """Evaluate answer sheets using Watson OCR"""
        try:
            if not self.watson_ocr:
                return {
                    'success': False,
                    'error': 'Watson OCR not available. Please check your .env configuration.'
                }

            # Run the async extraction in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Extract text from answer key
                logger.info("Extracting text from answer key...")
                key_extension = answer_key_path.split('.')[-1].lower()
                if key_extension == 'pdf':
                    answer_key_text = self.watson_ocr.extract_text_from_pdf(answer_key_path)
                else:
                    answer_key_text = self.watson_ocr.extract_text_from_image(answer_key_path)
                
                # Extract text from answer sheets
                logger.info("Extracting text from answer sheets...")
                sheet_results = []
                for i, sheet_path in enumerate(answer_sheet_paths):
                    sheet_extension = sheet_path.split('.')[-1].lower()
                    if sheet_extension == 'pdf':
                        sheet_text = self.watson_ocr.extract_text_from_pdf(sheet_path)
                    else:
                        sheet_text = self.watson_ocr.extract_text_from_image(sheet_path)
                    
                    sheet_results.append({
                        'file': f'Sheet_{i+1}',
                        'text': sheet_text
                    })
                
                return {
                    'success': True,
                    'processing_method': 'watson_ocr',
                    'answer_key_text': answer_key_text,
                    'results': sheet_results,
                    'engine_used': 'Watson'
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def check_grammar(self, input_data, mode="text", language="en-US"):
        """Run grammar check on text or image content using SSDigimark grammar checker.
        - mode="text": input_data is raw text
        - mode="image": input_data is a file path to an image (or pdf) to OCR first
        Returns dict with: success, original_text, corrected_text, highlighted_text, corrections[] or error
        """
        try:
            # Resolve text based on mode
            if mode == "image":
                if not self.watson_ocr:
                    return {"success": False, "error": "Watson OCR not available for image grammar check."}
                path = str(input_data)
                ext = (path.split('.')[-1] or '').lower()
                if ext == 'pdf':
                    text = self.watson_ocr.extract_text_from_pdf(path)
                else:
                    text = self.watson_ocr.extract_text_from_image(path)
                if not text or not text.strip():
                    return {"success": False, "error": "No text extracted from image for grammar check."}
            else:
                text = str(input_data or "")
                if not text.strip():
                    return {"success": False, "error": "Empty text provided for grammar check."}

            # Use LanguageTool public API for grammar checking (SSDigimark style)
            api_url = "https://api.languagetool.org/v2/check"
            data = {"text": text, "language": language}
            resp = requests.post(api_url, data=data, timeout=20)
            if resp.status_code != 200:
                return {"success": False, "error": f"Grammar API error {resp.status_code}: {resp.text[:200]}"}

            result = resp.json()
            matches = result.get("matches", [])

            # Process errors using SSDigimark style
            errors = []
            for match in matches:
                better = match.get("replacements", [])
                suggestion = better[0]['value'] if better else match['context']['text'][match['context']['offset']:match['context']['offset'] + match['length']]

                errors.append({
                    "offset": match["offset"],
                    "length": match["length"],
                    "message": match["message"],
                    "better": suggestion
                })

            # Apply SSDigimark highlighting with markers
            highlighted_text, corrected_text = self._highlight_text_with_markers(text, errors)
            
            # Debug logging
            logger.info(f"Grammar check: Found {len(errors)} errors")
            logger.info(f"Original text: {text[:100]}...")
            logger.info(f"Corrected text: {corrected_text[:100]}...")

            # Convert errors to corrections format for UI
            corrections = []
            for error in errors:
                rule_info = next((m.get("rule", {}) for m in matches if m.get("offset") == error["offset"]), {})
                ctype = rule_info.get("issueType") or (rule_info.get("category", {}) or {}).get("id") or "Grammar"
                
                corrections.append({
                    "type": ctype,
                    "original": text[error["offset"]:error["offset"] + error["length"]],
                    "suggestion": error["better"],
                    "reason": error["message"]
                })

            return {
                "success": True,
                "original_text": text,
                "corrected_text": corrected_text,
                "highlighted_text": highlighted_text,
                "corrections": corrections,
                "count": len(corrections)
            }
        except Exception as e:
            logger.error(f"Grammar check error: {e}")
            return {"success": False, "error": str(e)}

    def _highlight_text_with_markers(self, text, matches):
        """Highlight text with markers using SSDigimark style highlighting."""
        highlighted = text
        corrected = text
        offset = 0

        # Apply highlighting markers
        for match in matches:
            offset_start = match['offset'] + offset
            error_length = match['length']

            start_marker = "[!! "
            end_marker = " !!]"

            highlighted = (
                highlighted[:offset_start] +
                start_marker +
                highlighted[offset_start:offset_start + error_length] +
                end_marker +
                highlighted[offset_start + error_length:]
            )
            offset += len(start_marker) + len(end_marker)

        # Apply basic correction (reverse order to avoid offset conflicts)
        corrected_list = list(corrected)
        for match in sorted(matches, key=lambda x: -x['offset']):
            start = match['offset']
            end = start + match['length']
            suggestion = match['better']
            
            # Replace the error with the suggestion
            if start < len(corrected_list) and end <= len(corrected_list):
                corrected_list[start:end] = list(suggestion)
        
        corrected = ''.join(corrected_list)

        return highlighted, corrected

    def process_grammar_check(self, text, language="en"):
        """Basic grammar check placeholder"""
        # This is a placeholder - you can integrate actual grammar checking here
        return {
            'original_text': text,
            'corrected_text': text,
            'errors': [],
            'score': 85  # Placeholder score
        }

    def generate_questions(self, topic, difficulty="medium", num_questions=5):
        """Question generation placeholder"""
        # This is a placeholder - you can integrate actual question generation here
        questions = []
        for i in range(num_questions):
            questions.append({
                'question': f"Sample question {i+1} about {topic}",
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 'Option A',
                'difficulty': difficulty
            })
        return questions

    def get_system_info(self):
        """Get system information"""
        return {
            'watson_available': self.watson_ocr is not None,
            'python_version': sys.version,
            'platform': sys.platform
        }

# Create global backend instance
backend = Backend()

if __name__ == "__main__":
    print("Simplified Backend with Watson OCR loaded!")
    print(f"Watson OCR Available: {backend.is_available()}")
    status = backend.check_status()
    print(f"Status: {status}")
