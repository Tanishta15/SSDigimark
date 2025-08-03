import os
import re
import pandas as pd
import pypdfium2 as pdfium
import easyocr
import numpy as np
from typing import List, Dict, Tuple
import unicodedata

class MPSCQuestionExtractor:
    def __init__(self, pdf_folder: str = "MPSC papers"):
        self.pdf_folder = pdf_folder
        self.reader = easyocr.Reader(['en'])  # Only English
        self.question_patterns = [
            r'(\d+)\.\s*([A-Z].*?)(?=\d+\.|$)',  # 1. Question text
            r'Q\.?\s*(\d+)\s*[\):\.]?\s*([A-Z].*?)(?=Q\.?\s*\d+|$)',  # Q1) or Q.1: Question text
            r'(\d+)\)\s*([A-Z].*?)(?=\d+\)|$)',  # 1) Question text
            r'Question\s*(\d+)\s*[\):\.]?\s*([A-Z].*?)(?=Question\s*\d+|$)',  # Question 1: text
            r'(\d+)[\):\.]([A-Z][^0-9]*?)(?=\d+[\):\.]\s*[A-Z]|$)',  # Various number formats
            r'(\d+)\s+([A-Z][^0-9]*?)(?=\d+\s+[A-Z]|$)'  # Space separated numbers
        ]
    
    def is_english_text(self, text: str) -> bool:
        """Check if text is primarily English"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Remove common punctuation and numbers
        clean_text = re.sub(r'[0-9\.,;:!()\[\]{}\'\"@#$%^&*+=<>?/\\|`~\-_]', '', text)
        clean_text = clean_text.replace(' ', '')
        
        if len(clean_text) < 3:
            return False
        
        # Count Latin characters vs others
        latin_chars = 0
        total_chars = 0
        
        for char in clean_text:
            if char.isalpha():
                total_chars += 1
                # Check if character is in Latin script (English)
                if 'LATIN' in unicodedata.name(char, ''):
                    latin_chars += 1
                # Also consider common English characters
                elif ord(char) < 128:  # ASCII range
                    latin_chars += 1
        
        if total_chars == 0:
            return False
        
        # Consider it English if >80% of alphabetic characters are Latin/ASCII
        english_ratio = latin_chars / total_chars
        return english_ratio > 0.8
    
    def filter_english_lines(self, text_lines: List[str]) -> List[str]:
        """Filter out Hindi lines and keep only English content"""
        english_lines = []
        
        for line in text_lines:
            line = line.strip()
            if self.is_english_text(line):
                english_lines.append(line)
        
        return english_lines
    
    def extract_text_direct(self, pdf_path: str) -> str:
        """Extract text directly from PDF if it contains text"""
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            all_text = ""
            
            for page_num in range(len(pdf)):
                page = pdf.get_page(page_num)
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                all_text += text + "\n"
                textpage.close()
                page.close()
            
            pdf.close()
            return all_text
        except Exception as e:
            print(f"Direct text extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR for image-based PDFs"""
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            all_text = ""
            
            for page_num in range(len(pdf)):
                page = pdf.get_page(page_num)
                pil_image = page.render(scale=2.0).to_pil()
                
                # Convert PIL image to numpy array for EasyOCR
                img_array = np.array(pil_image)
                
                # Use OCR to extract text
                result = self.reader.readtext(img_array)
                
                # Extract text from OCR results
                page_text = []
                for (bbox, text, conf) in result:
                    if conf > 0.5:  # Only confident detections
                        page_text.append(text)
                
                # Filter English lines
                english_lines = self.filter_english_lines(page_text)
                all_text += " ".join(english_lines) + "\n"
                
                page.close()
            
            pdf.close()
            return all_text
        except Exception as e:
            print(f"OCR extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_questions_from_text(self, text: str, source_file: str) -> List[Dict]:
        """Extract numbered questions from text using multiple patterns"""
        questions = []
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        # Filter to keep only English text
        lines = text.split('\n')
        english_lines = self.filter_english_lines(lines)
        clean_text = ' '.join(english_lines)
        
        # Try each pattern
        for pattern in self.question_patterns:
            matches = re.findall(pattern, clean_text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if len(match) == 2:
                    question_num, question_text = match
                    question_text = question_text.strip()
                    
                    # Clean up the question text
                    question_text = re.sub(r'\s+', ' ', question_text)
                    question_text = re.sub(r'^\W+', '', question_text)  # Remove leading punctuation
                    
                    # Validate question (should be substantial English text)
                    if (len(question_text) > 20 and 
                        self.is_english_text(question_text) and
                        not question_text.lower().startswith('page') and
                        not question_text.lower().startswith('section')):
                        
                        questions.append({
                            'source': source_file,
                            'question_number': question_num,
                            'question': question_text,
                            'extraction_method': 'pattern_matching'
                        })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for q in questions:
            # Create a key based on first 50 characters of question
            key = q['question'][:50].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_questions.append(q)
        
        return unique_questions
    
    def extract_from_single_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract questions from a single PDF file"""
        filename = os.path.basename(pdf_path)
        print(f"Processing {filename}...")
        
        # Try direct text extraction first
        text = self.extract_text_direct(pdf_path)
        extraction_method = "direct_text"
        
        # If direct extraction doesn't yield much, try OCR
        if len(text.strip()) < 100:
            print(f"  Direct text extraction insufficient, using OCR...")
            text = self.extract_text_with_ocr(pdf_path)
            extraction_method = "ocr"
        
        # Extract questions from text
        questions = self.extract_questions_from_text(text, filename)
        
        # Update extraction method in results
        for q in questions:
            q['extraction_method'] = extraction_method
        
        print(f"  Extracted {len(questions)} English questions using {extraction_method}")
        return questions
    
    def extract_all_mpsc_questions(self) -> pd.DataFrame:
        """Extract questions from all MPSC PDFs"""
        if not os.path.exists(self.pdf_folder):
            print(f"MPSC papers folder '{self.pdf_folder}' not found!")
            return pd.DataFrame()
        
        all_questions = []
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        pdf_files.sort()  # Sort for consistent processing
        
        print(f"Found {len(pdf_files)} MPSC PDF files to process...")
        print("="*50)
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            try:
                questions = self.extract_from_single_pdf(pdf_path)
                all_questions.extend(questions)
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
        
        # Create DataFrame
        if all_questions:
            df = pd.DataFrame(all_questions)
            
            # Add metadata
            df['year'] = df['source'].str.extract(r'(\d{4})')
            df['paper_number'] = df['source'].str.extract(r'_(\d+)\.pdf')
            
            # Reorder columns
            column_order = ['source', 'year', 'paper_number', 'question_number', 'question', 'extraction_method']
            df = df[column_order]
            
            print("="*50)
            print(f"Total questions extracted: {len(df)}")
            
            # Show breakdown by year
            year_counts = df['year'].value_counts().sort_index()
            print("\nQuestions by year:")
            for year, count in year_counts.items():
                print(f"  {year}: {count} questions")
            
            return df
        else:
            print("No questions were extracted!")
            return pd.DataFrame()
    
    def save_results(self, df: pd.DataFrame, output_file: str = "mpsc_questions_extracted.csv"):
        """Save extracted questions to CSV file"""
        if not df.empty:
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\nResults saved to: {output_file}")
            
            # Show sample questions
            print(f"\nSample extracted questions:")
            for i, row in df.head(3).iterrows():
                print(f"\n{row['year']} Paper {row['paper_number']}, Q{row['question_number']}:")
                print(f"  {row['question'][:100]}...")
        else:
            print("No data to save!")

def main():
    """Main function to extract MPSC questions"""
    print("MPSC Question Extraction System")
    print("="*50)
    print("Extracting English questions only (filtering out Hindi)")
    print()
    
    # Initialize extractor
    extractor = MPSCQuestionExtractor()
    
    # Extract questions
    df = extractor.extract_all_mpsc_questions()
    
    # Save results
    extractor.save_results(df)
    
    print("\nMPSC question extraction completed!")

if __name__ == "__main__":
    main()
