# MPPSC Question Generator - AI-Powered Question Bank System

A comprehensive web-based application for generating customized MPPSC (Madhya Pradesh Public Service Commission) practice questions using advanced AI models and PDF extraction capabilities.

## 🚀 Features

- **AI-Powered Generation**: Uses Hugging Face transformers for intelligent question creation
- **PDF Question Extraction**: Extract and analyze questions from existing MPPSC papers
- **Custom Topic Input**: Add your own topics for each subject
- **Multiple Subjects**: Support for 7 key MPPSC subjects
- **Question Types**: Various question formats (MCQ, analytical, application-based)
- **Real-time Generation**: Generate questions instantly with progress tracking
- **Download Options**: Export as CSV or formatted question paper
- **Offline Mode**: Works without internet (template-based questions)
- **PDF Processing**: Advanced OCR and text extraction capabilities
- **Interactive Web Interface**: Modern, responsive Streamlit-based UI

## 📚 Subjects Covered

1. **Madhya Pradesh General Knowledge** - State-specific topics, history, geography, culture
2. **Indian Polity** - Constitutional framework, governance, political institutions
3. **Indian Economy** - Economic policies, development, financial systems
4. **Indian History** - Ancient, medieval, and modern Indian history
5. **Indian Geography** - Physical, human, and economic geography
6. **General Science** - Physics, chemistry, biology, technology
7. **Current Affairs** - Recent developments, news, and events

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (recommended for AI models)
- Internet connection (for initial model download)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Quick Start

#### Option 1: Using the launcher script (Recommended)
```bash
python run_mppsc_app.py
```

#### Option 2: Direct Streamlit command
```bash
streamlit run mppsc_streamlit_app.py
```

#### Option 3: Complete system pipeline
```bash
# Extract questions from PDFs
python run_system.py extract

# Generate new questions
python run_system.py generate

# Run complete pipeline
python run_system.py all
```

The web application will open in your default browser at `http://localhost:8501`

## 📖 How to Use

### 1. Configure Topics
- Navigate to the "Configure Topics" section
- For each subject, choose between:
  - **Default Topics**: Pre-loaded comprehensive topic list covering entire MPPSC syllabus
  - **Custom Topics**: Enter your own topics (one per line) for focused preparation
- View topic summaries and coverage for each subject

### 2. PDF Question Extraction (Optional)
- Upload existing MPPSC papers in PDF format
- Use the built-in OCR system to extract questions automatically
- Review and validate extracted questions before adding to question bank

### 3. Generate Questions
- Select subjects for question generation (multiple selection supported)
- Set the number of questions per subject (1-20 per batch)
- Choose generation mode:
  - **Online Mode**: AI-enhanced generation using Hugging Face models
  - **Offline Mode**: Template-based generation (faster, no internet required)
- Monitor real-time generation progress
- Click "Generate Questions" to start

### 4. Review & Filter Questions
- Browse generated questions with advanced filtering options
- Filter by:
  - Subject category
  - Question type (MCQ, analytical, application-based)
  - Difficulty level
  - Topic coverage
- View detailed question metadata including source, type, and difficulty rating

### 5. Export & Download
- **CSV Export**: Download all questions in structured spreadsheet format
- **Sample Paper**: Download professionally formatted question paper
- **PDF Report**: Generate comprehensive analysis report (using reportlab)
- Save custom question banks for future use

## 🏗️ Application Architecture

```
📁 Project Structure
├── 🌐 Web Interface
│   ├── mppsc_streamlit_app.py      # Main Streamlit web application
│   └── run_mppsc_app.py           # Web app launcher script
│
├── 🤖 AI Generation Engine
│   ├── generate_mppsc_questions.py # Core AI question generation
│   └── professional_question_generator.py # Advanced question templates
│
├── 📄 PDF Processing
│   ├── extract_questions_fitz.py   # PDF text extraction (PyMuPDF)
│   ├── extract_mpsc_questions.py   # MPSC-specific extraction
│   └── create_mppsc_pdf_reportlab.py # PDF report generation
│
├── 🗃️ Data Management
│   ├── mppsc_comprehensive_question_bank.csv # Master question database
│   ├── mpsc_questions_extracted.csv # Extracted questions from PDFs
│   └── mppsc_sample_question_paper.txt # Sample output format
│
├── 📂 Question Papers Archive
│   ├── MPPSC papers/              # Recent MPPSC papers (2021-2024)
│   ├── Papers/                    # Historical papers (2015-2025)
│   └── MPPSC_Question_Bank_and_Sample_Paper.pdf # Reference material
│
├── ⚙️ Configuration & Scripts
│   ├── requirements.txt           # Python dependencies
│   ├── run_system.py             # Complete system pipeline runner
│   ├── README_Streamlit.md       # This documentation
│   └── .env                      # Environment configuration
│
└── 🧠 AI Models Cache
    └── D:/huggingface_cache/      # Local model storage (configured)
```

