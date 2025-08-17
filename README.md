# MPPSC Services Platform - Comprehensive Guide

A unified platform for UPSC/MPPSC examination services featuring AI-powered answer sheet grading, professional question paper generation, and advanced grammar checking with IBM Watsonx AI integration.

## 🎯 Overview

This platform provides three integrated services for UPSC/MPPSC examination management:

1. **🎓 Answer Sheet Grading (Assessly)**: AI-powered automatic grading of handwritten answer sheets
2. **📄 Question Paper Generation**: Professional PDF question paper creation with customizable topics  
3. **✍️ Grammar Checker**: Advanced IBM Watsonx AI-powered grammar analysis and correction

## ✨ Key Features

### 🎓 Answer Sheet Grading (Assessly)

**Automated Grading System**
- Upload answer keys and handwritten answer sheets (PDF format)
- AI-powered handwriting recognition and text extraction using OCR
- Semantic similarity analysis between student answers and answer keys
- Configurable difficulty levels (Easy, Medium, Hard, Custom)
- Detailed scoring with customizable mark allocation thresholds
- Progress tracking and real-time status updates
- Comprehensive grading reports with detailed analysis

**Supported Formats**
- PDF answer sheets and answer keys
- Multiple answer sheets can be processed simultaneously
- High-accuracy handwritten text recognition
- Image preprocessing for better OCR results

**Grading Configuration**
- **Easy Mode**: Full marks (80%), High marks (70%), Mid marks (60%), Low marks (50%)
- **Medium Mode**: Full marks (75%), High marks (65%), Mid marks (55%), Low marks (45%)
- **Hard Mode**: Full marks (70%), High marks (60%), Mid marks (50%), Low marks (40%)
- **Custom Mode**: Set your own thresholds for each marking category

### 📄 Question Paper Generator

**Professional PDF Generation**
- Create MPPSC-style question papers with professional formatting
- A4 format with proper margins and typography using ReportLab
- Multiple subject support with organized sections
- Customizable topics and question selection
- Print-ready format with proper page breaks and headers

**Subject Coverage**
- **Madhya Pradesh GK**: History, Geography, Culture, Administration
- **Indian Polity**: Constitution, Parliament, Judiciary, Governance
- **Indian Economy**: Planning, Budget, Trade, Economic Development
- **Indian History**: Ancient, Medieval, Modern, Freedom Struggle
- **Indian Geography**: Physical, Economic, Environmental
- **General Science**: Physics, Chemistry, Biology, Technology
- **Current Affairs**: National and International developments

**Question Management**
- Extract questions from existing PDF files using AI
- Comprehensive question bank with 1000+ curated questions
- Topic-wise question organization and categorization
- Multiple choice and descriptive question support
- Smart question selection algorithms

**Output Features**
- Professional PDF generation with ReportLab
- Downloadable question papers in multiple formats
- Print-ready format with exam instructions
- Customizable paper layouts and formatting

### ✍️ Grammar Checker (Enhanced with IBM AI)

**IBM Watsonx AI Integration**
- **Primary**: IBM Watsonx AI with meta-llama/llama-2-13b-chat model
- **Fallback**: LanguageTool API for reliability
- Context-aware grammar and spelling correction
- Professional-level text improvement for UPSC/MPPSC writing
- Intelligent sentence restructuring and flow enhancement

**Advanced Grammar Analysis**
- Subject-verb agreement corrections
- Proper tense consistency throughout text
- Article usage improvements
- Better word choice suggestions
- Complete sentence restructuring for clarity
- Punctuation and formatting corrections

**Example Transformation**
```
Before: "Last week I is going to my friend house for doing some project, 
         but when I reach there he not at home and the books was very costlier."

After:  "Last week I went to my friend's house to work on a project, 
         but when I arrived, he was not home and the books were more expensive."
```

**Input Methods**
- Direct text input with real-time analysis
- File upload support (.txt, .csv files)
- Image OCR processing for handwritten text
- Batch processing for multiple documents

**Scoring System**
- **95-100 points**: Excellent - Perfect or near-perfect grammar
- **80-94 points**: Good - Minor errors, well-written
- **60-79 points**: Fair - Some errors, needs improvement
- **0-59 points**: Poor - Many errors, significant revision needed

