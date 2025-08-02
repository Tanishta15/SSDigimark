# MPPSC Question Generator - Streamlit Web Application

A user-friendly web interface for generating customized MPPSC (Madhya Pradesh Public Service Commission) practice questions.

## Features

- **Custom Topic Input**: Add your own topics for each subject
- **Multiple Subjects**: Support for 7 key MPPSC subjects
- **Question Types**: Various question formats (MCQ, analytical, application-based)
- **Real-time Generation**: Generate questions instantly
- **Download Options**: Export as CSV or formatted question paper
- **Offline Mode**: Works without internet (template-based questions)

## Subjects Covered

1. **Madhya Pradesh General Knowledge**
2. **Indian Polity**
3. **Indian Economy**
4. **Indian History**
5. **Indian Geography**
6. **General Science**
7. **Current Affairs**

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application

#### Option 1: Using the launcher script
```bash
python run_mppsc_app.py
```

#### Option 2: Direct Streamlit command
```bash
streamlit run mppsc_streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## How to Use

### 1. Configure Topics
- Navigate to the "Configure Topics" section
- For each subject, choose between:
  - **Default Topics**: Pre-loaded comprehensive topic list
  - **Custom Topics**: Enter your own topics (one per line)
- View topic summaries for each subject

### 2. Generate Questions
- Select subjects for question generation
- Set the number of questions per subject (1-20)
- Choose between online (AI-enhanced) or offline (template-based) mode
- Click "Generate Questions"

### 3. View Questions
- Browse generated questions with filtering options
- Filter by subject or question type
- View detailed question information including topic, type, and difficulty

### 4. Download Results
- **CSV Export**: Download all questions in spreadsheet format
- **Sample Paper**: Download a formatted question paper

## Application Structure

```
mppsc_streamlit_app.py          # Main Streamlit application
generate_mppsc_questions.py     # Core question generation logic
run_mppsc_app.py               # Application launcher
requirements.txt               # Python dependencies
README_Streamlit.md           # This documentation
```

## Question Types

- **Factual MCQ**: Multiple choice questions with statements
- **Madhya Pradesh Specific**: Questions focused on MP context
- **Analytical**: Questions requiring analysis and evaluation
- **Application**: Questions testing practical application of knowledge
- **Template Enhanced**: Offline template-based questions

## Customization Options

### Adding New Topics
1. Go to "Configure Topics"
2. Uncheck "Use default topics" for any subject
3. Enter your custom topics in the text area
4. Each topic should be on a separate line

### Modifying Question Templates
The application uses predefined templates that can be extended by modifying the `_load_question_templates()` method in the code.

## Technical Features

- **Session State Management**: Maintains data across page navigation
- **Progress Tracking**: Real-time generation progress
- **Error Handling**: Graceful handling of generation errors
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface with custom styling

## Troubleshooting

### Common Issues

1. **Module Not Found Error**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   streamlit run mppsc_streamlit_app.py --server.port 8502
   ```

3. **Memory Issues**
   - Use offline mode for low-memory systems
   - Reduce the number of questions per subject

### Performance Tips

- Use offline mode for faster generation
- Generate questions in smaller batches
- Clear browser cache if experiencing slow loading

## File Outputs

- **CSV File**: `mppsc_questions.csv` - Structured data format
- **Sample Paper**: `mppsc_sample_paper.txt` - Formatted question paper

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Support

For issues or questions:
1. Check the troubleshooting section
2. Ensure all dependencies are properly installed
3. Verify Python version compatibility

## License

This project is for educational purposes. Please ensure compliance with relevant examination body guidelines when using generated questions.

---

**Note**: This application is designed for practice and study purposes. Generated questions should be used as supplementary material alongside official MPPSC preparation resources.