## 🎯 Question Types & Templates

### AI-Generated Questions
- **Factual MCQ**: Multiple choice with detailed explanations
- **Madhya Pradesh Specific**: State-focused questions with local context
- **Analytical**: Critical thinking and reasoning questions
- **Application-Based**: Practical scenario and case study questions
- **Current Affairs**: Recent developments and trending topics

### Template-Based Questions (Offline Mode)
- **Pattern Recognition**: Questions following MPPSC exam patterns
- **Topic-Specific**: Targeted questions for specific syllabus areas
- **Difficulty Graded**: Questions ranging from basic to advanced levels
- **Format Standardized**: Consistent with official MPPSC format

## ⚙️ Advanced Configuration

### Environment Setup
The application supports custom environment configuration through `.env` file:
```bash
# Hugging Face model cache location
HF_HOME=D:/huggingface_cache
HF_HUB_CACHE=D:/huggingface_cache/hub
HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Model configuration
DEFAULT_MODEL=google/flan-t5-small
OFFLINE_MODE=false
```

### Custom Topics Configuration
1. **Web Interface Method**:
   - Go to "Configure Topics" in the web app
   - Uncheck "Use default topics" for any subject
   - Enter your custom topics in the text area (one per line)
   - Topics are automatically saved in session state

2. **Programmatic Method**:
   ```python
   custom_topics = {
       'madhya_pradesh_gk': [
           'Gwalior Fort History',
           'Bhimbetka Rock Shelters',
           'Madhya Pradesh Tribal Culture'
       ],
       'indian_polity': [
           'Panchayati Raj System',
           'Constitutional Amendments',
           'Electoral Reforms'
       ]
   }
   ```

### AI Model Customization
- **Default Model**: `google/flan-t5-small` (lightweight, fast)
- **Alternative Models**: Can be configured for better performance
  - `google/flan-t5-base` (better quality, more resources)
  - `google/flan-t5-large` (best quality, high resource usage)
- **Offline Templates**: Extensive template library for internet-free operation

### PDF Processing Options
- **OCR Engine**: EasyOCR for multilingual text recognition
- **PDF Library**: PyPDFium2 for efficient PDF processing
- **Supported Formats**: PDF, scanned images, text files
- **Language Support**: Hindi, English, and mixed content

## 🔧 Technical Features

- **Session State Management**: Persistent data across page navigation and browser sessions
- **Progress Tracking**: Real-time generation progress with detailed status updates
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Responsive Design**: Mobile-first design that works on all device sizes
- **Modern UI**: Clean, professional interface with custom CSS styling
- **Background Processing**: Non-blocking question generation with progress indicators
- **Memory Management**: Efficient handling of large question banks and PDF files
- **Caching**: Smart caching of generated questions and model outputs
- **Multi-threading**: Parallel processing for faster question generation
- **Auto-save**: Automatic saving of generated questions and user preferences

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. **Installation Issues**
```bash
# Issue: Module not found errors
Solution: pip install -r requirements.txt

# Issue: PyTorch installation problems
Solution: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Issue: Transformers cache permission errors
Solution: Set custom cache directory in .env file
```

#### 2. **Runtime Issues**
```bash
# Issue: Port already in use
Solution: streamlit run mppsc_streamlit_app.py --server.port 8502

# Issue: Model download failures
Solution: Check internet connection and try offline mode

# Issue: PDF processing errors
Solution: Ensure PDF files are not password protected or corrupted
```

#### 3. **Performance Issues**
```bash
# Issue: Slow question generation
Solution: 
- Use offline mode for faster generation
- Reduce number of questions per batch
- Use smaller AI model (flan-t5-small)

# Issue: Memory errors
Solution:
- Close other applications
- Use offline mode
- Generate questions in smaller batches
- Restart the application
```