**Advanced Features**
- BLIP2 model for image-to-text conversion
- Handwritten text recognition with preprocessing
- Batch processing for multiple answers
- Excel output with detailed analysis
- Error highlighting and correction suggestions
- Grammar issue consolidation in full-width display

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for AI services
- 1-2GB RAM for optimal performance
- 500MB storage for models and temporary files

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd UPSC_grading
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup IBM Credentials (Recommended for Best Grammar Results)**
   
   **Option A: Create .env file (Recommended)**
   ```bash
   # Create .env file in project root
   echo "WATSONX_API_KEY=your_api_key_here" > .env
   echo "WATSONX_URL=your_watson_url_here" >> .env
   echo "WATSONX_PROJECT_ID=your_project_id_here" >> .env
   ```

   **Option B: Environment Variables**
   ```bash
   export WATSONX_API_KEY="your_api_key_here"
   export WATSONX_URL="your_watson_url_here"
   export WATSONX_PROJECT_ID="your_project_id_here"
   ```

4. **Verify Installation**
   ```bash
   python validate_setup.py
   ```

5. **Run the Application**
   ```bash
   streamlit run mainpage.py
   ```

### Getting IBM Credentials

1. **IBM Cloud Account**: Sign up at https://cloud.ibm.com/

2. **Create a Watsonx AI Instance**:
   - Go to IBM Cloud Console
   - Search for "watsonx.ai"
   - Create a new service instance

3. **Get API Key**:
   - Go to IBM Cloud → Manage → Access (IAM)
   - Create a new API key
   - Copy the API key value

4. **Get Project ID**:
   - In your Watsonx.ai instance
   - Create or select a project
   - Copy the Project ID from project settings

### Key Dependencies

```python
# Core Web Framework
streamlit>=1.28.0
python-dotenv>=1.0.0

# Data Handling and Analysis
pandas>=2.1.0
numpy>=1.26.0
pyarrow>=16.0.0

# IBM AI Services
ibm-watson>=6.0.0
ibm-watsonx-ai>=1.3.0
ibm-generative-ai>=3.0.0

# Document Processing
pypdf>=3.0.0
reportlab>=4.0.0
pypdfium2>=4.0.0

# OCR and Image Processing
easyocr>=1.7.0
pillow>=10.0.0
pytesseract>=0.3.10

# ML and NLP
transformers>=4.30.0
torch>=2.0.0
sentence-transformers>=4.0.0

# Grammar Checking
language-tool-python>=2.9.0
requests>=2.32.0
```

## 📖 Usage Guide

### Getting Started

1. **Launch the Application**
   ```bash
   streamlit run mainpage.py
   ```

2. **Access the Web Interface**
   - Open your browser to `http://localhost:8501`
   - Select your preferred service from the sidebar navigation

### 🎓 Answer Sheet Grading

1. **Upload Files**
   - Upload answer key PDF in the designated section
   - Upload one or more answer sheet PDFs for grading

2. **Configure Grading Parameters**
   - Select difficulty level (Easy/Medium/Hard/Custom)
   - Set total marks per question (typically 4-20 marks)
   - Adjust thresholds if using custom mode

3. **Start Grading Process**
   - Click "Start Grading Process"
   - Monitor real-time progress updates
   - View comprehensive results and download reports

### 📄 Question Paper Generation

1. **Configure Topics**
   - Navigate to "Configure Topics" tab
   - Select subjects from available options
   - Choose specific topics within each subject
   - Use default curriculum or add custom topics

2. **Extract Questions (Optional)**
   - Upload PDF files containing existing questions
   - AI automatically extracts and categorizes questions
   - Review and validate extracted questions

3. **Generate Question Paper**
   - Set number of questions and difficulty level
   - Select question types (Short Answer, Long Answer)
   - Click "Generate Questions" to create question set
   - Generate professional PDF for printing

### ✍️ Grammar Checking

1. **Text Input Method**
   - Type or paste text directly into the interface
   - Click "Check Grammar" for comprehensive analysis
   - View consolidated grammar issues in full-width display

2. **Quick Correction**
   - Use "Quick Correct" for immediate text improvement
   - Copy corrected text from the provided code box

3. **File Upload Method**
   - Upload .txt files for batch analysis
   - Process single or multiple files simultaneously
   - Download corrected versions

4. **CSV Batch Processing**
   - Upload CSV files with multiple text entries
   - Process all entries with detailed analysis
   - Download results in Excel format with scoring

## 🏗️ Technical Architecture

### Project Structure

