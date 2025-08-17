import streamlit as st
import pandas as pd
import os
import sys
from typing import Dict, List
import random
import io
import traceback
import re
from datetime import datetime
import pypdfium2 as pdfium
import easyocr
import numpy as np
import unicodedata
try:
    from tkinter import filedialog
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# Add the current directory to the path to import the question generator
sys.path.append(os.path.dirname(__file__))

# Import the modified question generator
from generate_mppsc_questions import MPPSCQuestionGenerator


def select_folder_path():
    """Open a folder selection dialog and return the selected path"""
    if not TKINTER_AVAILABLE:
        st.warning("⚠️ Folder browser not available. Please enter path manually.")
        return None
    
    try:
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.wm_attributes('-topmost', 1)  # Bring dialog to front
        
        # Open folder selection dialog
        folder_path = filedialog.askdirectory(
            title="Select Folder Containing PDF/Text Files",
            initialdir=os.path.expanduser("~")  # Start in user's home directory
        )
        
        root.destroy()  # Clean up
        return folder_path if folder_path else None
        
    except Exception as e:
        st.error(f"Error opening folder browser: {str(e)}")
        return None


class AdvancedQuestionExtractor:
    """Advanced question extraction with OCR support"""
    
    def __init__(self):
        self.reader = None  # Initialize OCR reader only when needed
        self.question_patterns = [
            # Direct questions with question marks
            r'([A-Z][^?]*\?)',  # Any sentence ending with ?
            
            # Numbered questions with question marks
            r'(\d+)[\.\)]\s*([A-Z][^?]*\?)',  # 1. Question? or 1) Question?
            
            # Questions with "What", "Which", "Where", "When", "Why", "How"
            r'((?:What|Which|Where|When|Why|How|Who|Name|Define|Explain|Describe|Mention|Write|Give|State)\s+[^?]+\?)',
            
            # Short answer patterns for MPPSC
            r'(\d+)[\.\)]\s*([A-Z][^?]*?)(?:\s*\d+[\.\)]|$)',  # 1. Statement (without ?)
            
            # Questions without question marks but clear question words
            r'((?:What|Which|Where|When|Why|How|Who)\s+[^\.]{10,100})',
            
            # MPPSC specific patterns
            r'([A-Z][^\.]*(?:situated|located|found|called|known|famous|capital|objective|meaning|definition|aim|purpose)[^\.]*)',
        ]
        
        # Patterns to exclude (instruction text, headers, etc.)
        self.exclude_patterns = [
            r'This question contains',
            r'Answer each question',
            r'All questions are compulsory',
            r'Each question carries',
            r'very short answer type',
            r'short answer type',
            r'long answer type',
            r'marks\s*\.',
            r'P\.T\.O\.',
            r'SECTION',
            r'Que\.\s*:',
            r'^\d+\s*$',  # Just numbers
            r'words/\d+\s+to\s+\d+\s+lines',
            r'ideally in \d+ words',
            r'maximum \d+ to \d+ words',
        ]
    
    def init_ocr_reader(self):
        """Initialize OCR reader only when needed"""
        if self.reader is None:
            self.reader = easyocr.Reader(['en'])
    
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
                try:
                    if 'LATIN' in unicodedata.name(char, ''):
                        latin_chars += 1
                    # Also consider common English characters
                    elif ord(char) < 128:  # ASCII range
                        latin_chars += 1
                except ValueError:
                    # Character doesn't have a unicode name
                    if ord(char) < 128:
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
    
    def extract_text_direct(self, file_content, file_name: str) -> str:
        """Extract text directly from PDF if it contains text"""
        try:
            if isinstance(file_content, str):
                # It's a file path
                pdf = pdfium.PdfDocument(file_content)
            else:
                # It's file content
                pdf = pdfium.PdfDocument(file_content)
            
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
            st.warning(f"Direct text extraction failed for {file_name}: {e}")
            return ""
    
    def extract_text_with_ocr(self, file_content, file_name: str, max_pages: int = 10) -> str:
        """Extract text using OCR for image-based PDFs"""
        try:
            self.init_ocr_reader()
            
            if isinstance(file_content, str):
                # It's a file path
                pdf = pdfium.PdfDocument(file_content)
            else:
                # It's file content
                pdf = pdfium.PdfDocument(file_content)
            
            all_text = ""
            
            for page_num in range(min(max_pages, len(pdf))):  # Use configurable max_pages
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
            st.error(f"OCR extraction failed for {file_name}: {e}")
            return ""
    
    def extract_questions_from_text_advanced(self, text: str, source_file: str) -> List[Dict]:
        """Extract numbered questions from text using advanced patterns"""
        questions = []
        
        # Clean the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        
        # Filter to keep only English text
        lines = text.split('\n')
        english_lines = self.filter_english_lines(lines)
        clean_text = ' '.join(english_lines)
        
        # Split text into sentences for better extraction
        sentences = re.split(r'[.!]\s+', clean_text)
        
        # Try each pattern
        for pattern in self.question_patterns:
            matches = re.findall(pattern, clean_text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                # Handle different match formats
                if isinstance(match, tuple) and len(match) == 2:
                    question_num, question_text = match
                elif isinstance(match, tuple) and len(match) == 1:
                    question_num = "auto"
                    question_text = match[0]
                else:
                    question_num = "auto"
                    question_text = match
                
                question_text = question_text.strip()
                
                # Skip if it matches exclude patterns
                if any(re.search(exclude_pattern, question_text, re.IGNORECASE) for exclude_pattern in self.exclude_patterns):
                    continue
                
                # Clean up the question text
                question_text = re.sub(r'\s+', ' ', question_text)
                question_text = re.sub(r'^\W+', '', question_text)  # Remove leading punctuation
                question_text = re.sub(r'\s*\d+\s*$', '', question_text)  # Remove trailing numbers
                
                # Enhanced validation for actual questions
                if (len(question_text) > 15 and 
                    len(question_text) < 300 and  # Not too long
                    self.is_english_text(question_text) and
                    not question_text.lower().startswith('page') and
                    not question_text.lower().startswith('section') and
                    not question_text.lower().startswith('this question') and
                    not question_text.lower().startswith('answer each') and
                    not re.search(r'\d+\s*marks', question_text.lower()) and
                    not 'compulsory' in question_text.lower() and
                    self._is_actual_question(question_text)):
                    
                    # Determine subject/topic from context
                    subject = "General Studies"
                    topic = "Mixed Topics"
                    difficulty = "Medium"
                    
                    # Simple subject classification based on keywords
                    question_lower = question_text.lower()
                    if any(word in question_lower for word in ['constitution', 'article', 'amendment', 'parliament', 'government', 'election', 'democracy']):
                        subject = "Polity"
                        topic = "Constitutional Law"
                    elif any(word in question_lower for word in ['economy', 'gdp', 'inflation', 'budget', 'tax', 'banking', 'msp', 'poverty']):
                        subject = "Economy"
                        topic = "Economic Development"
                    elif any(word in question_lower for word in ['history', 'ancient', 'medieval', 'british', 'freedom', 'independence', 'dynasty', 'empire']):
                        subject = "History"
                        topic = "Indian History"
                    elif any(word in question_lower for word in ['geography', 'climate', 'river', 'mountain', 'ocean', 'continent', 'plateau', 'rainfall']):
                        subject = "Geography"
                        topic = "Physical Geography"
                    elif any(word in question_lower for word in ['science', 'physics', 'chemistry', 'biology', 'technology', 'computer', 'energy']):
                        subject = "Science & Technology"
                        topic = "General Science"
                    
                    questions.append({
                        'question': question_text,
                        'subject': subject,
                        'topic': topic,
                        'type': 'MCQ',
                        'difficulty': difficulty,
                        'source': f'Extracted from {source_file}',
                        'source_file': source_file,
                        'question_number': question_num,
                        'year': datetime.now().year
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
    
    def _is_actual_question(self, text: str) -> bool:
        """Check if text is likely an actual question"""
        text_lower = text.lower()
        
        # Question indicators
        question_indicators = [
            text.endswith('?'),  # Ends with question mark
            any(text_lower.startswith(word) for word in ['what', 'which', 'where', 'when', 'why', 'how', 'who', 'name', 'define', 'explain', 'describe', 'mention', 'write', 'give', 'state']),
            'is' in text_lower and ('?' in text or len(text) > 20),
            'are' in text_lower and ('?' in text or len(text) > 20),
            any(word in text_lower for word in ['situated', 'located', 'called', 'known as', 'famous for', 'capital of', 'objective', 'meaning', 'definition'])
        ]
        
        # Must have at least one question indicator
        if not any(question_indicators):
            return False
        
        # Exclude common non-question patterns
        exclude_phrases = [
            'this question contains',
            'answer each question',
            'all questions are',
            'each question carries',
            'marks)',
            'word limit',
            'time limit',
            'instructions:',
            'note:',
            'section -',
            'part -'
        ]
        
        return not any(phrase in text_lower for phrase in exclude_phrases)


def extract_questions_from_text(text_content):
    """
    Extract questions from text content using improved pattern matching.
    """
    questions = []
    
    # Enhanced question patterns for MPPSC papers
    patterns = [
        # Direct questions with question marks
        r'([A-Z][^?]*\?)',
        
        # Questions starting with question words
        r'((?:What|Which|Who|When|Where|Why|How|Name|Define|Explain|Describe|Mention|Write|Give|State)\s+[^?]+\?)',
        
        # MPPSC specific question patterns
        r'([A-Z][^\.]*(?:situated|located|found|called|known|famous|capital|objective|meaning|definition|aim|purpose)[^\.]*\?)',
        
        # Questions without question marks but clear indicators
        r'((?:What|Which|Where|When|Why|How|Who)\s+[^\.]{15,100})',
    ]
    
    # Exclude patterns (instruction text)
    exclude_patterns = [
        r'This question contains',
        r'Answer each question',
        r'All questions are compulsory',
        r'Each question carries',
        r'very short answer type',
        r'short answer type',
        r'long answer type',
        r'marks\s*\.',
        r'P\.T\.O\.',
        r'SECTION',
        r'words/\d+\s+to\s+\d+\s+lines',
        r'ideally in \d+ words',
        r'maximum \d+ to \d+ words',
    ]
    
    question_set = set()  # To avoid duplicates
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            question_text = match.group(1).strip()
            
            # Skip if it matches exclude patterns
            if any(re.search(exclude_pattern, question_text, re.IGNORECASE) for exclude_pattern in exclude_patterns):
                continue
            
            # Clean up the question
            question_text = re.sub(r'\s+', ' ', question_text)  # Remove extra whitespace
            question_text = question_text.strip()
            
            # Enhanced validation
            if (len(question_text) >= 15 and 
                len(question_text) <= 300 and 
                question_text not in question_set and
                not question_text.lower().startswith('this question') and
                not question_text.lower().startswith('answer each') and
                not re.search(r'\d+\s*marks', question_text.lower()) and
                not 'compulsory' in question_text.lower()):
                
                question_set.add(question_text)
                
                # Try to determine subject/topic from context
                subject = "General Studies"
                topic = "Mixed Topics"
                difficulty = "Medium"
                
                # Enhanced subject classification
                question_lower = question_text.lower()
                if any(word in question_lower for word in ['constitution', 'article', 'amendment', 'parliament', 'government', 'election', 'democracy']):
                    subject = "Polity"
                    topic = "Constitutional Law"
                elif any(word in question_lower for word in ['economy', 'gdp', 'inflation', 'budget', 'tax', 'banking', 'msp', 'poverty']):
                    subject = "Economy"
                    topic = "Economic Development"
                elif any(word in question_lower for word in ['history', 'ancient', 'medieval', 'british', 'freedom', 'independence', 'dynasty', 'empire']):
                    subject = "History"
                    topic = "Indian History"
                elif any(word in question_lower for word in ['geography', 'climate', 'river', 'mountain', 'ocean', 'continent', 'plateau', 'rainfall']):
                    subject = "Geography"
                    topic = "Physical Geography"
                elif any(word in question_lower for word in ['science', 'physics', 'chemistry', 'biology', 'technology', 'computer', 'energy']):
                    subject = "Science & Technology"
                    topic = "General Science"
                
                questions.append({
                    'question': question_text,
                    'subject': subject,
                    'topic': topic,
                    'type': 'MCQ',
                    'difficulty': difficulty,
                    'source': 'Extracted from Text',
                    'year': datetime.now().year
                })
    
    return questions[:50]  # Limit to 50 questions to avoid overwhelming


def process_single_file(file_content, file_name, file_type, max_pages=10):
    """Process a single file and extract questions using smart extraction (direct text + OCR fallback)"""
    try:
        extractor = AdvancedQuestionExtractor()
        
        if file_type == 'txt':
            # Handle text files
            if isinstance(file_content, bytes):
                text_content = str(file_content, "utf-8")
            else:
                text_content = file_content
            extracted_questions = extractor.extract_questions_from_text_advanced(text_content, file_name)
            
        elif file_type == 'pdf':
            # Handle PDF files with smart extraction: try direct first, then OCR
            st.info(f"📄 Processing {file_name}...")
            
            # Try direct text extraction first
            text = extractor.extract_text_direct(file_content, file_name)
            extraction_method = "direct_text"
            
            # If direct extraction doesn't yield much, use OCR
            if len(text.strip()) < 100:
                st.info(f"🔍 Direct extraction insufficient for {file_name}, using OCR (max {max_pages} pages)...")
                text = extractor.extract_text_with_ocr(file_content, file_name, max_pages)
                extraction_method = "ocr"
            else:
                st.success(f"✅ Direct text extraction successful for {file_name}")
            
            # Extract questions from text
            extracted_questions = extractor.extract_questions_from_text_advanced(text, file_name)
            
            # Update extraction method in results
            for q in extracted_questions:
                q['extraction_method'] = extraction_method
        else:
            return []
        
        # Add file source information to questions
        for q in extracted_questions:
            if 'source' not in q:
                q['source'] = f'Extracted from {file_name} ({extraction_method if file_type == "pdf" else "text"})'
            if 'source_file' not in q:
                q['source_file'] = file_name
            
        return extracted_questions
        
    except Exception as e:
        st.error(f"Error processing file {file_name}: {str(e)}")
        return []


def process_multiple_files(uploaded_files, max_pages=10):
    """Process multiple uploaded files"""
    if not uploaded_files:
        return
    
    all_extracted_questions = []
    file_results = []
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        file_type = uploaded_file.name.split('.')[-1].lower()
        status_text.text(f"Processing {uploaded_file.name}...")
        
        file_content = uploaded_file.read()
        extracted_questions = process_single_file(file_content, uploaded_file.name, file_type, max_pages)
        
        if extracted_questions:
            all_extracted_questions.extend(extracted_questions)
            file_results.append({
                'file_name': uploaded_file.name,
                'questions_count': len(extracted_questions),
                'file_type': file_type.upper()
            })
        else:
            file_results.append({
                'file_name': uploaded_file.name,
                'questions_count': 0,
                'file_type': file_type.upper()
            })
        
        # Update progress
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    progress_bar.progress(1.0)
    status_text.text("Processing complete!")
    
    # Store results in session state for persistence
    st.session_state.extraction_results = all_extracted_questions
    st.session_state.extraction_file_results = file_results
    st.session_state.extraction_source = "Multiple Files"
    st.session_state.extraction_timestamp = datetime.now()
    
    # Display results
    display_extraction_results(all_extracted_questions, file_results, "Multiple Files")


def process_folder_files(folder_path, max_pages=10):
    """Process all PDF and text files in a folder using smart extraction (direct + OCR)"""
    try:
        if not os.path.exists(folder_path):
            st.error(f"Folder path does not exist: {folder_path}")
            return
        
        # Find all PDF and text files
        supported_extensions = ['.pdf', '.txt']
        files_to_process = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    files_to_process.append(os.path.join(root, file))
        
        if not files_to_process:
            st.warning(f"No PDF or text files found in: {folder_path}")
            return
        
        st.info(f"Found {len(files_to_process)} files to process with smart extraction (direct text + OCR fallback, max {max_pages} pages per PDF)")
        
        all_extracted_questions = []
        file_results = []
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file_path in enumerate(files_to_process):
            file_name = os.path.basename(file_path)
            file_type = file_path.split('.')[-1].lower()
            status_text.text(f"Processing {file_name}...")
            
            try:
                extracted_questions = process_single_file(file_path, file_name, file_type, max_pages)
                
                if extracted_questions:
                    all_extracted_questions.extend(extracted_questions)
                    file_results.append({
                        'file_name': file_name,
                        'questions_count': len(extracted_questions),
                        'file_type': file_type.upper()
                    })
                else:
                    file_results.append({
                        'file_name': file_name,
                        'questions_count': 0,
                        'file_type': file_type.upper()
                    })
                    
            except Exception as e:
                st.error(f"Error processing {file_name}: {str(e)}")
                file_results.append({
                    'file_name': file_name,
                    'questions_count': 0,
                    'file_type': file_type.upper()
                })
            
            # Update progress
            progress_bar.progress((i + 1) / len(files_to_process))
        
        progress_bar.progress(1.0)
        status_text.text("Smart extraction processing complete!")
        
        # Store results in session state for persistence
        st.session_state.extraction_results = all_extracted_questions
        st.session_state.extraction_file_results = file_results
        st.session_state.extraction_source = f"Folder: {folder_path}"
        st.session_state.extraction_timestamp = datetime.now()
        
        # Display results
        display_extraction_results(all_extracted_questions, file_results, f"Folder: {folder_path}")
        
    except Exception as e:
        st.error(f"Error processing folder: {str(e)}")


def display_extraction_results(all_extracted_questions, file_results, source_description):
    """Display extraction results for multiple files"""
    if not all_extracted_questions:
        st.warning("⚠️ No questions could be extracted from any of the files.")
        
        # Show file processing summary
        if file_results:
            st.subheader("📊 File Processing Summary")
            df_results = pd.DataFrame(file_results)
            st.dataframe(df_results, use_container_width=True)
        
        st.info("""
        **Tips for better extraction:**
        - Ensure questions end with question marks (?)
        - Use clear numbering (1. 2. 3.) or Q1, Q2, Q3 format
        - Avoid overly complex formatting
        - Text should be readable (not scanned images)
        """)
        return
    
    st.success(f"✅ Successfully extracted {len(all_extracted_questions)} questions from {len(file_results)} files!")
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Questions", len(all_extracted_questions))
    with col2:
        st.metric("Files Processed", len(file_results))
    with col3:
        subjects = set(q['subject'] for q in all_extracted_questions)
        st.metric("Subjects Detected", len(subjects))
    with col4:
        successful_files = len([f for f in file_results if f['questions_count'] > 0])
        st.metric("Successful Extractions", successful_files)
    
    # File processing summary
    with st.expander("📊 File Processing Summary"):
        df_results = pd.DataFrame(file_results)
        st.dataframe(df_results, use_container_width=True)
        
        # Show statistics
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Questions per File:**")
            for result in file_results:
                if result['questions_count'] > 0:
                    st.write(f"• {result['file_name']}: {result['questions_count']} questions")
        with col2:
            st.write("**File Types Processed:**")
            file_type_counts = {}
            for result in file_results:
                file_type = result['file_type']
                file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
            for file_type, count in file_type_counts.items():
                st.write(f"• {file_type}: {count} files")
    
    # Subject distribution
    with st.expander("📊 Subject Distribution"):
        subject_counts = {}
        for q in all_extracted_questions:
            subject = q['subject']
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        for subject, count in subject_counts.items():
            percentage = (count / len(all_extracted_questions)) * 100
            st.write(f"**{subject}:** {count} questions ({percentage:.1f}%)")
    
    # Preview questions
    st.subheader("📝 Extracted Questions Preview")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_subject = st.selectbox(
            "Filter by Subject:",
            ["All Subjects"] + list(set(q['subject'] for q in all_extracted_questions))
        )
    with col2:
        selected_file = st.selectbox(
            "Filter by Source File:",
            ["All Files"] + list(set(q.get('source_file', 'Unknown') for q in all_extracted_questions))
        )
    with col3:
        preview_count = st.slider("Questions to preview:", 5, min(30, len(all_extracted_questions)), 15)
    
    # Filter questions
    filtered_questions = all_extracted_questions
    if selected_subject != "All Subjects":
        filtered_questions = [q for q in filtered_questions if q['subject'] == selected_subject]
    if selected_file != "All Files":
        filtered_questions = [q for q in filtered_questions if q.get('source_file') == selected_file]
    
    # Display preview
    for i, question in enumerate(filtered_questions[:preview_count], 1):
        with st.container():
            st.markdown(f"""
            <div class="question-card" style="border-left: 4px solid #28a745;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: inherit;">Q{i}</h4>
                    <div>
                        <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">
                            {question['subject']}
                        </span>
                        <span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                            {question.get('source_file', 'Unknown')}
                        </span>
                    </div>
                </div>
                <div style="color: inherit;">
                    <p><strong>Topic:</strong> {question['topic']}</p>
                    <p style="margin: 0; line-height: 1.6; font-size: 1.1em; color: inherit;">{question['question']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    if len(filtered_questions) > preview_count:
        st.info(f"Showing {preview_count} of {len(filtered_questions)} questions. Use the slider to see more.")
    
    # Actions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to Session", use_container_width=True):
            if 'generated_questions' not in st.session_state:
                st.session_state.generated_questions = []
            
            # Add extracted questions to session
            st.session_state.generated_questions.extend(all_extracted_questions)
            st.success(f"Added {len(all_extracted_questions)} questions to session!")
            st.balloons()
    
    with col2:
        # Download CSV
        df = pd.DataFrame(all_extracted_questions)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"batch_extracted_questions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Download text format
        text_output = f"EXTRACTED QUESTIONS FROM {source_description.upper()}\n"
        text_output += f"Extracted on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text_output += f"Total Questions: {len(all_extracted_questions)}\n"
        text_output += f"Files Processed: {len(file_results)}\n\n"
        
        # Group by file
        questions_by_file = {}
        for q in all_extracted_questions:
            file_name = q.get('source_file', 'Unknown')
            if file_name not in questions_by_file:
                questions_by_file[file_name] = []
            questions_by_file[file_name].append(q)
        
        for file_name, questions in questions_by_file.items():
            text_output += f"\n=== {file_name} ({len(questions)} questions) ===\n\n"
            for i, q in enumerate(questions, 1):
                text_output += f"{i}. {q['question']}\n"
                text_output += f"   Subject: {q['subject']} | Topic: {q['topic']}\n\n"
        
        st.download_button(
            label="📄 Download Text",
            data=text_output,
            file_name=f"batch_extracted_questions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )


st.set_page_config(
    page_title="MPPSC Question Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (dark mode compatible)
st.markdown("""
<style>
/* Main header styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Subject box styling - works in both light and dark mode */
.subject-box {
    background: var(--background-color, #f8f9fa);
    border: 1px solid var(--border-color, #dee2e6);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #007bff;
    color: var(--text-color, #333);
}

/* Question card styling - enhanced for dark mode */
.question-card {
    background: var(--card-background, white);
    border: 1px solid var(--border-color, #e0e0e0);
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: var(--text-color, #333);
}

/* Stats card styling */
.stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 8px;
    color: white !important;
    text-align: center;
    margin: 0.5rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Dark mode specific overrides */
@media (prefers-color-scheme: dark) {
    .subject-box {
        background: #2d3748 !important;
        border-color: #4a5568 !important;
        color: #e2e8f0 !important;
    }
    
    .question-card {
        background: #2d3748 !important;
        border-color: #4a5568 !important;
        color: #e2e8f0 !important;
    }
}

/* Streamlit dark theme detection */
.stApp[data-theme="dark"] .subject-box {
    background: #262730 !important;
    border-color: #464852 !important;
    color: #fafafa !important;
}

.stApp[data-theme="dark"] .question-card {
    background: #262730 !important;
    border-color: #464852 !important;
    color: #fafafa !important;
}

/* Force visibility for important text */
.question-card h4, 
.question-card p, 
.question-card strong {
    color: inherit !important;
}

/* Enhanced contrast for readability */
.question-card hr {
    border-color: var(--border-color, #dee2e6);
    opacity: 0.3;
}

/* Success/error message styling */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 8px;
}

/* File uploader styling */
.uploadedFile {
    border-radius: 8px;
    border: 2px dashed #007bff;
    padding: 1rem;
}

/* Metric containers */
.metric-container {
    background: var(--card-background, white);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    color: var(--text-color, #333);
}

/* Expander styling */
.streamlit-expander {
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    background: var(--card-background, white);
}

/* Button styling */
.stButton > button {
    border-radius: 8px;
    border: none;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Download button specific styling */
.stDownloadButton > button {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    color: white;
    border-radius: 8px;
    font-weight: 600;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    background-color: var(--card-background, #f8f9fa);
    color: var(--text-color, #333);
}

/* Checkbox and radio styling */
.stCheckbox, .stRadio {
    color: var(--text-color, #333) !important;
}

/* Slider styling */
.stSlider {
    color: var(--text-color, #333) !important;
}

/* Progress bar styling */
.stProgress .st-bo {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Selectbox styling */
.stSelectbox label, .stMultiSelect label {
    color: var(--text-color, #333) !important;
    font-weight: 600;
}

/* Text area styling */
.stTextArea label {
    color: var(--text-color, #333) !important;
    font-weight: 600;
}

/* File uploader label */
.stFileUploader label {
    color: var(--text-color, #333) !important;
    font-weight: 600;
}

/* Ensure all text is visible */
* {
    color: inherit;
}

/* Dark mode text color fixes */
[data-theme="dark"] h1,
[data-theme="dark"] h2,
[data-theme="dark"] h3,
[data-theme="dark"] h4,
[data-theme="dark"] h5,
[data-theme="dark"] h6,
[data-theme="dark"] p,
[data-theme="dark"] span,
[data-theme="dark"] div {
    color: #fafafa !important;
}

/* Light mode text color fixes */
[data-theme="light"] h1,
[data-theme="light"] h2,
[data-theme="light"] h3,
[data-theme="light"] h4,
[data-theme="light"] h5,
[data-theme="light"] h6,
[data-theme="light"] p,
[data-theme="light"] span,
[data-theme="light"] div {
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

class StreamlitMPPSCGenerator(MPPSCQuestionGenerator):
    """Extended MPPSC Generator for Streamlit with user input topics"""
    
    def __init__(self, user_topics: Dict[str, List[str]] = None, **kwargs):
        self.user_topics = user_topics or {}
        super().__init__(**kwargs)
        
    def _load_mppsc_curriculum(self) -> Dict[str, List[str]]:
        """Load user-defined topics if available, otherwise use default"""
        if self.user_topics:
            return self.user_topics
        
        # Default topics if no user input
        return {
            'madhya_pradesh_gk': [
                'Madhya Pradesh History', 'Gond Dynasty', 'Chandela Dynasty', 'Malwa Region',
                'Madhya Pradesh Geography', 'Vindhya Range', 'Satpura Range', 'Narmada River',
                'Chambal River', 'Son River', 'Tapti River', 'Madhya Pradesh Climate', 
                'Madhya Pradesh Economy', 'Madhya Pradesh Industries', 'Madhya Pradesh Agriculture',
                'Madhya Pradesh Culture', 'Madhya Pradesh Literature', 'Madhya Pradesh Arts', 
                'Madhya Pradesh Festivals', 'Khajuraho Temples', 'Sanchi Stupa', 'Ujjain',
                'Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Tribal Culture of MP'
            ],
            'indian_polity': [
                'Indian Constitution', 'Fundamental Rights', 'Directive Principles', 'Parliament',
                'Lok Sabha', 'Rajya Sabha', 'President', 'Prime Minister', 'Council of Ministers',
                'Supreme Court', 'High Courts', 'State Government', 'Local Government',
                'Panchayati Raj', 'Urban Local Bodies', 'Election Commission', 'CAG', 'UPSC'
            ],
            'indian_economy': [
                'Economic Planning', 'Five Year Plans', 'NITI Aayog', 'Budget Process',
                'Fiscal Policy', 'Monetary Policy', 'RBI', 'Banking System', 'Capital Markets',
                'Foreign Trade', 'Economic Reforms', 'Agriculture', 'Industry', 'Services Sector',
                'Employment', 'Poverty', 'Inflation', 'Economic Growth'
            ],
            'indian_history': [
                'Ancient India', 'Indus Valley Civilization', 'Vedic Period', 'Mauryan Empire',
                'Gupta Period', 'Medieval India', 'Delhi Sultanate', 'Mughal Empire',
                'Maratha Empire', 'British Rule', 'Freedom Struggle', 'Modern India'
            ],
            'indian_geography': [
                'Physical Geography', 'Indian Rivers', 'Mountain Ranges', 'Climate', 'Monsoons',
                'Natural Resources', 'Agriculture', 'Industries', 'Transportation', 'Population',
                'Economic Geography', 'Environmental Issues', 'Disaster Management'
            ],
            'general_science': [
                'Physics', 'Chemistry', 'Biology', 'Environmental Science', 'Computer Science',
                'Information Technology', 'Space Technology', 'Nuclear Technology',
                'Biotechnology', 'Medical Science', 'Agricultural Science', 'Science and Technology Policy',
                'Scientific Research'
            ],
            'current_affairs': [
                'Government Schemes', 'Policy Initiatives', 'National Events', 'International Events',
                'Sports', 'Awards', 'Important Personalities', 'Books and Authors',
                'Science and Technology News', 'Economic Developments', 'Political Developments'
            ]
        }
    
    def create_sample_question_paper(self, questions: List[Dict]) -> str:
        """Create a formatted sample question paper"""
        from datetime import datetime
        
        paper = f"""
═══════════════════════════════════════════════════════════════════
                    MPPSC SAMPLE QUESTION PAPER
                  Madhya Pradesh Public Service Commission
═══════════════════════════════════════════════════════════════════

Date: {datetime.now().strftime('%B %d, %Y')}
Time: 2 Hours                                    Maximum Marks: 200
                                                 
Instructions:
1. All questions are compulsory.
2. Each question carries equal marks.
3. Read the questions carefully before answering.
4. Use of calculator is not allowed.

═══════════════════════════════════════════════════════════════════

"""
        
        # Group questions by subject
        subject_wise = {}
        for q in questions:
            subject = q['subject']
            if subject not in subject_wise:
                subject_wise[subject] = []
            subject_wise[subject].append(q)
        
        question_number = 1
        
        for subject, subject_questions in subject_wise.items():
            paper += f"\nSECTION: {subject.replace('_', ' ').upper()}\n"
            paper += "─" * 60 + "\n\n"
            
            for q in subject_questions:
                paper += f"{question_number}. {q['question']}\n\n"
                question_number += 1
        
        paper += "═" * 67 + "\n"
        paper += "                           END OF PAPER\n"
        paper += "═" * 67
        
        return paper

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_topics' not in st.session_state:
        st.session_state.user_topics = {}
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'topics_configured' not in st.session_state:
        st.session_state.topics_configured = False
    # Add persistent extraction results
    if 'extraction_results' not in st.session_state:
        st.session_state.extraction_results = []
    if 'extraction_file_results' not in st.session_state:
        st.session_state.extraction_file_results = []
    if 'extraction_source' not in st.session_state:
        st.session_state.extraction_source = ""
    if 'extraction_timestamp' not in st.session_state:
        st.session_state.extraction_timestamp = None

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 MPPSC Question Generator</h1>
        <p>Generate customized questions for Madhya Pradesh Public Service Commission</p>
    </div>
    """, unsafe_allow_html=True)

def render_topic_input_section():
    """Render the topic input section"""
    st.header("🎯 Configure Your Topics")
    
    # Predefined subjects
    subjects = [
        'madhya_pradesh_gk',
        'indian_polity', 
        'indian_economy',
        'indian_history',
        'indian_geography', 
        'general_science',
        'current_affairs'
    ]
    
    # Create tabs for different subjects
    tabs = st.tabs([subject.replace('_', ' ').title() for subject in subjects])
    
    # Initialize user_topics with existing session state or empty dict
    user_topics = st.session_state.user_topics.copy() if st.session_state.user_topics else {}
    
    for i, (tab, subject) in enumerate(zip(tabs, subjects)):
        with tab:
            st.subheader(f"Topics for {subject.replace('_', ' ').title()}")
            
            # Default topics for this subject
            default_topics = get_default_topics_for_subject(subject)
            
            # Check if we already have data for this subject
            existing_data = user_topics.get(subject, [])
            has_existing = len(existing_data) > 0
            
            # Option to use default or custom topics
            use_default = st.checkbox(f"Use default topics for {subject.replace('_', ' ')}", 
                                    value=not has_existing or len(existing_data) == len(default_topics), 
                                    key=f"default_{subject}")
            
            if use_default:
                user_topics[subject] = default_topics
                st.info(f"✅ Using {len(default_topics)} default topics")
                
                # Show default topics
                with st.expander(f"View default topics for {subject.replace('_', ' ')}"):
                    for topic in default_topics:
                        st.write(f"• {topic}")
            else:
                # Custom topic input
                st.write("Enter your custom topics (one per line):")
                
                # Pre-populate with existing custom data if available
                existing_text = '\n'.join(existing_data) if has_existing and existing_data != default_topics else ""
                
                custom_topics_text = st.text_area(
                    f"Topics for {subject.replace('_', ' ')}",
                    value=existing_text,
                    height=150,
                    placeholder="Enter topics, one per line...",
                    key=f"custom_{subject}"
                )
                
                if custom_topics_text:
                    custom_topics = [topic.strip() for topic in custom_topics_text.split('\n') if topic.strip()]
                    user_topics[subject] = custom_topics
                    st.success(f"✅ Added {len(custom_topics)} custom topics")
                else:
                    user_topics[subject] = []
                    st.warning("No custom topics entered")
    
    return user_topics

def get_default_topics_for_subject(subject):
    """Get default topics for a specific subject"""
    default_curriculum = {
        'madhya_pradesh_gk': [
            'Madhya Pradesh History', 'Gond Dynasty', 'Chandela Dynasty', 'Malwa Region',
            'Madhya Pradesh Geography', 'Vindhya Range', 'Satpura Range', 'Narmada River',
            'Chambal River', 'Son River', 'Tapti River', 'Madhya Pradesh Climate', 
            'Madhya Pradesh Economy', 'Madhya Pradesh Industries', 'Madhya Pradesh Agriculture',
            'Madhya Pradesh Culture', 'Madhya Pradesh Literature', 'Madhya Pradesh Arts', 
            'Madhya Pradesh Festivals', 'Khajuraho Temples', 'Sanchi Stupa', 'Ujjain',
            'Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Tribal Culture of MP'
        ],
        'indian_polity': [
            'Indian Constitution', 'Fundamental Rights', 'Directive Principles', 'Parliament',
            'Lok Sabha', 'Rajya Sabha', 'President', 'Prime Minister', 'Council of Ministers',
            'Supreme Court', 'High Courts', 'State Government', 'Local Government',
            'Panchayati Raj', 'Urban Local Bodies', 'Election Commission', 'CAG', 'UPSC'
        ],
        'indian_economy': [
            'Economic Planning', 'Five Year Plans', 'NITI Aayog', 'Budget Process',
            'Fiscal Policy', 'Monetary Policy', 'RBI', 'Banking System', 'Capital Markets',
            'Foreign Trade', 'Economic Reforms', 'Agriculture', 'Industry', 'Services Sector',
            'Employment', 'Poverty', 'Inflation', 'Economic Growth'
        ],
        'indian_history': [
            'Ancient India', 'Indus Valley Civilization', 'Vedic Period', 'Mauryan Empire',
            'Gupta Period', 'Medieval India', 'Delhi Sultanate', 'Mughal Empire',
            'Maratha Empire', 'British Rule', 'Freedom Struggle', 'Modern India'
        ],
        'indian_geography': [
            'Physical Geography', 'Indian Rivers', 'Mountain Ranges', 'Climate', 'Monsoons',
            'Natural Resources', 'Agriculture', 'Industries', 'Transportation', 'Population',
            'Economic Geography', 'Environmental Issues', 'Disaster Management'
        ],
        'general_science': [
            'Physics', 'Chemistry', 'Biology', 'Environmental Science', 'Computer Science',
            'Information Technology', 'Space Technology', 'Nuclear Technology',
            'Biotechnology', 'Medical Science', 'Agricultural Science', 'Science and Technology Policy',
            'Scientific Research'
        ],
        'current_affairs': [
            'Government Schemes', 'Policy Initiatives', 'National Events', 'International Events',
            'Sports', 'Awards', 'Important Personalities', 'Books and Authors',
            'Science and Technology News', 'Economic Developments', 'Political Developments'
        ]
    }
    return default_curriculum.get(subject, [])

def render_generation_section(user_topics):
    """Render the question generation section"""
    st.header("⚡ Generate Questions")
    
    # Check for extracted questions sent from extraction section
    if hasattr(st.session_state, 'uploaded_questions_for_generation') and st.session_state.uploaded_questions_for_generation:
        st.success("✅ **Extracted Questions Available for Generation**")
        
        with st.expander("📊 View Extracted Questions from Extraction Section", expanded=True):
            extracted_questions = st.session_state.uploaded_questions_for_generation
            
            # Display summary
            total_questions = len(extracted_questions)
            st.info(f"**Total Questions:** {total_questions} | **Source:** {extracted_questions[0].get('source', 'Unknown') if extracted_questions else 'Unknown'}")
            
            # Show questions by subject
            questions_by_subject = {}
            for question_data in extracted_questions:
                subject = question_data.get('subject', 'General Studies')
                if subject not in questions_by_subject:
                    questions_by_subject[subject] = []
                questions_by_subject[subject].append(question_data)
            
            # Display subject distribution
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Subject Distribution:**")
                for subject, questions in questions_by_subject.items():
                    st.write(f"• **{subject}:** {len(questions)} questions")
            
            with col2:
                st.write("**Source Files:**")
                source_files = set(q.get('source_file', 'Unknown') for q in extracted_questions)
                for file_name in source_files:
                    file_count = len([q for q in extracted_questions if q.get('source_file') == file_name])
                    st.write(f"• **{file_name}:** {file_count} questions")
            
            # Preview questions
            with st.expander("📝 Question Preview (First 5)"):
                for i, q in enumerate(extracted_questions[:5], 1):
                    st.write(f"**{i}.** {q.get('question', 'Unknown question')}")
                    st.write(f"   📚 Subject: {q.get('subject', 'Unknown')} | 🎯 Topic: {q.get('topic', 'Unknown')}")
                    st.write("---")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Use These Questions", help="Use extracted questions for generation enhancement"):
                    # Add extracted questions to the main uploaded_questions flow
                    if 'generation_uploaded_questions' not in st.session_state:
                        st.session_state.generation_uploaded_questions = []
                    
                    # Ensure we don't duplicate questions
                    existing_questions = {q.get('question', '')[:50] for q in st.session_state.generation_uploaded_questions}
                    new_questions = []
                    
                    for q in extracted_questions:
                        question_key = q.get('question', '')[:50]
                        if question_key not in existing_questions:
                            new_questions.append(q)
                    
                    st.session_state.generation_uploaded_questions.extend(new_questions)
                    
                    # Clear the uploaded_questions_for_generation to prevent confusion
                    st.session_state.uploaded_questions_for_generation = []
                    
                    st.success(f"✅ Added {len(new_questions)} new extracted questions for generation!")
                    if len(new_questions) < len(extracted_questions):
                        st.info(f"📝 Skipped {len(extracted_questions) - len(new_questions)} duplicate questions")
                    
                    # Show total count
                    total_count = len(st.session_state.generation_uploaded_questions)
                    st.info(f"📊 Total questions available for generation: {total_count}")
                    
                    st.rerun()
            
            with col2:
                if st.button("📊 Download as CSV", help="Download extracted questions as CSV"):
                    df = pd.DataFrame(extracted_questions)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_data,
                        file_name=f"extracted_questions_for_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🗑️ Clear Extracted Questions", help="Remove extracted questions from generation"):
                    st.session_state.uploaded_questions_for_generation = []
                    if hasattr(st.session_state, 'generation_uploaded_questions'):
                        st.session_state.generation_uploaded_questions = []
                    st.success("Extracted questions cleared!")
                    st.rerun()
        
        st.divider()
    
    # CSV Upload Section
    st.subheader("📤 Upload Existing Question Bank (Optional)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a CSV or text file with existing questions to enhance generation",
            type=['csv', 'txt', 'pdf'],
            help="Upload a CSV file with structured data or a text/PDF file to extract questions from"
        )
    
    with col2:
        # Download sample template
        sample_csv = """id,question,subject,topic,type,difficulty,source,year
1,"What is the capital of Madhya Pradesh?",madhya_pradesh_gk,State Capital,factual_mcq,easy,custom,2024
2,"Analyze the impact of Narmada River on MP's economy",madhya_pradesh_gk,Narmada River,analytical,moderate,custom,2024
3,"Which article of the Constitution deals with Fundamental Rights?",indian_polity,Fundamental Rights,factual_mcq,moderate,custom,2024"""
        
        st.download_button(
            label="📄 Download Template",
            data=sample_csv,
            file_name="question_bank_template.csv",
            mime="text/csv",
            help="Download a sample CSV template to understand the format"
        )
    
    uploaded_questions = []
    
    # First, check for extracted questions from extraction section
    if hasattr(st.session_state, 'generation_uploaded_questions') and st.session_state.generation_uploaded_questions:
        uploaded_questions.extend(st.session_state.generation_uploaded_questions)
        st.success(f"📋 Using {len(st.session_state.generation_uploaded_questions)} questions from extraction section")
        
        # Show a preview of what's loaded
        with st.expander("📝 Preview of Loaded Questions", expanded=False):
            for i, q in enumerate(st.session_state.generation_uploaded_questions[:5], 1):
                st.write(f"**{i}.** {q.get('question', 'No question text')[:100]}...")
                st.write(f"   � Subject: {q.get('subject', 'Unknown')} | 🎯 Topic: {q.get('topic', 'Unknown')}")
            
            if len(st.session_state.generation_uploaded_questions) > 5:
                st.write(f"... and {len(st.session_state.generation_uploaded_questions) - 5} more questions")
    
    # Debug section - can be removed later
    if st.checkbox("🔍 Debug Session State", help="Show session state for debugging"):
        st.write("**Session State Keys:**")
        for key in st.session_state.keys():
            if 'generation' in key or 'extraction' in key or 'uploaded' in key:
                value = st.session_state[key]
                if isinstance(value, list):
                    st.write(f"• {key}: {len(value)} items")
                else:
                    st.write(f"• {key}: {value}")
    
    # Then, handle file upload
    if uploaded_file is not None:
        try:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == 'csv':
                # Handle CSV files
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['question', 'subject', 'topic', 'type', 'difficulty']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    st.info("Required columns: id, question, subject, topic, type, difficulty, source, year")
                else:
                    new_questions = df.to_dict('records')
                    
                    # Avoid duplicates
                    existing_questions = {q.get('question', '')[:50] for q in uploaded_questions}
                    unique_new_questions = []
                    
                    for q in new_questions:
                        question_key = q.get('question', '')[:50]
                        if question_key not in existing_questions:
                            unique_new_questions.append(q)
                    
                    uploaded_questions.extend(unique_new_questions)
                    st.success(f"✅ Successfully loaded {len(unique_new_questions)} new questions from CSV")
                    if len(unique_new_questions) < len(new_questions):
                        st.info(f"📝 Skipped {len(new_questions) - len(unique_new_questions)} duplicate questions")
                    
            elif file_type == 'txt':
                # Handle text files
                text_content = str(uploaded_file.read(), "utf-8")
                extractor = AdvancedQuestionExtractor()
                extracted_questions = extractor.extract_questions_from_text_advanced(text_content, uploaded_file.name)
                
                if extracted_questions:
                    # Avoid duplicates
                    existing_questions = {q.get('question', '')[:50] for q in uploaded_questions}
                    unique_extracted_questions = []
                    
                    for q in extracted_questions:
                        question_key = q.get('question', '')[:50]
                        if question_key not in existing_questions:
                            unique_extracted_questions.append(q)
                    
                    uploaded_questions.extend(unique_extracted_questions)
                    st.success(f"✅ Successfully extracted {len(unique_extracted_questions)} new questions from text file")
                    if len(unique_extracted_questions) < len(extracted_questions):
                        st.info(f"📝 Skipped {len(extracted_questions) - len(unique_extracted_questions)} duplicate questions")
                    
                    # Show extraction preview
                    with st.expander("📝 Extracted Questions Preview"):
                        for i, q in enumerate(unique_extracted_questions[:3], 1):
                            st.write(f"**Question {i}:** {q['question'][:100]}...")
                        if len(unique_extracted_questions) > 3:
                            st.write(f"... and {len(unique_extracted_questions) - 3} more questions")
                else:
                    st.warning("No questions could be extracted from the text file")
                    
            elif file_type == 'pdf':
                # Handle PDF files with advanced extraction
                try:
                    extractor = AdvancedQuestionExtractor()
                    file_content = uploaded_file.read()
                    
                    # Try direct text extraction first
                    text = extractor.extract_text_direct(file_content, uploaded_file.name)
                    extraction_method = "direct_text"
                    
                    # If direct extraction doesn't yield much, try OCR
                    if len(text.strip()) < 100:
                        st.info(f"Direct text extraction insufficient, using OCR for {uploaded_file.name}...")
                        text = extractor.extract_text_with_ocr(file_content, uploaded_file.name, 10)
                        extraction_method = "ocr"
                    
                    extracted_questions = extractor.extract_questions_from_text_advanced(text, uploaded_file.name)
                    
                    if extracted_questions:
                        # Update extraction method in results
                        for q in extracted_questions:
                            q['extraction_method'] = extraction_method
                        
                        # Avoid duplicates
                        existing_questions = {q.get('question', '')[:50] for q in uploaded_questions}
                        unique_extracted_questions = []
                        
                        for q in extracted_questions:
                            question_key = q.get('question', '')[:50]
                            if question_key not in existing_questions:
                                unique_extracted_questions.append(q)
                        
                        uploaded_questions.extend(unique_extracted_questions)
                        st.success(f"✅ Successfully extracted {len(unique_extracted_questions)} new questions from PDF using {extraction_method}")
                        if len(unique_extracted_questions) < len(extracted_questions):
                            st.info(f"📝 Skipped {len(extracted_questions) - len(unique_extracted_questions)} duplicate questions")
                        
                        # Show extraction preview
                        with st.expander("📝 Extracted Questions Preview"):
                            for i, q in enumerate(unique_extracted_questions[:3], 1):
                                st.write(f"**Question {i}:** {q['question'][:100]}...")
                            if len(unique_extracted_questions) > 3:
                                st.write(f"... and {len(unique_extracted_questions) - 3} more questions")
                    else:
                        st.warning("No questions could be extracted from the PDF file")
                        
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
            
            # Show summary for all file types if questions were loaded/extracted from files
            new_questions_from_file = []
            if uploaded_file is not None and uploaded_questions:
                # Calculate new questions added from this file upload
                extraction_count = len(st.session_state.get('generation_uploaded_questions', []))
                if len(uploaded_questions) > extraction_count:
                    new_questions_from_file = uploaded_questions[extraction_count:]
            
            if new_questions_from_file:
                # Determine data structure based on source
                if file_type == 'csv':
                    # CSV has structured data
                    with st.expander("📊 Uploaded Questions Summary"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            subjects_in_file = set(q.get('subject', 'Unknown') for q in uploaded_questions)
                            st.write("**Subjects in File:**")
                            for subject in subjects_in_file:
                                count = len([q for q in uploaded_questions if q.get('subject') == subject])
                                st.write(f"• {subject.replace('_', ' ').title()}: {count} questions")
                        
                        with col2:
                            types_in_file = set(q.get('type', 'Unknown') for q in uploaded_questions)
                            st.write("**Question Types:**")
                            for qtype in types_in_file:
                                count = len([q for q in uploaded_questions if q.get('type') == qtype])
                                st.write(f"• {qtype}: {count} questions")
                        
                        with col3:
                            difficulties_in_file = set(q.get('difficulty', 'Unknown') for q in uploaded_questions)
                            st.write("**Difficulty Levels:**")
                            for diff in difficulties_in_file:
                                count = len([q for q in uploaded_questions if q.get('difficulty') == diff])
                                st.write(f"• {diff}: {count} questions")
                else:
                    # Text/PDF has extracted data
                    with st.expander("📊 Extracted Questions Summary"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total Questions", len(uploaded_questions))
                            st.write("**File Type:** " + file_type.upper())
                        
                        with col2:
                            avg_length = sum(len(q['question']) for q in uploaded_questions) / len(uploaded_questions)
                            st.metric("Avg Question Length", f"{avg_length:.0f} chars")
                            st.write("**Source:** Extracted from text")
                
                # Option to use uploaded questions
                use_uploaded = st.checkbox(
                    "Include uploaded/extracted questions in generation",
                    value=True,
                    help="If checked, questions from the uploaded file will be mixed with newly generated ones"
                )
                
                if not use_uploaded:
                    uploaded_questions = []
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please ensure your file has the correct format and encoding.")
    
    # Overall Summary of All Uploaded Questions (Extracted + File Upload)
    if uploaded_questions:
        st.subheader("📋 All Uploaded Questions Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", len(uploaded_questions))
        
        with col2:
            extraction_count = len([q for q in uploaded_questions if 'extraction_method' in q or 'source' in q and 'Extracted from' in str(q['source'])])
            st.metric("From Extraction", extraction_count)
        
        with col3:
            file_upload_count = len(uploaded_questions) - extraction_count
            st.metric("From File Upload", file_upload_count)
        
        with col4:
            unique_subjects = set(q.get('subject', 'Unknown') for q in uploaded_questions)
            st.metric("Subjects", len(unique_subjects))
        
        # Detailed breakdown
        with st.expander("📊 Detailed Breakdown of All Questions"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📚 Subject Distribution:**")
                subject_counts = {}
                for q in uploaded_questions:
                    subject = q.get('subject', 'Unknown')
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
                
                for subject, count in sorted(subject_counts.items()):
                    percentage = (count / len(uploaded_questions)) * 100
                    st.write(f"• **{subject.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)")
            
            with col2:
                st.write("**🎯 Question Types:**")
                type_counts = {}
                for q in uploaded_questions:
                    qtype = q.get('type', 'Unknown')
                    type_counts[qtype] = type_counts.get(qtype, 0) + 1
                
                for qtype, count in sorted(type_counts.items()):
                    st.write(f"• **{qtype}:** {count} questions")
            
            with col3:
                st.write("**📈 Difficulty Levels:**")
                difficulty_counts = {}
                for q in uploaded_questions:
                    difficulty = q.get('difficulty', 'Unknown')
                    difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
                
                for difficulty, count in sorted(difficulty_counts.items()):
                    st.write(f"• **{difficulty}:** {count} questions")
        
        # Sources breakdown
        with st.expander("📁 Sources Breakdown"):
            source_counts = {}
            for q in uploaded_questions:
                source = q.get('source', 'Unknown')
                if 'Extracted from' in str(source):
                    source_type = "Extraction"
                elif 'source_file' in q:
                    source_type = f"File: {q.get('source_file', 'Unknown')}"
                else:
                    source_type = "File Upload"
                source_counts[source_type] = source_counts.get(source_type, 0) + 1
            
            for source, count in sorted(source_counts.items()):
                st.write(f"• **{source}:** {count} questions")
        
        # Option to use uploaded questions
        use_uploaded = st.checkbox(
            "✅ Include all uploaded/extracted questions in generation",
            value=True,
            help="If checked, all questions from extraction and file uploads will be mixed with newly generated ones"
        )
        
        if not use_uploaded:
            uploaded_questions = []
            st.info("📝 Uploaded questions will be excluded from generation")
        else:
            st.success(f"📋 Using {len(uploaded_questions)} uploaded questions for enhanced generation")
    
    st.divider()
    
    # Generation Parameters
    st.subheader("🎛️ Generation Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_subjects = st.multiselect(
            "Select Subjects:",
            options=list(user_topics.keys()),
            default=list(user_topics.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col2:
        questions_per_subject = st.slider(
            "New Questions per Subject:",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of new questions to generate for each subject"
        )
    
    with col3:
        offline_mode = st.checkbox("Offline Mode (Template-based only)", value=False)
    
    # Advanced Options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            filter_by_difficulty = st.selectbox(
                "Filter uploaded questions by difficulty:",
                options=['All', 'easy', 'moderate', 'hard'],
                help="Filter uploaded questions by difficulty level"
            )
        
        with col2:
            mix_ratio = st.slider(
                "Uploaded to Generated Ratio:",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="0 = Only generated, 1 = Only uploaded, 0.5 = Equal mix"
            )
    
    # Generate button
    if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
        if not selected_subjects:
            st.error("Please select at least one subject!")
            return
        
        # Filter topics for selected subjects
        filtered_topics = {subject: topics for subject, topics in user_topics.items() 
                          if subject in selected_subjects and topics}
        
        if not filtered_topics and not uploaded_questions:
            st.error("No topics found for selected subjects and no uploaded questions!")
            return
        
        # Show generation progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            all_questions = []
            
            # Process uploaded questions first
            if uploaded_questions:
                status_text.text("Processing uploaded questions...")
                
                # Filter uploaded questions by selected subjects
                filtered_uploaded = []
                for q in uploaded_questions:
                    if q.get('subject') in selected_subjects:
                        # Apply difficulty filter
                        if filter_by_difficulty == 'All' or q.get('difficulty') == filter_by_difficulty:
                            filtered_uploaded.append(q)
                
                # Calculate how many uploaded questions to include
                total_new_questions = len(selected_subjects) * questions_per_subject
                max_uploaded = int(total_new_questions * mix_ratio / (1 - mix_ratio)) if mix_ratio < 1 else len(filtered_uploaded)
                
                if filtered_uploaded:
                    # Randomly sample uploaded questions
                    import random
                    selected_uploaded = random.sample(
                        filtered_uploaded, 
                        min(max_uploaded, len(filtered_uploaded))
                    )
                    all_questions.extend(selected_uploaded)
                    st.info(f"📚 Included {len(selected_uploaded)} questions from uploaded CSV")
                
                progress_bar.progress(0.3)
            
            # Generate new questions if topics are available
            if filtered_topics:
                status_text.text("Initializing question generator...")
                generator = StreamlitMPPSCGenerator(
                    user_topics=filtered_topics,
                    offline_mode=offline_mode
                )
                
                total_subjects = len(selected_subjects)
                
                for i, subject in enumerate(selected_subjects):
                    if subject in filtered_topics:
                        status_text.text(f"Generating questions for {subject.replace('_', ' ').title()}...")
                        
                        # Generate questions
                        questions = generator.generate_subject_wise_questions(subject, questions_per_subject)
                        all_questions.extend(questions)
                        
                        # Update progress
                        progress_bar.progress(0.3 + (0.7 * (i + 1) / total_subjects))
            
            # Store in session state
            st.session_state.generated_questions = all_questions
            st.session_state.generator = generator if 'generator' in locals() else None
            
            progress_bar.progress(1.0)
            status_text.text("Questions generated successfully!")
            
            # Show final summary
            new_questions = len([q for q in all_questions if q.get('source') == 'mppsc_generator'])
            uploaded_count = len([q for q in all_questions if q.get('source') != 'mppsc_generator'])
            
            st.success(f"✅ **Generation Complete!**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", len(all_questions))
            with col2:
                st.metric("New Generated", new_questions)
            with col3:
                st.metric("From Upload", uploaded_count)
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.text(traceback.format_exc())

def render_questions_display():
    """Render the generated questions"""
    if not st.session_state.generated_questions:
        st.info("No questions generated yet. Configure topics and generate questions above.")
        return
    
    st.header("📋 Generated Questions")
    
    questions = st.session_state.generated_questions
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{len(questions)}</h3>
            <p>Total Questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        subjects_count = len(set(q.get('subject', 'Unknown') for q in questions))
        st.markdown(f"""
        <div class="stats-card">
            <h3>{subjects_count}</h3>
            <p>Subjects Covered</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        generated_count = len([q for q in questions if q.get('source') == 'mppsc_generator'])
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);">
            <h3>{generated_count}</h3>
            <p>Generated</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        uploaded_count = len([q for q in questions if q.get('source') != 'mppsc_generator'])
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);">
            <h3>{uploaded_count}</h3>
            <p>Uploaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter options
    st.subheader("🔍 Filter Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subject_filter = st.selectbox(
            "Filter by Subject:",
            options=['All'] + list(set(q.get('subject', 'Unknown') for q in questions)),
            format_func=lambda x: x.replace('_', ' ').title() if x != 'All' else x
        )
    
    with col2:
        type_filter = st.selectbox(
            "Filter by Type:",
            options=['All'] + list(set(q.get('type', 'Unknown') for q in questions))
        )
    
    with col3:
        source_filter = st.selectbox(
            "Filter by Source:",
            options=['All'] + list(set(q.get('source', 'Unknown') for q in questions)),
            format_func=lambda x: 'Generated' if x == 'mppsc_generator' else ('Uploaded' if x != 'All' else 'All')
        )
    
    # Apply filters
    filtered_questions = questions
    if subject_filter != 'All':
        filtered_questions = [q for q in filtered_questions if q.get('subject') == subject_filter]
    if type_filter != 'All':
        filtered_questions = [q for q in filtered_questions if q.get('type') == type_filter]
    if source_filter != 'All':
        if source_filter == 'Generated':
            filtered_questions = [q for q in filtered_questions if q.get('source') == 'mppsc_generator']
        else:
            filtered_questions = [q for q in filtered_questions if q.get('source') != 'mppsc_generator']
    
    # Display questions
    st.subheader(f"📝 Questions ({len(filtered_questions)} shown)")
    
    for i, question in enumerate(filtered_questions, 1):
        # Determine question source for styling
        is_uploaded = question.get('source') != 'mppsc_generator'
        source_badge = "📤 Uploaded" if is_uploaded else "⚡ Generated"
        card_style = "border-left: 4px solid #28a745;" if is_uploaded else "border-left: 4px solid #007bff;"
        
        with st.container():
            st.markdown(f"""
            <div class="question-card" style="{card_style}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: inherit;">Question {i}</h4>
                    <span style="background: {'#28a745' if is_uploaded else '#007bff'}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">
                        {source_badge}
                    </span>
                </div>
                <div style="color: inherit;">
                    <p><strong>Subject:</strong> {question.get('subject', 'Unknown').replace('_', ' ').title()}</p>
                    <p><strong>Topic:</strong> {question.get('topic', 'Unknown')}</p>
                    <p><strong>Type:</strong> {question.get('type', 'Unknown')}</p>
                    <p><strong>Difficulty:</strong> {question.get('difficulty', 'Unknown')}</p>
                    {f"<p><strong>Year:</strong> {question.get('year', 'Unknown')}</p>" if question.get('year') else ""}
                    <hr style="margin: 1rem 0; opacity: 0.3;">
                    <p><strong>Question:</strong></p>
                    <p style="margin: 0; line-height: 1.6; font-size: 1.1em; color: inherit;">{question.get('question', 'No question text available')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_persistent_extraction_results():
    """Display extraction results from session state if they exist"""
    if st.session_state.extraction_results and st.session_state.extraction_file_results:
        st.success("✅ **Previous Extraction Results Available**")
        
        with st.expander("📊 View Persistent Extraction Results", expanded=True):
            # Show source and timestamp
            st.info(f"**Source:** {st.session_state.extraction_source} | **Extracted:** {st.session_state.extraction_timestamp}")
            
            # Display summary
            total_questions = len(st.session_state.extraction_results)
            total_files = len(st.session_state.extraction_file_results)
            st.metric("Total Questions Extracted", total_questions)
            st.metric("Files Processed", total_files)
            
            # Show questions by subject
            questions_by_subject = {}
            for question_data in st.session_state.extraction_results:
                subject = question_data.get('subject', 'General')
                if subject not in questions_by_subject:
                    questions_by_subject[subject] = []
                questions_by_subject[subject].append(question_data)
            
            # Display questions
            for subject, questions in questions_by_subject.items():
                with st.expander(f"📚 {subject} ({len(questions)} questions)"):
                    for i, question_data in enumerate(questions[:10], 1):  # Show first 10
                        st.write(f"**{i}.** {question_data['question']}")
                        if 'options' in question_data and question_data['options']:
                            for opt in question_data['options']:
                                st.write(f"   {opt}")
                        st.write("---")
                    
                    if len(questions) > 10:
                        st.info(f"... and {len(questions) - 10} more questions in this subject")
            
            # File processing details
            with st.expander("📁 File Processing Details"):
                for file_info in st.session_state.extraction_file_results:
                    file_name = file_info.get('file_name', 'Unknown')
                    questions_count = file_info.get('questions_count', 0)
                    extraction_method = file_info.get('extraction_method', 'Unknown')
                    
                    st.write(f"**📄 {file_name}**")
                    st.write(f"   • Questions extracted: {questions_count}")
                    st.write(f"   • Method: {extraction_method}")
                    st.write("")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Clear results button
                if st.button("🗑️ Clear Previous Results", help="Clear stored extraction results from memory"):
                    st.session_state.extraction_results = []
                    st.session_state.extraction_file_results = []
                    st.session_state.extraction_source = ""
                    st.session_state.extraction_timestamp = ""
                    st.success("Previous results cleared!")
                    st.rerun()
            
            with col2:
                # Send to generation section button
                if st.button("📤 Send to Generation", help="Send extracted questions to the generation section as uploaded questions"):
                    if 'uploaded_questions_for_generation' not in st.session_state:
                        st.session_state.uploaded_questions_for_generation = []
                    
                    # Convert extraction results to generation format
                    formatted_questions = []
                    for i, q in enumerate(st.session_state.extraction_results, 1):
                        formatted_question = {
                            'id': i,
                            'question': q.get('question', ''),
                            'subject': q.get('subject', 'General Studies'),
                            'topic': q.get('topic', 'Mixed Topics'),
                            'type': q.get('type', 'MCQ'),
                            'difficulty': q.get('difficulty', 'Medium'),
                            'source': f"Extracted from {st.session_state.extraction_source}",
                            'year': q.get('year', datetime.now().year),
                            'extraction_method': q.get('extraction_method', 'text'),
                            'source_file': q.get('source_file', 'Unknown')
                        }
                        formatted_questions.append(formatted_question)
                    
                    # Store in session state for generation section
                    st.session_state.uploaded_questions_for_generation = formatted_questions
                    st.session_state.extraction_sent_to_generation = True
                    
                    st.success(f"✅ Sent {len(formatted_questions)} questions to Generation section!")
                    st.info("💡 Go to the 'Generate Questions' page to use these extracted questions.")
            
            with col3:
                # Download CSV button
                if st.button("💾 Download CSV", help="Download extracted questions as CSV file"):
                    # Convert to DataFrame for CSV export
                    df_data = []
                    for i, q in enumerate(st.session_state.extraction_results, 1):
                        df_data.append({
                            'id': i,
                            'question': q.get('question', ''),
                            'subject': q.get('subject', 'General Studies'),
                            'topic': q.get('topic', 'Mixed Topics'),
                            'type': q.get('type', 'MCQ'),
                            'difficulty': q.get('difficulty', 'Medium'),
                            'source': f"Extracted from {st.session_state.extraction_source}",
                            'year': q.get('year', datetime.now().year),
                            'extraction_method': q.get('extraction_method', 'text'),
                            'source_file': q.get('source_file', 'Unknown')
                        })
                    
                    df = pd.DataFrame(df_data)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download as CSV",
                        data=csv_data,
                        file_name=f"extracted_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

def render_extraction_section():
    """Render the question extraction section with smart extraction (direct + OCR)"""
    st.header("📄 Extract Questions from Files")
    st.write("Upload multiple PDF or text files to automatically extract questions using smart extraction.")
    st.info("🧠 **Smart Extraction Mode**: PDFs are first processed with direct text extraction, then OCR is used as fallback for scanned documents.")
    
    # Display persistent results if available
    display_persistent_extraction_results()
    
    # Tabs for different upload methods (removed MPPSC OCR tab as it's now integrated)
    tab1, tab2 = st.tabs(["📁 Multiple Files", "🗂️ Folder Path"])
    
    with tab1:
        st.subheader("Upload Multiple Files")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_files = st.file_uploader(
                "Choose files to extract questions from",
                type=['pdf', 'txt'],
                accept_multiple_files=True,
                help="Upload multiple PDF or text files. PDFs will be processed with smart extraction (direct text + OCR fallback)."
            )
        with col2:
            max_pages_upload = st.slider(
                "Max pages per PDF:",
                min_value=1,
                max_value=50,
                value=10,
                help="Limit pages for OCR processing",
                key="max_pages_upload"
            )
        
        if uploaded_files:
            process_multiple_files(uploaded_files, max_pages_upload)
    
    with tab2:
        st.subheader("Process Folder")
        st.info("Enter the path to a folder containing PDF or text files to process all files at once using smart extraction.")
        
        # Create columns for folder path input and browse button
        col_path, col_browse = st.columns([4, 1])
        
        with col_path:
            # Initialize session state for folder path if not exists
            if 'selected_folder_path' not in st.session_state:
                st.session_state.selected_folder_path = ""
            
            folder_path = st.text_input(
                "Folder Path:",
                value=st.session_state.selected_folder_path,
                placeholder=r"C:\path\to\your\folder or MPPSC papers",
                help="Enter the full path to a folder containing PDF or text files. Smart extraction will be used for all PDFs."
            )
            
            # Update session state when text input changes
            if folder_path != st.session_state.selected_folder_path:
                st.session_state.selected_folder_path = folder_path
        
        with col_browse:
            st.write("")  # Add some vertical spacing
            if st.button("📂 Browse", help="Open folder selection dialog", use_container_width=True):
                if TKINTER_AVAILABLE:
                    with st.spinner("Opening folder browser..."):
                        selected_path = select_folder_path()
                        if selected_path:
                            st.session_state.selected_folder_path = selected_path
                            folder_path = selected_path
                            st.success(f"✅ Selected: {os.path.basename(selected_path)}")
                            st.rerun()  # Refresh to show the selected path
                        else:
                            st.info("No folder selected")
                else:
                    st.warning("⚠️ Folder browser requires tkinter. Please enter path manually.")
        
        # Use the current folder path value (either from text input or browse)
        current_folder_path = st.session_state.selected_folder_path
        
        col1, col2 = st.columns(2)
        with col1:
            max_pages = st.slider(
                "Max pages per PDF (for OCR fallback):",
                min_value=1,
                max_value=50,
                value=10,
                help="Limit pages processed during OCR fallback"
            )
        with col2:
            st.write("**Smart Extraction Features:**")
            st.write("✅ Direct text extraction first")
            st.write("✅ OCR fallback for scanned docs")
            st.write("✅ English text filtering")
            st.write("✅ Advanced pattern recognition")
        
        # Show selected folder path if one is chosen
        if current_folder_path:
            st.success(f"📁 Selected folder: `{current_folder_path}`")
            
            # Check if folder exists and show file count
            if os.path.exists(current_folder_path):
                supported_extensions = ['.pdf', '.txt']
                file_count = 0
                for root, dirs, files in os.walk(current_folder_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in supported_extensions):
                            file_count += 1
                
                if file_count > 0:
                    st.info(f"📊 Found {file_count} supported files (PDF/TXT) in the selected folder")
                else:
                    st.warning("⚠️ No PDF or TXT files found in the selected folder")
            else:
                st.error("❌ The selected folder path does not exist")
        
        if current_folder_path and st.button("📂 Process Folder with Smart Extraction", use_container_width=True, type="primary"):
            process_folder_files(current_folder_path, max_pages)
    
    # Instructions when no files are uploaded
    if 'uploaded_files' not in locals() or not uploaded_files:
        st.info("📁 Please upload files or specify a folder path to begin smart extraction.")
        
        with st.expander("ℹ️ How Smart Question Extraction Works"):
            st.markdown("""
            **Smart Extraction Process:**
            - **Step 1**: Direct text extraction using pypdfium2 for text-based PDFs
            - **Step 2**: OCR fallback using EasyOCR for scanned/image-based PDFs
            - **Step 3**: English text filtering to remove non-English content
            - **Step 4**: Advanced pattern recognition for question detection
            
            **Supported File Types:**
            - **PDF files**: Smart extraction (direct text → OCR fallback)
            - **Text files**: Direct text analysis for plain text files
            
            **Question Detection Patterns:**
            - Numbered questions: `1. What is...?`
            - Q-format: `Q1. Which of the following...?`
            - Direct questions: `What is the capital of...?`
            - MCQ patterns: Questions followed by options (A), (B), etc.
            
            **Smart Processing Features:**
            - **Automatic Method Selection**: Direct text first, OCR if needed
            - **Performance Optimization**: Page limits for OCR processing
            - **Quality Assurance**: Confidence filtering for OCR results
            - **Language Detection**: English content focus with multilingual filtering
            
            **Automatic Classification:**
            - Questions automatically categorized by subject
            - Topics inferred from question content
            - Difficulty levels assigned based on complexity
            - Source file tracking with extraction method
            
            **Quality Assurance:**
            - Minimum 20 characters per question
            - Maximum 500 characters per question
            - Duplicate detection across all files
            - Invalid pattern filtering
            - English language validation
            
            **Perfect for Mixed Document Types:**
            - Handles both text-based and scanned PDFs
            - Optimized for government exam papers
            - Filters Hindi/multilingual content automatically
            - Efficient processing with smart fallback
            """)


def extract_mppsc_papers_with_ocr(mppsc_folder: str, max_pages: int = 10):
    """DEPRECATED: This function is replaced by the integrated smart extraction"""
    st.warning("This function is deprecated. Please use the folder processing option above which now includes smart extraction (direct text + OCR) by default.")
    return
    """Extract questions from MPPSC papers using advanced OCR"""
    if not os.path.exists(mppsc_folder):
        st.error(f"MPPSC papers folder '{mppsc_folder}' not found!")
        return
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(mppsc_folder) if f.endswith('.pdf')]
    pdf_files.sort()
    
    if not pdf_files:
        st.warning(f"No PDF files found in: {mppsc_folder}")
        return
    
    st.info(f"Found {len(pdf_files)} MPPSC PDF files to process with OCR...")
    
    # Initialize extractor
    extractor = AdvancedQuestionExtractor()
    
    all_extracted_questions = []
    file_results = []
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf_file in enumerate(pdf_files):
        pdf_path = os.path.join(mppsc_folder, pdf_file)
        status_text.text(f"Processing {pdf_file} with OCR...")
        
        try:
            # Try direct text extraction first
            text = extractor.extract_text_direct(pdf_path, pdf_file)
            extraction_method = "direct_text"
            
            # If direct extraction doesn't yield much, try OCR
            if len(text.strip()) < 100:
                status_text.text(f"Using OCR for {pdf_file}...")
                # For OCR, we'll modify the existing function to limit pages
                text = extractor.extract_text_with_ocr(pdf_path, pdf_file, max_pages)
                extraction_method = "ocr"
            
            # Extract questions from text
            extracted_questions = extractor.extract_questions_from_text_advanced(text, pdf_file)
            
            # Add metadata
            for q in extracted_questions:
                q['extraction_method'] = extraction_method
                # Extract year and paper number from filename
                year_match = re.search(r'(\d{4})', pdf_file)
                paper_match = re.search(r'_(\d+)\.pdf', pdf_file)
                if year_match:
                    q['year'] = year_match.group(1)
                if paper_match:
                    q['paper_number'] = paper_match.group(1)
            
            if extracted_questions:
                all_extracted_questions.extend(extracted_questions)
                file_results.append({
                    'file_name': pdf_file,
                    'questions_count': len(extracted_questions),
                    'file_type': 'PDF',
                    'extraction_method': extraction_method
                })
                st.success(f"✅ {pdf_file}: {len(extracted_questions)} questions using {extraction_method}")
            else:
                file_results.append({
                    'file_name': pdf_file,
                    'questions_count': 0,
                    'file_type': 'PDF',
                    'extraction_method': extraction_method
                })
                st.warning(f"⚠️ {pdf_file}: No questions extracted")
                
        except Exception as e:
            st.error(f"Error processing {pdf_file}: {str(e)}")
            file_results.append({
                'file_name': pdf_file,
                'questions_count': 0,
                'file_type': 'PDF',
                'extraction_method': 'error'
            })
        
        # Update progress
        progress_bar.progress((i + 1) / len(pdf_files))
    
    progress_bar.progress(1.0)
    status_text.text("MPPSC extraction completed!")
    
    # Display results
    if all_extracted_questions:
        display_extraction_results(all_extracted_questions, file_results, f"MPPSC Papers: {mppsc_folder}")
    else:
        st.warning("No questions were extracted from any MPPSC papers.")
        
        # Show processing summary
        if file_results:
            st.subheader("📊 Processing Summary")
            df_results = pd.DataFrame(file_results)
            st.dataframe(df_results, use_container_width=True)


def render_download_section():
    """Render the download section"""
    if not st.session_state.generated_questions:
        st.info("No questions generated yet. Generate questions first to enable downloads.")
        return
    
    st.header("💾 Download Questions")
    
    questions = st.session_state.generated_questions
    
    # Download statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Questions", len(questions))
    with col2:
        generated_count = len([q for q in questions if q.get('source') == 'mppsc_generator'])
        st.metric("Generated Questions", generated_count)
    with col3:
        uploaded_count = len([q for q in questions if q.get('source') != 'mppsc_generator'])
        st.metric("Uploaded Questions", uploaded_count)
    
    st.divider()
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Download as CSV")
        st.write("Export all questions as a CSV file for data analysis or import into other systems.")
        
        # Create CSV data
        df = pd.DataFrame(questions)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📊 Download CSV File",
            data=csv_data,
            file_name=f"mppsc_questions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download questions in CSV format"
        )
        
        # Show preview of CSV structure
        with st.expander("Preview CSV Structure"):
            st.dataframe(df.head(3), use_container_width=True)
    
    with col2:
        st.subheader("📄 Download Sample Paper")
        st.write("Generate a formatted question paper ready for printing or distribution.")
        
        # Generate sample paper
        if st.session_state.generator:
            sample_paper = st.session_state.generator.create_sample_question_paper(questions)
        else:
            # Fallback if no generator available
            from datetime import datetime
            sample_paper = f"""
MPPSC SAMPLE QUESTION PAPER
Generated on: {datetime.now().strftime('%B %d, %Y')}

Total Questions: {len(questions)}

""" + "\n".join([f"{i+1}. {q.get('question', 'N/A')}" for i, q in enumerate(questions)])
        
        st.download_button(
            label="📄 Download Sample Paper",
            data=sample_paper,
            file_name=f"mppsc_sample_paper_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download formatted question paper"
        )
        
        # Show preview of paper format
        with st.expander("Preview Paper Format"):
            preview_lines = sample_paper.split('\n')[:15]
            st.text('\n'.join(preview_lines) + '\n...')

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to:",
            ["Configure Topics", "Generate Questions", "Extract Questions", "View Questions", "Download"]
        )
    
    # Main content based on page selection
    if page == "Configure Topics":
        user_topics = render_topic_input_section()
        st.session_state.user_topics = user_topics
        
        # Show summary
        if user_topics:
            st.subheader("📊 Topics Summary")
            for subject, topics in user_topics.items():
                if topics:
                    subject_name = subject.replace('_', ' ').title()
                    st.markdown(f"""
                    <div class="subject-box">
                        <strong>{subject_name}:</strong> {len(topics)} topics configured
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show first few topics as preview
                    with st.expander(f"Preview topics for {subject_name}"):
                        preview_topics = topics[:10]  # Show first 10 topics
                        for topic in preview_topics:
                            st.write(f"• {topic}")
                        if len(topics) > 10:
                            st.write(f"... and {len(topics) - 10} more topics")
            
            # Overall summary
            total_topics = sum(len(topics) for topics in user_topics.values() if topics)
            active_subjects = len([s for s, topics in user_topics.items() if topics])
            
            st.info(f"📈 **Overall Summary:** {active_subjects} subjects configured with {total_topics} total topics")
    
    elif page == "Generate Questions":
        if not st.session_state.user_topics:
            st.warning("Please configure topics first!")
        else:
            render_generation_section(st.session_state.user_topics)
    
    elif page == "Extract Questions":
        render_extraction_section()
    
    elif page == "View Questions":
        render_questions_display()
    
    elif page == "Download":
        render_download_section()
    
    # Footer
    st.markdown("---")
    st.markdown("**MPPSC Question Generator** | Built with Streamlit | © 2025")

if __name__ == "__main__":
    main()