#### 4. **Web Interface Issues**
```bash
# Issue: Blank page or loading errors
Solution:
- Clear browser cache and cookies
- Try a different browser (Chrome recommended)
- Check browser console for JavaScript errors
- Restart the Streamlit server
```

### Performance Optimization Tips

1. **Hardware Recommendations**:
   - **Minimum**: 4GB RAM, 2GB free disk space
   - **Recommended**: 8GB+ RAM, 5GB+ free disk space
   - **Optimal**: 16GB+ RAM, SSD storage

2. **Software Optimization**:
   - Use offline mode for production environments
   - Cache frequently used topics and templates
   - Generate questions in batches of 5-10 for best performance
   - Regular cleanup of temporary files

3. **Network Optimization**:
   - Download models once and use offline
   - Use local PDF files instead of cloud storage
   - Configure proper proxy settings if behind corporate firewall

## 📄 File Outputs & Formats

### Generated Files
- **`mppsc_questions.csv`** - Structured spreadsheet with all generated questions
  - Columns: Question, Options, Correct Answer, Subject, Topic, Type, Difficulty
- **`mppsc_sample_question_paper.txt`** - Formatted question paper ready for printing
- **`mppsc_comprehensive_question_bank.csv`** - Master database of all questions
- **`mpsc_questions_extracted.csv`** - Questions extracted from PDF sources

### Export Formats
1. **CSV Export**: Complete data with metadata for analysis
2. **Formatted Paper**: Print-ready question paper with proper numbering
3. **PDF Report**: Professional analysis report with statistics
4. **JSON Export**: Machine-readable format for integration

## 🌐 Browser Compatibility

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| **Chrome** | 90+ | ✅ Fully Supported | Recommended browser |
| **Firefox** | 88+ | ✅ Fully Supported | Good performance |
| **Safari** | 14+ | ✅ Supported | Some UI limitations |
| **Edge** | 90+ | ✅ Fully Supported | Windows recommended |
| **Opera** | 76+ | ⚠️ Limited | Basic functionality |

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **Python**: 3.8+
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Internet for initial setup

### Recommended Requirements
- **OS**: Latest stable versions
- **Python**: 3.10+
- **RAM**: 8GB+
- **Storage**: 5GB+ free space (for model cache)
- **Network**: Broadband for model downloads

## 🔐 Security & Privacy

- **Local Processing**: All AI processing happens locally
- **No Data Transmission**: Questions are not sent to external servers
- **Privacy First**: User data and custom topics remain on local machine
- **Secure PDF Processing**: Safe handling of uploaded documents
- **No Telemetry**: No usage tracking or data collection

## 🤝 Support & Contribution

### Getting Help
1. **Documentation**: Check this README for comprehensive guidance
2. **Error Messages**: Application provides detailed error descriptions
3. **Logs**: Check console output for technical details
4. **GitHub Issues**: Report bugs and feature requests

### Contributing
1. **Bug Reports**: Detailed issue descriptions with reproduction steps
2. **Feature Requests**: Suggestions for new functionality
3. **Code Contributions**: Follow standard Python coding conventions
4. **Documentation**: Help improve this README and code comments

## 📝 License & Usage

**Educational Use License**
- ✅ Personal study and practice
- ✅ Educational institution use
- ✅ Non-commercial research
- ❌ Commercial distribution without permission
- ❌ Selling generated questions

**Disclaimer**: This application is designed for practice and study purposes. Generated questions should be used as supplementary material alongside official MPPSC preparation resources.

## 🔄 Version History

- **v1.0.0** - Initial release with basic question generation
- **v1.1.0** - Added PDF extraction capabilities
- **v1.2.0** - Enhanced AI models and offline mode
- **v1.3.0** - Improved web interface and error handling
- **Current** - Full-featured system with comprehensive documentation

---

## 📞 Contact & Support

For technical issues, feature requests, or general questions:

- **Project Repository**: Available in your local workspace
- **Documentation**: This README file
- **System Requirements**: Check compatibility before installation

**Important Note**: This is an educational tool for MPPSC preparation. Always cross-reference with official MPPSC materials and guidelines for examination preparation.

---

*Last Updated: August 2025 | Built with ❤️ for MPPSC aspirants*