```
UPSC_grading/
├── mainpage.py                     # Main Streamlit application
├── requirements.txt                # Comprehensive dependencies
├── README.md                       # This comprehensive documentation
├── .env                           # IBM credentials (user-created)
├── setup_complete.py              # Setup validation script
├── 
├── finalflow/                      # Answer sheet grading system
│   ├── flow/                       # Core grading algorithms
│   ├── input_folder/              # Upload processing
│   └── results/                   # Generated reports
├── 
├── SSDigimark-master/              # Grammar checking modules
│   ├── checker.py                  # Main text processing engine
│   ├── grammar_checker.py          # IBM AI + LanguageTool integration
│   ├── scorer.py                   # Advanced scoring algorithms
│   ├── highlighter.py              # Error highlighting system
│   ├── csv_mode.py                 # Batch processing utilities
│   └── utils/                      # OCR and image utilities
├── 
├── SSDigimark-Question-generator/  # Question paper generation
│   ├── create_mppsc_pdf_reportlab.py # Professional PDF generation
│   ├── extract_mpsc_questions.py    # AI question extraction
│   ├── generate_mppsc_questions.py  # Question generation engine
│   ├── mppsc_comprehensive_question_bank.csv # Question database
│   └── MPPSC papers/               # Reference materials
├── 
└── data_processing/                # Additional utilities
    ├── __init__.py
    ├── data_access/               # Data handling modules
    ├── transform/                 # Text transformation
    └── utils/                     # Common utilities
```

### Answer Sheet Grading Pipeline

1. **PDF Processing**: Extract text and images from uploaded PDFs using pypdfium2
2. **OCR Recognition**: Convert handwritten text to digital format using EasyOCR
3. **Text Preprocessing**: Clean and normalize extracted text
4. **Semantic Analysis**: Compare answers with answer keys using sentence transformers
5. **Similarity Computation**: Calculate semantic similarity scores
6. **Score Calculation**: Apply configurable thresholds and generate marks
7. **Report Generation**: Create comprehensive grading reports with detailed analysis

### Question Paper Generation Pipeline

1. **Content Management**: Organize questions by subject, topic, and difficulty
2. **AI Extraction**: Extract questions from PDF files using pattern matching
3. **Question Validation**: Filter and validate extracted questions
4. **Layout Generation**: Professional formatting with ReportLab
5. **PDF Creation**: Generate print-ready question papers with proper styling

### Grammar Checking System (Enhanced)

1. **Input Processing**: Handle text, files, and images with preprocessing
2. **IBM AI Integration**: Primary correction using Watsonx AI with Llama model
3. **Fallback System**: LanguageTool API as secondary option
4. **Error Analysis**: Comprehensive grammar, spelling, and style detection
5. **Intelligent Correction**: Context-aware improvements and restructuring
6. **Scoring Algorithm**: Advanced scoring based on error types and frequency
7. **Result Presentation**: Full-width consolidated display with detailed feedback

## ⚡ Performance & Optimization

### Response Times
- **Grammar Analysis**: Under 3 seconds with IBM AI (1-2 seconds with LanguageTool fallback)
- **Question Generation**: 5-10 seconds for complete papers
- **Answer Sheet Grading**: 1-3 minutes per sheet (depending on content length)
- **OCR Processing**: 5-15 seconds for image analysis and text extraction

### Resource Requirements
- **Memory**: 1-2GB RAM for optimal performance (models load on demand)
- **Storage**: 500MB for models and temporary files
- **Network**: Required for IBM AI services and LanguageTool API
- **CPU**: Moderate usage during processing (GPU optional for faster inference)

## 🛠️ Troubleshooting

### Common Issues & Solutions

**"Module not found" errors**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Verify virtual environment
which python
```

**IBM Grammar Checker Issues**
```bash
# Check .env file exists and has correct format
cat .env

# Test IBM connection
python test_ibm_grammar.py

# Verify credentials in IBM Cloud Console
```

**Slow Processing**
- Check internet connection stability
- Reduce image resolution for faster OCR
- Process smaller batches to avoid timeouts
- Ensure sufficient RAM availability

**PDF Generation Fails**
```bash
# Install additional dependencies
pip install reportlab fpdf2

# Check file permissions
ls -la output_directory/

