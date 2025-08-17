import streamlit as st
import os
import sys
import pandas as pd
import random
import io
import traceback
import re
import tempfile
import subprocess
import json
import asyncio
from datetime import datetime
from typing import Dict, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(page_title="MPPSC Services", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS Styling ----------
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #e0e7ff 0%, #f7f9fc 100%);
    }
    .title {
        text-align: center;
        font-size: 48px;
        font-weight: 1200;
        color: #2563eb;
        margin-top: 30px;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .subtitle {
        text-align: center;
        font-size: 24px;
        color: #64748b;
        margin-bottom: 40px;
        font-weight: 500;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e40af 0%, #3b82f6 100%);
    }
    
    /* Main content area */
    .main-content {
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem;
    }
    
    /* Info cards styling */
    .stAlert > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-left: 4px solid #0ea5e9;
        border-radius: 8px;
        color: #1e293b !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stAlert p {
        color: #334155 !important;
        font-weight: 500;
    }
    
    .stAlert strong {
        color: #0f172a !important;
        font-weight: 700;
    }
    
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 40px;
        justify-items: center;
        padding: 0 10%;
        margin-bottom: 40px;
    }
    .grid-button {
        background: linear-gradient(120deg, #4f8cff 0%, #6ee7b7 100%);
        color: #fff !important;
        padding: 32px 0;
        text-align: center;
        font-size: 40px;
        font-weight: 700;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(79,140,255,0.13);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
        width: 100%;
        min-height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        border: none;
        outline: none;
    }
    .grid-button:hover {
        background: linear-gradient(120deg, #265df2 0%, #34d399 100%);
        transform: scale(1.04);
        box-shadow: 0 12px 32px rgba(46, 91, 255, 0.18);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for page selection
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = None

# Sidebar Navigation
with st.sidebar:
    st.title("MPPSC Services")
    st.markdown("---")
    
    # Navigation buttons
    if st.button("Grade Answer Sheet", use_container_width=True, type="primary" if st.session_state.selected_page == "grade" else "secondary"):
        st.session_state.selected_page = "grade"
        st.rerun()
    
    if st.button("Question Paper Generator", use_container_width=True, type="primary" if st.session_state.selected_page == "qgen" else "secondary"):
        st.session_state.selected_page = "qgen"
        st.rerun()
    
    if st.button("Grammar Checker", use_container_width=True, type="primary" if st.session_state.selected_page == "grammar" else "secondary"):
        st.session_state.selected_page = "grammar"
        st.rerun()
    
    st.markdown("---")
    st.markdown("Select a service to get started")

# Main content area
if st.session_state.selected_page is None:
    # Welcome screen
    st.markdown('<div class="title">Welcome to MPPSC Services</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Select a service from the sidebar to get started</div>', unsafe_allow_html=True)
    
    # Add some information cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **Grade Answer Sheet**
        
        Automated AI-powered grading of handwritten answer sheets with semantic similarity analysis.
        """)
    
    with col2:
        st.info("""
        **Question Paper Generator**
        
        Create professional MPPSC-style question papers with customizable topics and PDF export.
        """)
    
    with col3:
        st.info("""
        **Grammar Checker**
        
        Advanced AI-powered grammar analysis with error detection and correction suggestions.
        """)

elif st.session_state.selected_page == "grade":
        # --- Grading UI and Logic (from frontend.py) with error handling ---
        import os, sys, asyncio, json, time, pandas as pd, io, traceback
        try:
            sys.path.append(os.path.abspath(os.path.dirname(__file__)))
            sys.path.append(os.path.abspath("finalflow/flow"))
            
            # Import the pipeline module
            try:
                import pipeline
            except ImportError:
                st.error("Pipeline module not found. Please check your finalflow installation.")
                st.stop()
                
            ANSWERKEY_FOLDER = os.path.abspath("finalflow/input_folder/AnswerKey/clean_pdf")
            ANSWERSHEET_FOLDER = os.path.abspath("finalflow/input_folder/AnswerSheet/Handwritten")
            RESULTS_FOLDER = os.path.abspath("finalflow/results")
            TEMPIMG = os.path.abspath("finalflow/input_folder/AnswerSheet")
            os.makedirs(ANSWERKEY_FOLDER, exist_ok=True)
            os.makedirs(ANSWERSHEET_FOLDER, exist_ok=True)
            os.makedirs(RESULTS_FOLDER, exist_ok=True)
            os.makedirs(TEMPIMG, exist_ok=True)

            def save_uploaded_file(uploaded_file, folder):
                file_path = os.path.join(folder, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                return file_path

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
                import finalflow.flow.app as pipeline
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(pipeline.main(
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

            def load_similarity_results():
                files = [f for f in os.listdir(RESULTS_FOLDER) if f.startswith("similarity_") and f.endswith(".json")]
                if not files:
                    return None
                files.sort(key=lambda f: os.path.getmtime(os.path.join(RESULTS_FOLDER, f)), reverse=True)
                result_file = os.path.join(RESULTS_FOLDER, files[0])
                with open(result_file, "r") as f:
                    return json.load(f)

            def allocate_marks(score, thresholds, total_marks):
                if score >= thresholds["full_marks"]:
                    return total_marks
                elif score >= thresholds["high_marks"]:
                    return total_marks * 0.75
                elif score >= thresholds["mid_marks"]:
                    return total_marks * 0.5
                elif score >= thresholds["low_marks"]:
                    return total_marks * 0.25
                else:
                    return 0

            st.title("Assessly - Grading Assistant")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.header("Answer Key Upload")
                answer_key = st.file_uploader("Upload Answer Key", type=['pdf'], key="answer_key")
                if answer_key:
                    save_uploaded_file(answer_key, ANSWERKEY_FOLDER)
                    st.success(f"{answer_key.name} Uploaded Successfully!")
                
                st.header("Answer Sheet Upload")
                answer_sheets = st.file_uploader("Upload Answer Sheets", type=['pdf'], accept_multiple_files=True, key="answer_sheets")
                if answer_sheets:
                    for sheet in answer_sheets:
                        save_uploaded_file(sheet, ANSWERSHEET_FOLDER)
                    st.success(f"{len(answer_sheets)} PDF(s) Uploaded Successfully!")
            
            with col2:
                st.header("Difficulty Level")
                difficulty = st.radio("Select Difficulty", ["Easy 🟢", "Medium 🟠", "Hard 🔴", "Customize"], index=1, key="difficulty")
                if difficulty == "Customize":
                    st.subheader("Customize Difficulty Level")
                    difficulty_thresholds = {
                        "full_marks": st.slider("Full Marks Threshold", 0.0, 1.0, 0.8, key="full_marks"),
                        "high_marks": st.slider("High Marks Threshold", 0.0, 1.0, 0.7, key="high_marks"),
                        "mid_marks": st.slider("Mid Marks Threshold", 0.0, 1.0, 0.6, key="mid_marks"),
                        "low_marks": st.slider("Low Marks Threshold", 0.0, 1.0, 0.5, key="low_marks")
                    }
                else:
                    difficulty_thresholds = {
                        "Easy 🟢": {"full_marks": 0.8, "high_marks": 0.7, "mid_marks": 0.6, "low_marks": 0.5},
                        "Medium 🟠": {"full_marks": 0.75, "high_marks": 0.65, "mid_marks": 0.55, "low_marks": 0.45},
                        "Hard 🔴": {"full_marks": 0.7, "high_marks": 0.6, "mid_marks": 0.5, "low_marks": 0.4}
                    }[difficulty]
                total_marks = st.number_input("Enter Total Marks per Question", min_value=1, value=4, key="total_marks")

            st.divider()
            if st.button("Start Grading Process", key="start_grading"):
                try:
                    if answer_key and answer_sheets:
                        with st.spinner("Processing... Please wait ⏳"):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            processing_steps = [
                                "Uploading answer scripts...",
                                "Reading handwritten responses...",
                                "Extracting key content...",
                                "Matching answers to reference...",
                                "Evaluating based on similarity...",
                                "Assigning scores carefully...",
                                "Summarizing performance metrics...",
                                "Double-checking evaluations...",
                                "Compiling final reports...",
                                "Preparing your results!"
                            ]
                            for i, step in enumerate(processing_steps):
                                time.sleep(1)
                                progress_bar.progress((i + 1) * 10)
                                status_text.text(step)
                            answer_sheet_path = os.path.join(ANSWERSHEET_FOLDER, answer_sheets[0].name)
                            answer_key_path = os.path.join(ANSWERKEY_FOLDER, answer_key.name)
                            extracted_text_pdf = os.path.join(ANSWERSHEET_FOLDER, "extracted_text.pdf")
                            temp_image_dir = os.path.join(ANSWERSHEET_FOLDER, "tempimg")
                            output_json_answersheet = os.path.join(ANSWERSHEET_FOLDER, "Json_with_answers", "answersheet.json")
                            output_json_answerkey = os.path.join(ANSWERKEY_FOLDER, "Json_with_answers", "answerkey.json")
                            result_dir = RESULTS_FOLDER
                            os.makedirs(os.path.dirname(output_json_answersheet), exist_ok=True)
                            os.makedirs(os.path.dirname(output_json_answerkey), exist_ok=True)
                            os.makedirs(temp_image_dir, exist_ok=True)
                            trigger_grading(
                                input_pdf_answersheet=answer_sheet_path,
                                input_pdf_answerkey=answer_key_path,
                                extracted_text_pdf=extracted_text_pdf,
                                temp_image_dir=temp_image_dir,
                                output_json_answersheet=output_json_answersheet,
                                output_json_answerkey=output_json_answerkey,
                                result_dir=result_dir,
                                difficulty=difficulty,
                                total_marks=total_marks,
                                thresholds=difficulty_thresholds
                            )
                            progress_bar.empty()
                            status_text.text("Grading Complete!")
                        similarity_results = load_similarity_results()
                        if similarity_results:
                            comparisons = similarity_results.get('comparisons', [])
                            if comparisons:
                                comparison_data = []
                                total_obtained_marks = 0
                                for comp in comparisons:
                                    question_number = comp.get("question_number")
                                    answer1 = comp.get("answer1", "")
                                    answer2 = comp.get("answer2", "")
                                    similarity_score = comp.get("similarity_score", 0)
                                    marks_obtained = allocate_marks(similarity_score, difficulty_thresholds, total_marks)
                                    total_obtained_marks += marks_obtained
                                    comparison_data.append({
                                        "Question Number": question_number,
                                        "Answer 1": answer1,
                                        "Answer 2": answer2,
                                        "Similarity Score": round(similarity_score, 4),
                                        "Marks Obtained": round(marks_obtained, 2)
                                    })
                                df_results = pd.DataFrame(comparison_data)
                                st.subheader("Detailed Results")
                                st.dataframe(df_results, use_container_width=True)
                                st.success(f"Total Marks Obtained: {round(total_obtained_marks, 2)} / {len(comparisons) * total_marks}")
                                csv_buffer = io.StringIO()
                                df_results.to_csv(csv_buffer, index=False)
                                st.download_button(
                                    label="Download Results as CSV",
                                    data=csv_buffer.getvalue(),
                                    file_name="grading_results.csv",
                                    mime="text/csv"
                                )
                            else:
                                st.warning("No comparisons found in the results.")
                        else:
                            st.warning("No similarity results file found.")
                except Exception as e:
                    st.error(f"An error occurred during grading: {e}")
                    st.code(traceback.format_exc())
        except Exception as e:
            st.error(f"A setup error occurred: {e}")
            st.code(traceback.format_exc())
            
elif st.session_state.selected_page == "qgen":
    # --- Question Generator UI and Logic ---
    st.subheader("Question Paper Generator")
    st.write("Generate professional MPPSC-style question papers with customizable topics and formats.")
    
    # Simple, working question generator interface
    try:
        # Initialize session state for question generator
        if 'qgen_questions' not in st.session_state:
            st.session_state.qgen_questions = []
        if 'qgen_topics' not in st.session_state:
            st.session_state.qgen_topics = {}
        
        # Add CSS for question generator
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .question-card {
            background: var(--card-background, white);
            border: 1px solid var(--border-color, #e0e0e0);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: var(--text-color, #333);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>MPPSC Question Generator</h1>
            <p>Generate customized questions for Madhya Pradesh Public Service Commission</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for different functionalities
        tab1, tab2, tab3 = st.tabs(["Configure Topics", "Generate Questions", "Question Bank"])
        
        with tab1:
            st.header("Configure Your Topics")
            
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
            
            # Default topics
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
            
            # Create topic configuration interface
            user_topics = st.session_state.qgen_topics.copy() if st.session_state.qgen_topics else {}
            
            for subject in subjects:
                with st.expander(f"{subject.replace('_', ' ').title()}", expanded=False):
                    use_default = st.checkbox(f"Use default topics", 
                                            value=True, 
                                            key=f"default_{subject}")
                    
                    if use_default:
                        user_topics[subject] = default_curriculum.get(subject, [])
                        st.success(f"Using {len(default_curriculum.get(subject, []))} default topics")
                        
                        # Show default topics
                        if st.checkbox(f"Show topics", key=f"show_{subject}"):
                            for topic in default_curriculum.get(subject, []):
                                st.write(f"• {topic}")
                    else:
                        # Custom topic input
                        st.write("Enter your custom topics (one per line):")
                        existing_text = '\n'.join(user_topics.get(subject, []))
                        
                        custom_topics_text = st.text_area(
                            f"Topics for {subject.replace('_', ' ')}",
                            value=existing_text,
                            height=150,
                            key=f"custom_{subject}"
                        )
                        
                        if custom_topics_text:
                            custom_topics = [topic.strip() for topic in custom_topics_text.split('\n') if topic.strip()]
                            user_topics[subject] = custom_topics
                            st.success(f"Added {len(custom_topics)} custom topics")
                        else:
                            user_topics[subject] = []
            
            st.session_state.qgen_topics = user_topics
            
            if st.button("Save Topic Configuration"):
                st.success("Topics configuration saved!")
        
        with tab2:
            st.header("Generate Questions")
            
            # Generation parameters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                num_questions = st.number_input("Number of questions", min_value=1, max_value=50, value=10)
            
            with col2:
                question_type = st.selectbox("Question type", ["Short Answer", "Long Answer", "Mixed"])
            
            with col3:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
            
            # Subject selection
            if st.session_state.qgen_topics:
                selected_subjects = st.multiselect(
                    "Select subjects",
                    list(st.session_state.qgen_topics.keys()),
                    default=list(st.session_state.qgen_topics.keys())[:3]
                )
            else:
                st.warning("Please configure topics first in the Configure Topics tab.")
                selected_subjects = []
            
            if st.button("Generate Questions") and selected_subjects:
                with st.spinner("Generating questions..."):
                    generated_questions = []
                    
                    for i in range(num_questions):
                        subject = random.choice(selected_subjects)
                        topics = st.session_state.qgen_topics.get(subject, [])
                        
                        if topics:
                            topic = random.choice(topics)
                            
                            # Simple question generation templates
                            templates = {
                                'madhya_pradesh_gk': [
                                    f"What is the historical significance of {topic} in Madhya Pradesh?",
                                    f"Discuss the role of {topic} in the development of Madhya Pradesh.",
                                    f"Explain the importance of {topic} in Madhya Pradesh's cultural heritage."
                                ],
                                'indian_polity': [
                                    f"Explain the constitutional provisions related to {topic}.",
                                    f"What is the role of {topic} in Indian democratic system?",
                                    f"Discuss the powers and functions of {topic}."
                                ],
                                'indian_economy': [
                                    f"Analyze the impact of {topic} on Indian economic growth.",
                                    f"What are the challenges and opportunities in {topic}?",
                                    f"Discuss the government policies related to {topic}."
                                ],
                                'indian_history': [
                                    f"Discuss the historical importance of {topic} in Indian history.",
                                    f"What were the major achievements during {topic}?",
                                    f"How did {topic} influence Indian society and culture?"
                                ],
                                'indian_geography': [
                                    f"Explain the geographical significance of {topic}.",
                                    f"What are the climatic conditions associated with {topic}?",
                                    f"How does {topic} affect the agricultural pattern of the region?"
                                ],
                                'general_science': [
                                    f"Explain the scientific principles behind {topic}.",
                                    f"What are the applications of {topic} in daily life?",
                                    f"Discuss the recent developments in {topic}."
                                ],
                                'current_affairs': [
                                    f"Analyze the recent developments in {topic}.",
                                    f"What is the significance of {topic} in current context?",
                                    f"Discuss the implications of {topic} for India."
                                ]
                            }
                            
                            # Get templates for the subject
                            subject_templates = templates.get(subject, templates['indian_polity'])
                            question_text = random.choice(subject_templates)
                            
                            # Modify based on question type
                            if question_type == "Short Answer":
                                question_text = f"Briefly explain: {topic}"
                            elif question_type == "Long Answer":
                                question_text = f"Critically analyze and discuss in detail: {topic}"
                            
                            generated_questions.append({
                                'question': question_text,
                                'subject': subject,
                                'topic': topic,
                                'type': question_type if question_type != "Mixed" else random.choice(["Short Answer", "Long Answer"]),
                                'difficulty': difficulty if difficulty != "Mixed" else random.choice(["Easy", "Medium", "Hard"]),
                                'source': 'AI Generated',
                                'year': datetime.now().year
                            })
                    
                    st.session_state.qgen_questions.extend(generated_questions)
                    st.success(f"Generated {len(generated_questions)} questions!")
        
        with tab3:
            st.header("Question Bank")
            
            # Display all questions
            if st.session_state.qgen_questions:
                st.subheader(f"Total Questions: {len(st.session_state.qgen_questions)}")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_subject = st.selectbox(
                        "Filter by subject",
                        ["All"] + list(set(q['subject'] for q in st.session_state.qgen_questions))
                    )
                with col2:
                    filter_type = st.selectbox(
                        "Filter by type",
                        ["All"] + list(set(q['type'] for q in st.session_state.qgen_questions))
                    )
                with col3:
                    show_count = st.slider("Questions to show", 5, min(30, len(st.session_state.qgen_questions)), 10)
                
                # Filter questions
                filtered_questions = st.session_state.qgen_questions
                if filter_subject != "All":
                    filtered_questions = [q for q in filtered_questions if q['subject'] == filter_subject]
                if filter_type != "All":
                    filtered_questions = [q for q in filtered_questions if q['type'] == filter_type]
                
                # Display questions
                for i, q in enumerate(filtered_questions[:show_count], 1):
                    st.markdown(f"""
                    <div class="question-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0;">Q{i}</h4>
                            <div>
                                <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">
                                    {q['subject'].replace('_', ' ').title()}
                                </span>
                                <span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                    {q['type']}
                                </span>
                            </div>
                        </div>
                        <p><strong>Topic:</strong> {q['topic']}</p>
                        <p style="margin: 0; line-height: 1.6; font-size: 1.1em;">{q['question']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download options
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Clear All Questions"):
                        st.session_state.qgen_questions = []
                        st.success("All questions cleared!")
                        st.rerun()
                
                with col2:
                    # Download CSV
                    df = pd.DataFrame(st.session_state.qgen_questions)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"mppsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    # Create text question paper
                    paper_text = f"""
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

═══════════════════════════════════════════════════════════════════

"""
                    
                    for i, q in enumerate(st.session_state.qgen_questions, 1):
                        paper_text += f"{i}. {q['question']}\n\n"
                    
                    paper_text += "═" * 67 + "\n"
                    paper_text += "                           END OF PAPER\n"
                    paper_text += "═" * 67
                    
                    st.download_button(
                        label="Download TXT",
                        data=paper_text,
                        file_name=f"mppsc_question_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            else:
                st.info("No questions generated yet. Go to the 'Generate Questions' tab to create some questions!")
    
    except Exception as e:
        st.error(f"Error in question generator: {e}")
        st.code(traceback.format_exc())
    
    # Add question generator path
    qgen_path = os.path.join(os.path.dirname(__file__), 'SSDigimark-Question-generator')
    if qgen_path not in sys.path:
        sys.path.insert(0, qgen_path)
    
    try:
        import pypdfium2 as pdfium
        import easyocr
        import numpy as np
        import unicodedata
        from generate_mppsc_questions import MPPSCQuestionGenerator
        PDF_SUPPORT = True
        QGEN_SUPPORT = True
    except ImportError as e:
        PDF_SUPPORT = False
        QGEN_SUPPORT = False
        # Don't show warning in the main UI, just use fallback
        # st.warning(f"Some libraries not installed ({e}). Using fallback functionality.")
        
        # Create fallback question generator class
        class MPPSCQuestionGenerator:
            def __init__(self):
                self.offline_mode = True
                
            def generate_subject_wise_questions(self, subject, num_questions=8):
                return self._generate_fallback_questions(subject, num_questions)
                
            def _generate_fallback_questions(self, subject, num_questions):
                topics = {
                    'madhya_pradesh_gk': ['MP History', 'MP Geography', 'MP Culture'],
                    'indian_polity': ['Constitution', 'Parliament', 'Judiciary'],
                    'indian_economy': ['Budget', 'Banking', 'Trade'],
                    'indian_history': ['Ancient India', 'Medieval India', 'Modern India'],
                    'indian_geography': ['Rivers', 'Mountains', 'Climate'],
                    'general_science': ['Physics', 'Chemistry', 'Biology'],
                    'current_affairs': ['Government Schemes', 'Recent Events']
                }.get(subject, ['General Topic'])
                
                questions = []
                for i in range(num_questions):
                    topic = random.choice(topics)
                    questions.append({
                        'question': f"Explain the significance of {topic} in the context of {subject.replace('_', ' ')}.",
                        'subject': subject,
                        'topic': topic,
                        'type': 'descriptive',
                        'difficulty': 'moderate'
                    })
                return questions

        # Fallback question generator
        def generate_questions_by_topic(topic, num_questions=10, difficulty='Medium'):
            # Load the CSV file if it exists
            csv_file = os.path.join(qgen_path, 'mppsc_comprehensive_question_bank.csv')
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    if 'Topic' in df.columns:
                        topic_questions = df[df['Topic'].str.contains(topic, case=False, na=False)]
                        if len(topic_questions) > 0:
                            return topic_questions.sample(min(num_questions, len(topic_questions))).to_dict('records')
                except Exception as e:
                    st.error(f"Error reading question bank: {e}")
            
            # Fallback to sample questions
            sample_questions = [
                {"question": f"Explain the importance of {topic} in the context of Madhya Pradesh.", "marks": 5, "type": "Short"},
                {"question": f"Discuss the role of {topic} in Indian governance.", "marks": 10, "type": "Medium"},
                {"question": f"Analyze the impact of {topic} on society and economy.", "marks": 15, "type": "Long"},
                {"question": f"What are the key challenges in {topic}? Suggest solutions.", "marks": 10, "type": "Medium"},
                {"question": f"Compare and contrast different approaches to {topic}.", "marks": 15, "type": "Long"}
            ]
            return random.sample(sample_questions, min(num_questions, len(sample_questions)))
        
        # Function definitions for question paper generation
        def create_mppsc_pdf_question_paper(questions):
            """Create a PDF question paper using reportlab"""
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
                import tempfile
                
                # Create a temporary PDF file
                temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                temp_pdf.close()
                
                # Create PDF document
                doc = SimpleDocTemplate(temp_pdf.name, pagesize=A4, 
                                       rightMargin=72, leftMargin=72, 
                                       topMargin=72, bottomMargin=18)
                
                # Get styles
                styles = getSampleStyleSheet()
                
                # Create custom styles
                title_style = ParagraphStyle('CustomTitle', 
                                            parent=styles['Heading1'],
                                            fontSize=18,
                                            spaceAfter=30,
                                            alignment=TA_CENTER)
                
                section_style = ParagraphStyle('CustomSection',
                                              parent=styles['Heading2'], 
                                              fontSize=14,
                                              spaceAfter=12,
                                              spaceBefore=24)
                
                question_style = ParagraphStyle('CustomQuestion',
                                               parent=styles['Normal'],
                                               fontSize=11,
                                               spaceAfter=12,
                                               leftIndent=20)
                
                # Story list to hold content
                story = []
                
                # Add title page
                story.append(Paragraph("MPPSC SAMPLE QUESTION PAPER", title_style))
                story.append(Paragraph("Madhya Pradesh Public Service Commission", styles['Heading3']))
                story.append(Spacer(1, 12))
                story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
                story.append(Paragraph("Time: 2 Hours &nbsp;&nbsp;&nbsp;&nbsp; Maximum Marks: 200", styles['Normal']))
                story.append(Spacer(1, 24))
                
                # Add instructions
                story.append(Paragraph("Instructions:", styles['Heading4']))
                story.append(Paragraph("1. All questions are compulsory.", styles['Normal']))
                story.append(Paragraph("2. Each question carries equal marks.", styles['Normal']))
                story.append(Paragraph("3. Read the questions carefully before answering.", styles['Normal']))
                story.append(Spacer(1, 24))
                
                # Group questions by subject
                subject_wise = {}
                for q in questions:
                    subject = q['subject']
                    if subject not in subject_wise:
                        subject_wise[subject] = []
                    subject_wise[subject].append(q)
                
                question_number = 1
                
                for subject, subject_questions in subject_wise.items():
                    # Add section header
                    subject_title = f"SECTION: {subject.replace('_', ' ').upper()}"
                    story.append(Paragraph(subject_title, section_style))
                    
                    for q in subject_questions:
                        question_text = f"Q{question_number}. {q['question']}"
                        
                        # Clean up the question text for PDF
                        question_text = question_text.replace('\n', '<br/>')
                        question_text = question_text.replace('&', '&amp;')
                        question_text = question_text.replace('<', '&lt;')
                        question_text = question_text.replace('>', '&gt;')
                        
                        story.append(Paragraph(question_text, question_style))
                        
                        # Add topic and metadata if available
                        if 'topic' in q and q['topic']:
                            meta_text = f"<i>Topic: {q['topic']}</i>"
                            story.append(Paragraph(meta_text, styles['Normal']))
                        
                        story.append(Spacer(1, 6))
                        question_number += 1
                
                # Build PDF
                doc.build(story)
                
                # Read the PDF file and return as bytes
                with open(temp_pdf.name, 'rb') as f:
                    pdf_bytes = f.read()
                
                # Clean up temp file
                os.unlink(temp_pdf.name)
                
                return pdf_bytes
                
            except ImportError:
                st.error("ReportLab library not installed. Installing now...")
                try:
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
                    st.success("ReportLab installed! Please try again.")
                    return None
                except Exception as e:
                    st.error(f"Failed to install ReportLab: {e}")
                    return None
            except Exception as e:
                st.error(f"Error creating PDF: {e}")
                return None

        def create_question_paper(questions):
            """Create a formatted question paper (text version for compatibility)"""
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

        def extract_questions_from_text(text_content, file_name):
            """Extract questions from text content with better cleaning"""
            questions = []
            
            # Clean the text first
            text_content = clean_extracted_text(text_content)
            
            # Enhanced question patterns - more specific and cleaner
            patterns = [
                # Questions ending with question mark
                r'(?:^|\s)(?:\d+[\.\)]\s*)?([A-Z][^?]*\?)',
                # Questions starting with question words
                r'(?:^|\s)(?:\d+[\.\)]\s*)?((?:What|Which|Who|When|Where|Why|How|Name|Define|Explain|Describe|Mention|Write|Give|State|Discuss|Analyze)\s+[^?]*\?)',
            ]
            
            exclude_patterns = [
                r'This question contains', r'Answer each question', r'All questions are compulsory',
                r'Each question carries', r'very short answer type', r'short answer type',
                r'long answer type', r'marks\s*\.', r'P\.T\.O\.', r'SECTION', r'Roll No',
                r'Candidate should', r'Time:', r'Maximum Marks', r'Instructions',
                r'write his her', r'hmch', r'felT', r'tetinfl', r'TORl', r'cTWf',
                r'^[A-Z]\s+\d+', r'^\d+\s+[A-Z]',  # Single letter + number patterns
            ]
            
            question_set = set()
            
            for pattern in patterns:
                matches = re.finditer(pattern, text_content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    question_text = match.group(1).strip()
                    
                    # Check if question should be excluded
                    if any(re.search(exclude_pattern, question_text, re.IGNORECASE) for exclude_pattern in exclude_patterns):
                        continue
                    
                    # Clean the question text
                    question_text = clean_question_text(question_text)
                    
                    # Validate question quality
                    if is_valid_question(question_text) and question_text not in question_set:
                        question_set.add(question_text)
                        
                        # Subject classification
                        subject, topic = classify_question(question_text)
                        
                        questions.append({
                            'question': question_text,
                            'subject': subject,
                            'topic': topic,
                            'type': 'Short Answer',
                            'difficulty': 'Medium',
                            'source': f'Extracted from {file_name}',
                            'year': datetime.now().year
                        })
            
            return questions[:20]  # Limit to 20 questions

        def clean_extracted_text(text):
            """Clean extracted text from PDFs"""
            # Remove excessive whitespace and normalize
            text = re.sub(r'\s+', ' ', text)
            
            # Remove common PDF extraction artifacts but keep question text
            # Remove specific problematic patterns first
            text = re.sub(r'M-\d{4}/GS-[IVX]+\s+\d+[^\w\s]*', '', text)  # Remove exam codes
            text = re.sub(r'Roll\s*No[^\n?]*(?:\n|$)', '', text, flags=re.IGNORECASE)
            text = re.sub(r'Candidate\s+should[^\n?]*(?:\n|$)', '', text, flags=re.IGNORECASE)
            
            # Remove lines that are mostly symbols or gibberish
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    # Check if line is mostly gibberish
                    letter_count = len(re.findall(r'[A-Za-z]', line))
                    symbol_count = len(re.findall(r'[^\w\s\?\.\,\-\(\)\:\;\'\"!]', line))
                    
                    # Keep line if it has reasonable letter content or ends with question mark
                    if (letter_count > 5 and symbol_count < letter_count) or line.endswith('?'):
                        # Clean individual line
                        line = re.sub(r'[^\w\s\?\.\,\-\(\)\:\;\'\"!\']', ' ', line)
                        line = re.sub(r'\s+', ' ', line).strip()
                        if len(line) > 5:  # Only keep meaningful lines
                            cleaned_lines.append(line)
            
            text = ' '.join(cleaned_lines)
            
            # Final cleanup
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()

        def clean_question_text(question):
            """Clean individual question text"""
            # Remove question numbers at the beginning
            question = re.sub(r'^\s*\d+[\.\)]\s*', '', question)
            
            # Remove problematic character sequences but keep essential text
            question = re.sub(r'\^[a-z]', '', question)  # Remove ^d, ^s etc
            question = re.sub(r'[^\w\s\?\.\,\-\(\)\:\;\'\"!\']', ' ', question)
            
            # Fix spacing
            question = re.sub(r'\s+', ' ', question)
            
            # Ensure question ends with question mark if it's a question
            question = question.strip()
            if not question.endswith('?') and any(word in question.lower() for word in ['what', 'which', 'who', 'when', 'where', 'why', 'how']):
                question += '?'
            
            return question

        def is_valid_question(question):
            """Validate if the extracted text is a proper question"""
            if len(question) < 8 or len(question) > 500:
                return False
            
            # Check for minimum number of actual words
            words = re.findall(r'\b[A-Za-z]{2,}\b', question)
            if len(words) < 3:
                return False
            
            # Check for known meaningless patterns (very specific gibberish only)
            meaningless_patterns = [
                r'hmch', r'felT', r'tetinfl', r'TORl', r'cTWf', r'3TT',
                r'write his her', r'Roll No', r'here',
                r'^[A-Z]\s+\d+', r'^\d+\s+[A-Z]',  # Single letter + number patterns
                r'[0-9]{2,}[A-Z]{2,}[0-9]{2,}',  # Number-letter-number patterns
            ]
            
            for pattern in meaningless_patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    return False
            
            # Check for minimum meaningful English words (including question words)
            common_words = ['what', 'which', 'who', 'when', 'where', 'why', 'how', 'are', 'is', 'was', 'were', 'the', 'in', 'of', 'and', 'or', 'for', 'with', 'from', 'by', 'to', 'at', 'on', 'many', 'meant', 'ruler', 'ended', 'mentioned']
            found_common = sum(1 for word in words if word.lower() in common_words)
            
            # Should have at least 1 common English word OR start with question word
            starts_with_question = any(question.lower().startswith(qw) for qw in ['what', 'which', 'who', 'when', 'where', 'why', 'how'])
            
            if found_common < 1 and not starts_with_question:
                return False
            
            # Check for too many remaining special characters
            clean_question = re.sub(r'[^\w\s\?\.\,\-\(\)\:\;\'\"!]', '', question)
            if len(clean_question) < len(question) * 0.7:  # More than 30% removed
                return False
            
            return True

        def classify_question(question_text):
            """Classify question into subject and topic"""
            question_lower = question_text.lower()
            
            # Enhanced classification
            if any(word in question_lower for word in ['constitution', 'parliament', 'government', 'fundamental rights', 'directive principles', 'president', 'prime minister', 'supreme court', 'lok sabha', 'rajya sabha']):
                return "indian_polity", "Constitutional Law & Governance"
            elif any(word in question_lower for word in ['economy', 'gdp', 'budget', 'fiscal', 'monetary', 'rbi', 'banking', 'inflation', 'trade', 'planning']):
                return "indian_economy", "Economic Development"
            elif any(word in question_lower for word in ['history', 'ancient', 'medieval', 'british', 'mughal', 'mauryan', 'gupta', 'freedom struggle', 'independence']):
                return "indian_history", "Indian History"
            elif any(word in question_lower for word in ['geography', 'river', 'mountain', 'climate', 'monsoon', 'plateau', 'desert', 'forest', 'minerals']):
                return "indian_geography", "Physical Geography"
            elif any(word in question_lower for word in ['madhya pradesh', 'mp', 'bhopal', 'indore', 'gwalior', 'jabalpur', 'narmada', 'chambal', 'vindhya', 'satpura']):
                return "madhya_pradesh_gk", "State Knowledge"
            elif any(word in question_lower for word in ['science', 'physics', 'chemistry', 'biology', 'technology', 'computer', 'space', 'nuclear', 'medical']):
                return "general_science", "Science & Technology"
            elif any(word in question_lower for word in ['current', 'recent', 'award', 'sports', 'scheme', 'policy', 'government scheme']):
                return "current_affairs", "Current Affairs"
            else:
                return "general_studies", "Mixed Topics"

        def extract_questions_from_pdf(pdf_content, file_name):
            """Extract questions from PDF content with improved OCR handling"""
            if not PDF_SUPPORT:
                return []
            
            try:
                # First try basic PDF text extraction
                pdf = pdfium.PdfDocument(pdf_content)
                all_text = ""
                
                for page_num in range(min(5, len(pdf))):  # Limit to first 5 pages
                    page = pdf.get_page(page_num)
                    textpage = page.get_textpage()
                    text = textpage.get_text_range()
                    
                    # If text extraction yields very little or garbled text, try OCR
                    if len(text.strip()) < 50 or has_too_much_gibberish(text):
                        try:
                            # Convert page to image for OCR
                            bitmap = page.render(scale=2.0)  # Higher resolution for better OCR
                            pil_image = bitmap.to_pil()
                            
                            # Use EasyOCR for better text extraction
                            if 'easyocr' in sys.modules:
                                reader = easyocr.Reader(['en'])
                                ocr_result = reader.readtext(np.array(pil_image))
                                
                                # Combine OCR results
                                ocr_text = " ".join([item[1] for item in ocr_result if item[2] > 0.5])  # Only high confidence
                                if len(ocr_text) > len(text):
                                    text = ocr_text
                        except Exception as ocr_error:
                            st.warning(f"OCR failed for page {page_num + 1}: {str(ocr_error)}")
                    
                    all_text += text + "\n"
                    textpage.close()
                    page.close()
                
                pdf.close()
                
                # Additional cleaning for PDF extracted text
                all_text = clean_pdf_text(all_text)
                
                return extract_questions_from_text(all_text, file_name)
                
            except Exception as e:
                st.error(f"Error processing PDF {file_name}: {e}")
                return []

        def has_too_much_gibberish(text):
            """Check if text has too much gibberish content"""
            if len(text) < 10:
                return True
            
            # Count special characters and numbers vs letters
            special_count = len(re.findall(r'[^\w\s]', text))
            letter_count = len(re.findall(r'[A-Za-z]', text))
            
            if letter_count == 0:
                return True
            
            # If more than 40% special characters, likely gibberish
            if special_count / len(text) > 0.4:
                return True
            
            return False

        def clean_pdf_text(text):
            """Additional cleaning specifically for PDF extracted text"""
            # Remove common PDF extraction artifacts
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
            text = re.sub(r'\s*\|\s*', ' ', text)  # Remove table separators
            text = re.sub(r'_{3,}', ' ', text)  # Remove long underscores
            text = re.sub(r'-{3,}', ' ', text)  # Remove long dashes
            text = re.sub(r'\.{3,}', ' ', text)  # Remove long dots
            
            # Remove page numbers and headers/footers
            text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\b\d+\s*/\s*\d+\b', '', text)  # Page numbers like 1/10
            
            # Remove common exam paper artifacts
            text = re.sub(r'Roll\s*No[^\n]*\n?', '', text, flags=re.IGNORECASE)
            text = re.sub(r'Name[^\n]*\n?', '', text, flags=re.IGNORECASE)
            text = re.sub(r'Signature[^\n]*\n?', '', text, flags=re.IGNORECASE)
            
            return text
        
        def generate_realistic_question(subject, topic, question_type, difficulty):
            """Generate more realistic and subject-specific questions using MPPSCQuestionGenerator"""
            
            if QGEN_SUPPORT:
                try:
                    # Use the actual MPPSCQuestionGenerator
                    generator = MPPSCQuestionGenerator(offline_mode=True)  # Use offline mode for faster response
                    
                    # Generate a single question using the available method
                    generated_questions = generator.generate_subject_wise_questions(subject, num_questions=1)
                    
                    if generated_questions:
                        return generated_questions[0].get('question', f"Discuss the importance of {topic} in {subject.replace('_', ' ')}.")
                    
                except Exception as e:
                    # Fallback to static templates if generation fails
                    print(f"Question generation error: {e}")
            
            # Fallback: Subject-specific question templates
            templates = {
                'madhya_pradesh_gk': [
                    f"What is the historical significance of {topic} in Madhya Pradesh?",
                    f"Discuss the role of {topic} in the development of Madhya Pradesh.",
                    f"Which district of Madhya Pradesh is famous for {topic}?",
                    f"What are the key features of {topic} in Madhya Pradesh?",
                    f"How does {topic} contribute to Madhya Pradesh's cultural heritage?",
                ],
                'indian_polity': [
                    f"Explain the constitutional provisions related to {topic}.",
                    f"What is the role of {topic} in Indian democratic system?",
                    f"Discuss the powers and functions of {topic}.",
                    f"How does {topic} ensure checks and balances in Indian polity?",
                    f"What are the key amendments related to {topic}?",
                ],
                'indian_economy': [
                    f"Analyze the impact of {topic} on Indian economic growth.",
                    f"What are the challenges and opportunities in {topic}?",
                    f"Discuss the government policies related to {topic}.",
                    f"How does {topic} affect income distribution in India?",
                    f"What is the role of {topic} in sustainable development?",
                ],
                'indian_history': [
                    f"Discuss the historical importance of {topic} in Indian history.",
                    f"What were the major achievements during {topic}?",
                    f"How did {topic} influence Indian society and culture?",
                    f"What were the causes and consequences of {topic}?",
                    f"Compare {topic} with contemporary developments.",
                ],
                'indian_geography': [
                    f"Explain the geographical significance of {topic}.",
                    f"What are the climatic conditions associated with {topic}?",
                    f"How does {topic} affect the agricultural pattern of the region?",
                    f"Discuss the economic importance of {topic}.",
                    f"What are the environmental challenges related to {topic}?",
                ],
                'general_science': [
                    f"Explain the scientific principles behind {topic}.",
                    f"What are the applications of {topic} in daily life?",
                    f"Discuss the recent developments in {topic}.",
                    f"How does {topic} impact human health and environment?",
                    f"What are the ethical considerations in {topic}?",
                ],
                'current_affairs': [
                    f"Analyze the recent developments in {topic}.",
                    f"What is the significance of {topic} in current context?",
                    f"Discuss the implications of {topic} for India.",
                    f"How does {topic} affect India's international relations?",
                    f"What are the challenges and opportunities in {topic}?",
                ]
            }
            
            # Get templates for the subject
            subject_templates = templates.get(subject, templates['indian_polity'])
            base_question = random.choice(subject_templates)
            
            if question_type == "Short Answer":
                short_starters = [
                    "Briefly explain",
                    "What do you understand by",
                    "Define",
                    "State the main features of",
                    "Write a short note on"
                ]
                starter = random.choice(short_starters)
                base_question = f"{starter} {topic}."
                
            elif question_type == "Long Answer":
                long_starters = [
                    "Critically analyze",
                    "Discuss in detail",
                    "Examine the role of",
                    "Evaluate the significance of",
                    "Elaborate on the importance of"
                ]
                starter = random.choice(long_starters)
                base_question = f"{starter} {topic} in the Indian context."
            
            return base_question
        
        # Add CSS for question generator
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .question-card {
            background: var(--card-background, white);
            border: 1px solid var(--border-color, #e0e0e0);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: var(--text-color, #333);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>MPPSC Question Generator</h1>
            <p>Generate customized questions for Madhya Pradesh Public Service Commission</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize session state for question generator
        if 'qgen_questions' not in st.session_state:
            st.session_state.qgen_questions = []
        if 'qgen_topics' not in st.session_state:
            st.session_state.qgen_topics = {}
        
        # Tabs for different functionalities
        tab1, tab2, tab3 = st.tabs(["Configure Topics", "Extract from Files", "Generate Questions"])
        
        with tab1:
            st.header("Configure Your Topics")
            
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
            
            # Default topics
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
            
            # Create topic configuration interface
            user_topics = st.session_state.qgen_topics.copy() if st.session_state.qgen_topics else {}
            
            for subject in subjects:
                with st.expander(f"{subject.replace('_', ' ').title()}", expanded=False):
                    use_default = st.checkbox(f"Use default topics", 
                                            value=True, 
                                            key=f"default_{subject}")
                    
                    if use_default:
                        user_topics[subject] = default_curriculum.get(subject, [])
                        st.success(f"Using {len(default_curriculum.get(subject, []))} default topics")
                        
                        # Show default topics
                        if st.checkbox(f"Show topics", key=f"show_{subject}"):
                            for topic in default_curriculum.get(subject, []):
                                st.write(f"• {topic}")
                    else:
                        # Custom topic input
                        st.write("Enter your custom topics (one per line):")
                        existing_text = '\n'.join(user_topics.get(subject, []))
                        
                        custom_topics_text = st.text_area(
                            f"Topics for {subject.replace('_', ' ')}",
                            value=existing_text,
                            height=150,
                            key=f"custom_{subject}"
                        )
                        
                        if custom_topics_text:
                            custom_topics = [topic.strip() for topic in custom_topics_text.split('\n') if topic.strip()]
                            user_topics[subject] = custom_topics
                            st.success(f"Added {len(custom_topics)} custom topics")
                        else:
                            user_topics[subject] = []
            
            st.session_state.qgen_topics = user_topics
            
            if st.button("Save Topic Configuration"):
                st.success("Topics configuration saved!")
        
        with tab2:
            st.header("Extract Questions from Files")
            
            if not PDF_SUPPORT:
                st.warning("PDF support not available. Please install pypdfium2, easyocr, and numpy for full functionality.")
            
            # File upload
            uploaded_files = st.file_uploader(
                "Upload PDF or text files containing questions",
                type=['pdf', 'txt'] if PDF_SUPPORT else ['txt'],
                accept_multiple_files=True,
                key="qgen_files"
            )
            
            if uploaded_files:
                if st.button("Extract Questions"):
                    extracted_questions = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        try:
                            if uploaded_file.name.endswith('.txt'):
                                content = str(uploaded_file.read(), "utf-8")
                                questions = extract_questions_from_text(content, uploaded_file.name)
                            elif uploaded_file.name.endswith('.pdf') and PDF_SUPPORT:
                                # Basic PDF text extraction
                                content = uploaded_file.read()
                                questions = extract_questions_from_pdf(content, uploaded_file.name)
                            else:
                                st.warning(f"Unsupported file type: {uploaded_file.name}")
                                continue
                            
                            extracted_questions.extend(questions)
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.text("Extraction complete!")
                    
                    if extracted_questions:
                        st.session_state.qgen_questions.extend(extracted_questions)
                        st.success(f"Extracted {len(extracted_questions)} questions!")
                        
                        # Preview
                        with st.expander("Preview Extracted Questions"):
                            for i, q in enumerate(extracted_questions[:5], 1):
                                st.markdown(f"""
                                <div class="question-card">
                                    <strong>Q{i}:</strong> {q['question']}<br>
                                    <small><strong>Subject:</strong> {q['subject']} | <strong>Topic:</strong> {q['topic']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No questions could be extracted from the uploaded files.")
        
        with tab3:
            st.header("Generate Questions")
            
            # Generation parameters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                num_questions = st.number_input("Number of questions", min_value=1, max_value=50, value=10)
            
            with col2:
                question_type = st.selectbox("Question type", [ "Short Answer", "Long Answer", "Mixed"])
            
            with col3:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
            
            # Subject selection
            if st.session_state.qgen_topics:
                selected_subjects = st.multiselect(
                    "Select subjects",
                    list(st.session_state.qgen_topics.keys()),
                    default=list(st.session_state.qgen_topics.keys())[:3]
                )
            else:
                st.warning("Please configure topics first in the Configure Topics tab.")
                selected_subjects = []
            
            if st.button("Generate Questions") and selected_subjects:
                with st.spinner("Generating questions..."):
                    generated_questions = []
                    
                    for i in range(num_questions):
                        subject = random.choice(selected_subjects)
                        topics = st.session_state.qgen_topics.get(subject, [])
                        
                        if topics:
                            topic = random.choice(topics)
                            
                            # Enhanced question generation with more realistic templates
                            question_text = generate_realistic_question(subject, topic, question_type, difficulty)
                            
                            generated_questions.append({
                                'question': question_text,
                                'subject': subject,
                                'topic': topic,
                                'type': question_type if question_type != "Mixed" else random.choice(["Short Answer", "Long Answer"]),
                                'difficulty': difficulty if difficulty != "Mixed" else random.choice(["Easy", "Medium", "Hard"]),
                                'source': 'AI Generated',
                                'year': datetime.now().year
                            })
                    
                    st.session_state.qgen_questions.extend(generated_questions)
                    st.success(f"Generated {len(generated_questions)} questions!")
            
            # Display all questions
            if st.session_state.qgen_questions:
                st.divider()
                st.subheader(f"Question Bank ({len(st.session_state.qgen_questions)} questions)")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_subject = st.selectbox(
                        "Filter by subject",
                        ["All"] + list(set(q['subject'] for q in st.session_state.qgen_questions))
                    )
                with col2:
                    filter_type = st.selectbox(
                        "Filter by type",
                        ["All"] + list(set(q['type'] for q in st.session_state.qgen_questions))
                    )
                with col3:
                    show_count = st.slider("Questions to show", 5, min(30, len(st.session_state.qgen_questions)), 10)
                
                # Filter questions
                filtered_questions = st.session_state.qgen_questions
                if filter_subject != "All":
                    filtered_questions = [q for q in filtered_questions if q['subject'] == filter_subject]
                if filter_type != "All":
                    filtered_questions = [q for q in filtered_questions if q['type'] == filter_type]
                
                # Display questions
                for i, q in enumerate(filtered_questions[:show_count], 1):
                    st.markdown(f"""
                    <div class="question-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0;">Q{i}</h4>
                            <div>
                                <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px;">
                                    {q['subject'].replace('_', ' ').title()}
                                </span>
                                <span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                    {q['type']}
                                </span>
                            </div>
                        </div>
                        <p><strong>Topic:</strong> {q['topic']}</p>
                        <p style="margin: 0; line-height: 1.6; font-size: 1.1em;">{q['question']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Download options
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Clear All Questions"):
                        st.session_state.qgen_questions = []
                        st.success("All questions cleared!")
                        st.rerun()
                
                with col2:
                    # Download CSV
                    df = pd.DataFrame(st.session_state.qgen_questions)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"mppsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    # Download options for question papers
                    col3a, col3b = st.columns(2)
                    
                    with col3a:
                        # Create text question paper
                        paper_text = create_question_paper(st.session_state.qgen_questions)
                        
                        st.download_button(
                            label="Download TXT",
                            data=paper_text,
                            file_name=f"mppsc_question_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    
                    with col3b:
                        # Create PDF question paper
                        if st.button("Generate PDF"):
                            with st.spinner("Generating PDF..."):
                                pdf_bytes = create_mppsc_pdf_question_paper(st.session_state.qgen_questions)
                                
                                if pdf_bytes:
                                    st.download_button(
                                        label="Download PDF",
                                        data=pdf_bytes,
                                        file_name=f"mppsc_question_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                        mime="application/pdf"
                                    )

elif st.session_state.selected_page == "grammar":
    st.subheader("Grammar Checker")
    st.write("Check and correct grammar in your answers using advanced AI-powered tools.")
    
    # Import grammar checker functions
    import sys
    import os
    
    # Add SSDigimark to Python path
    ssdigimark_path = os.path.join(os.path.dirname(__file__), 'SSDigimark-master')
    if ssdigimark_path not in sys.path:
        sys.path.insert(0, ssdigimark_path)
    
    try:
        from checker import process_text
        from grammar_checker import check_grammar, correct_text
        from scorer import get_grammar_score
    except ImportError as e:
        st.error(f"Error loading grammar checker modules: {e}")
        st.stop()
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Text Input", "File Upload", "Handwriting Extraction"])
    
    with tab1:
        st.markdown("### Enter text to check grammar:")
        
        # Direct text input without samples
        user_text = st.text_area("Enter your text here:", height=150, placeholder="Type or paste your text here...")
        
        # Full width buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            check_grammar = st.button("Check Grammar", use_container_width=True, type="primary")
        with col_btn2:
            quick_correct = st.button("Quick Correct", use_container_width=True)
        
        # Process detailed grammar check
        if check_grammar:
            if user_text.strip():
                with st.spinner("Analyzing grammar..."):
                    try:
                        # Use the updated grammar checker
                        result = process_text(user_text)
                        
                        # Display results in full width
                        st.markdown("### Analysis Results")
                        
                        # Metrics in full width
                        col_score, col_remark, col_issues = st.columns(3)
                        with col_score:
                            st.metric("Grammar Score", f"{result.get('score', 0)}%")
                        with col_remark:
                            st.metric("Assessment", result.get('remark', 'Unknown'))
                        with col_issues:
                            st.metric("Issues Found", len(result.get('errors', [])))
                        
                        # Full width text areas
                        st.markdown("### Original Text")
                        st.text_area("Original:", value=result.get('original', user_text), height=100, disabled=True, key="original_check")
                        
                        st.markdown("### Corrected Text")
                        st.text_area("Corrected:", value=result.get('corrected', user_text), height=100, disabled=True, key="corrected_check")
                        
                        # Consolidated issues display in full width
                        if result.get('errors'):
                            st.markdown("### Grammar Issues Analysis")
                            issues_text = ""
                            for i, error in enumerate(result['errors'], 1):
                                issue_detail = error.get('highlighted', 'Grammar issue detected')
                                issues_text += f"Issue {i}: {issue_detail}\n\n"
                            
                            st.text_area(
                                "All Issues Found:",
                                value=issues_text.strip(),
                                height=150,
                                disabled=True,
                                key="issues_check"
                            )
                        else:
                            st.success("No grammar issues found!")
                            
                    except Exception as e:
                        st.error(f"Error during grammar analysis: {str(e)}")
            else:
                st.warning("Please enter some text to analyze.")
        
        # Process quick correction
        if quick_correct:
            if user_text.strip():
                with st.spinner("Correcting text..."):
                    try:
                        corrected = correct_text(user_text)
                        st.markdown("### Quick Correction")
                        st.text_area("Corrected text:", value=corrected, height=150, key="quick_corrected")
                        
                        # Copy button simulation
                        st.code(corrected, language=None)
                        st.info("You can copy the corrected text from the code box above")
                        
                    except Exception as e:
                        st.error(f"Error during correction: {str(e)}")
            else:
                st.warning("Please enter some text to correct.")
    
    with tab2:
        st.markdown("### Upload a text file for grammar checking:")
        
        uploaded_file = st.file_uploader("Choose a text file", type=['txt', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "text/plain":
                    # Handle text file
                    content = str(uploaded_file.read(), "utf-8")
                    st.text_area("File content:", value=content, height=200, disabled=True)
                    
                    if st.button("Analyze File Content", type="primary"):
                        with st.spinner("Processing file..."):
                            result = process_text(content)
                            
                            # Display results
                            col_score, col_remark = st.columns(2)
                            with col_score:
                                st.metric("Overall Score", f"{result.get('score', 0)}%")
                            with col_remark:
                                st.metric("Assessment", result.get('remark', 'Unknown'))
                            
                            # Download corrected version
                            corrected_content = result.get('corrected', content)
                            st.download_button(
                                label="Download Corrected File",
                                data=corrected_content,
                                file_name=f"corrected_{uploaded_file.name}",
                                mime="text/plain"
                            )
                
                elif uploaded_file.name.endswith('.csv'):
                    # Handle CSV file
                    try:
                        from csv_mode import process_csv
                        df = pd.read_csv(uploaded_file)
                        st.dataframe(df.head())
                        
                        if st.button("Process CSV File", type="primary"):
                            with st.spinner("Processing CSV..."):
                                # Process CSV with grammar checking
                                result_df = process_csv(uploaded_file)
                                st.dataframe(result_df)
                                
                                # Download processed CSV
                                csv_buffer = io.StringIO()
                                result_df.to_csv(csv_buffer, index=False)
                                st.download_button(
                                    label="Download Processed CSV",
                                    data=csv_buffer.getvalue(),
                                    file_name=f"processed_{uploaded_file.name}",
                                    mime="text/csv"
                                )
                    except Exception as e:
                        st.error(f"Error processing CSV: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab3:
        st.markdown("### Extract text from handwritten images:")
        
        # Import OCR function
        try:
            import sys
            import os
            ocr_path = os.path.join(os.path.dirname(__file__), 'SSDigimark-master', 'utils')
            if ocr_path not in sys.path:
                sys.path.insert(0, ocr_path)
            from ocr_reader import extract_text_from_image
            
            uploaded_image = st.file_uploader(
                "Choose an image file containing handwritten text", 
                type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
                key="handwriting_image"
            )
            
            if uploaded_image is not None:
                # Display the uploaded image
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Extract Text", type="primary"):
                        with st.spinner("Extracting text from image..."):
                            try:
                                # Save uploaded file temporarily
                                import tempfile
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                                    tmp_file.write(uploaded_image.getvalue())
                                    tmp_path = tmp_file.name
                                
                                # Extract text using Watson OCR
                                extracted_text = extract_text_from_image(tmp_path)
                                
                                # Clean up temporary file
                                os.unlink(tmp_path)
                                
                                if extracted_text:
                                    st.markdown("### Extracted Text")
                                    st.text_area(
                                        "Text extracted from image:", 
                                        value=extracted_text, 
                                        height=150, 
                                        key="extracted_text_display"
                                    )
                                    
                                    # Store extracted text in session state for further processing
                                    st.session_state['extracted_handwriting'] = extracted_text
                                    
                                else:
                                    st.warning("No text could be extracted from the image. Please ensure the image contains clear, readable text.")
                                
                            except Exception as e:
                                st.error(f"Error during text extraction: {str(e)}")
                
                with col2:
                    if st.button("Extract & Check Grammar"):
                        with st.spinner("Extracting text and checking grammar..."):
                            try:
                                # Save uploaded file temporarily
                                import tempfile
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                                    tmp_file.write(uploaded_image.getvalue())
                                    tmp_path = tmp_file.name
                                
                                # Extract text using Watson OCR
                                extracted_text = extract_text_from_image(tmp_path)
                                
                                # Clean up temporary file
                                os.unlink(tmp_path)
                                
                                if extracted_text:
                                    # Process the extracted text for grammar checking
                                    result = process_text(extracted_text)
                                    
                                    # Display results in full width
                                    st.markdown("### Extraction & Grammar Analysis Results")
                                    
                                    # Metrics in full width
                                    col_score, col_remark, col_issues = st.columns(3)
                                    with col_score:
                                        st.metric("Grammar Score", f"{result.get('score', 0)}%")
                                    with col_remark:
                                        st.metric("Assessment", result.get('remark', 'Unknown'))
                                    with col_issues:
                                        st.metric("Issues Found", len(result.get('errors', [])))
                                    
                                    # Full width text areas
                                    st.markdown("### Original Extracted Text")
                                    st.text_area("Extracted:", value=result.get('original', extracted_text), height=100, disabled=True, key="original_extracted")
                                    
                                    st.markdown("### Corrected Text")
                                    st.text_area("Corrected:", value=result.get('corrected', extracted_text), height=100, disabled=True, key="corrected_extracted")
                                    
                                    # Consolidated issues display in full width
                                    if result.get('errors'):
                                        st.markdown("### Grammar Issues Analysis")
                                        issues_text = ""
                                        for i, error in enumerate(result['errors'], 1):
                                            issue_detail = error.get('highlighted', 'Grammar issue detected')
                                            issues_text += f"Issue {i}: {issue_detail}\n\n"
                                        
                                        st.text_area(
                                            "All Issues Found:",
                                            value=issues_text.strip(),
                                            height=150,
                                            disabled=True,
                                            key="issues_extracted"
                                        )
                                    else:
                                        st.success("No grammar issues found in extracted text!")
                                
                                else:
                                    st.warning("No text could be extracted from the image. Please ensure the image contains clear, readable text.")
                                
                            except Exception as e:
                                st.error(f"Error during extraction and grammar analysis: {str(e)}")
                
                # Tips for better OCR results
                st.markdown("### Tips for Better Text Extraction:")
                st.info("""
                **For optimal results:**
                - Use high-resolution images (at least 300 DPI)
                - Ensure good lighting and contrast
                - Keep the image straight and well-focused
                - Use clear, legible handwriting
                - Avoid shadows or glare on the paper
                - For best accuracy, write in block letters when possible
                """)
        
        except ImportError as e:
            st.error(f"OCR functionality not available: {e}")
            st.info("Please ensure all required dependencies are installed: pip install easyocr python-dotenv")
    
    # Information section
    with st.expander("About the Grammar Checker"):
        st.markdown("""
        **Features:**
        - **AI-Powered:** Uses IBM Watsonx AI with Llama model for intelligent corrections
        - **Fallback System:** Automatically falls back to LanguageTool API if needed
        - **Scoring:** Provides detailed grammar scores and assessments
        - **Context-Aware:** Understands context for better corrections
        - **Multiple Formats:** Supports text files and CSV processing
        
        **Setup:**
        - For best results, configure IBM API keys (see IBM_SETUP_GUIDE.md)
        - Without IBM keys, the system uses LanguageTool API as fallback
        
        **Tip:** The system works best with complete sentences and paragraphs.
        """)

# Footer
st.markdown("---")
st.markdown("**MPPSC Services Platform** - Powered by Advanced AI Technology")
st.markdown("For support and feature requests, please refer to the documentation.")