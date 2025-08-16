"""
Configuration file for MPPSC Integrated Platform
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
EVALUATOR_DIR = BASE_DIR / "SSDigimark-evaluator" / "SSDigimark-evaluator"
MASTER_DIR = BASE_DIR / "SSDigimark-master" / "SSDigimark-master" 
GENERATOR_DIR = BASE_DIR / "SSDigimark-Question-generator" / "SSDigimark-Question-generator"

# Temporary directories
TEMP_DIR = BASE_DIR / "temp"
UPLOADS_DIR = TEMP_DIR / "uploads"
ANSWER_KEYS_DIR = TEMP_DIR / "answer_keys"
ANSWER_SHEETS_DIR = TEMP_DIR / "answer_sheets"
RESULTS_DIR = TEMP_DIR / "results"
EVALUATION_DIR = TEMP_DIR / "evaluation"
CACHE_DIR = TEMP_DIR / "cache"

# File extensions
ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
ALLOWED_PDF_EXTENSIONS = ['.pdf']
ALLOWED_CSV_EXTENSIONS = ['.csv']

# OCR settings
OCR_CONFIDENCE_THRESHOLD = 0.8
DEFAULT_OCR_ENGINE = "easyocr"

# Evaluation settings
DEFAULT_MARKING_SCHEME = {
    'correct': 1.0,
    'incorrect': -0.33,
    'unanswered': 0.0
}

# Grammar checker settings
GRAMMAR_CHECK_SETTINGS = {
    'check_spelling': True,
    'check_grammar': True,
    'check_style': True,
    'language': 'en-US'
}

# Question generator settings
QUESTION_GENERATOR_SETTINGS = {
    'default_num_questions': 10,
    'max_questions': 100,
    'default_difficulty': 'medium',
    'default_subject': 'all'
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'MPPSC Integrated Platform',
    'page_icon': '📚',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Database settings (if needed in future)
DATABASE_SETTINGS = {
    'use_database': False,
    'database_url': 'sqlite:///mppsc_platform.db'
}

# API settings (if needed)
API_SETTINGS = {
    'enable_api': False,
    'api_host': '0.0.0.0',
    'api_port': 8000
}

# Logging settings
LOGGING_SETTINGS = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/mppsc_platform.log'
}

# Security settings
SECURITY_SETTINGS = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_file_types': ALLOWED_IMAGE_EXTENSIONS + ALLOWED_PDF_EXTENSIONS + ALLOWED_CSV_EXTENSIONS,
    'scan_uploads': False
}

def create_directories():
    """Create required directories if they don't exist"""
    directories = [
        TEMP_DIR,
        UPLOADS_DIR,
        ANSWER_KEYS_DIR,
        ANSWER_SHEETS_DIR,
        RESULTS_DIR,
        EVALUATION_DIR,
        CACHE_DIR,
        BASE_DIR / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_project_paths():
    """Get all project paths for import"""
    return [
        str(EVALUATOR_DIR),
        str(MASTER_DIR),
        str(GENERATOR_DIR)
    ]

# Initialize directories on import
create_directories()