# Verify disk space
df -h
```

**Grammar Checker Fallback to LanguageTool**
- This is normal behavior when IBM API is unavailable
- Check IBM service status and rate limits
- Verify API key validity and project access

### Debug Mode

Enable detailed logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validation Script

Run the comprehensive validation:
```bash
python validate_setup.py
```

## 📋 Best Practices

### For Users

1. **File Quality**: Use high-resolution, clear images for better OCR accuracy
2. **Text Structure**: Provide well-formatted text for optimal grammar checking
3. **Batch Processing**: Use reasonable batch sizes to avoid timeouts
4. **Result Verification**: Always review automated results before final submission
5. **Backup Data**: Keep original files as backup before processing

### For Developers

1. **Error Handling**: Implement comprehensive exception handling
2. **Resource Management**: Clean up temporary files and memory usage
3. **User Feedback**: Provide clear progress indicators and status updates
4. **Testing**: Test with various input types and edge cases
5. **Documentation**: Maintain clear code documentation and comments

## 🤝 Contributing

### Development Setup

1. Fork the repository from GitHub
2. Create a Python virtual environment
3. Install development dependencies: `pip install -r requirements.txt`
4. Make changes and test thoroughly with validation script
5. Submit pull requests with clear descriptions and test results

### Code Standards

- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings for all functions
- Include error handling for all user-facing functions
- Write unit tests for new features and modifications
- Maintain backward compatibility when possible

## 📄 License & Credits

### Third-Party Services & Libraries
- **IBM Watsonx AI**: Advanced AI-powered grammar correction
- **LanguageTool**: Open-source grammar checking API
- **ReportLab**: Professional PDF generation library
- **Streamlit**: Modern web application framework
- **EasyOCR**: Optical character recognition library
- **Transformers/Hugging Face**: NLP model ecosystem

### Original Components
- **SSDigimark**: Custom grammar checking implementation
- **Assessly**: Answer sheet grading system
- **Question Generator**: MPPSC-specific question paper creation

## 🆘 Support & Documentation

### Getting Help

1. **Check Documentation**: Review this comprehensive guide
2. **Run Validation**: Use `python validate_setup.py` for system checks
3. **Check Logs**: Review application logs for specific error messages
4. **IBM Setup**: Follow IBM_SETUP_GUIDE.md for AI integration
5. **GitHub Issues**: Create issues with detailed error reports and reproduction steps

### Additional Resources

- **IBM Watsonx AI Documentation**: https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html
- **LanguageTool API**: https://languagetool.org/http-api/
- **Streamlit Documentation**: https://docs.streamlit.io/

## 🔮 Future Enhancements

### Planned Features

1. **Multi-language Support**: Regional language processing for vernacular answers
2. **Advanced Analytics**: Detailed performance insights and learning analytics
3. **Collaboration Tools**: Multi-user review, commenting, and feedback systems
4. **Mobile Interface**: Responsive design optimized for mobile devices
5. **Offline Mode**: Local processing capabilities without internet dependency

### Technical Improvements

1. **Performance**: GPU acceleration and faster processing algorithms
2. **Accuracy**: Enhanced OCR and improved text recognition models
3. **Scalability**: Better handling of large batches and concurrent users
4. **Security**: Enhanced data protection and privacy measures
5. **Integration**: Connect with external LMS and examination management systems

### AI Enhancements

1. **Custom Models**: Train domain-specific models for UPSC/MPPSC content
2. **Adaptive Learning**: System learns from user corrections and preferences
3. **Contextual Understanding**: Better subject-specific grammar and terminology
4. **Multi-modal Processing**: Combined text, image, and audio analysis

---

## 🎉 Recent Updates & Improvements

### Version 2.0 - IBM AI Integration
- ✅ **Removed all emojis** from interface for professional appearance
- ✅ **Eliminated sample text inputs** - users provide their own content
- ✅ **IBM Watsonx AI integration** with meta-llama/llama-2-13b-chat model
- ✅ **Enhanced grammar correction** with context-aware improvements
- ✅ **Full-width UI layout** for better space utilization
- ✅ **Consolidated issues display** in single comprehensive text area
- ✅ **Professional-grade output** suitable for UPSC/MPPSC writing standards

### Grammar Quality Improvement Examples
```
Input:  "Last week I is going to my friend house for doing some project"
Output: "Last week I went to my friend's house to work on a project"

Input:  "The books was very costlier than expected"  
Output: "The books were more expensive than expected"
```

---

This comprehensive platform combines cutting-edge AI technology with user-friendly interfaces to provide a complete solution for UPSC/MPPSC examination management, content generation, and assessment automation.