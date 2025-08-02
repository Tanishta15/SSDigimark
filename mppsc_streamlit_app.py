import streamlit as st
import pandas as pd
import os
import sys
from typing import Dict, List
import random
import io
import traceback

# Add the current directory to the path to import the question generator
sys.path.append(os.path.dirname(__file__))

# Import the modified question generator
from generate_mppsc_questions import MPPSCQuestionGenerator

# Set page config
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
    
    # CSV Upload Section
    st.subheader("📤 Upload Existing Question Bank (Optional)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a CSV file with existing questions to enhance generation",
            type=['csv'],
            help="Upload a CSV file with columns: id, question, subject, topic, type, difficulty, source, year"
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
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['question', 'subject', 'topic', 'type', 'difficulty']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                st.info("Required columns: id, question, subject, topic, type, difficulty, source, year")
            else:
                uploaded_questions = df.to_dict('records')
                st.success(f"✅ Successfully loaded {len(uploaded_questions)} questions from CSV")
                
                # Show summary of uploaded questions
                with st.expander("📊 Uploaded Questions Summary"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        subjects_in_csv = df['subject'].unique()
                        st.write("**Subjects in CSV:**")
                        for subject in subjects_in_csv:
                            count = len(df[df['subject'] == subject])
                            st.write(f"• {subject.replace('_', ' ').title()}: {count} questions")
                    
                    with col2:
                        types_in_csv = df['type'].unique()
                        st.write("**Question Types:**")
                        for qtype in types_in_csv:
                            count = len(df[df['type'] == qtype])
                            st.write(f"• {qtype}: {count} questions")
                    
                    with col3:
                        difficulties_in_csv = df['difficulty'].unique()
                        st.write("**Difficulty Levels:**")
                        for diff in difficulties_in_csv:
                            count = len(df[df['difficulty'] == diff])
                            st.write(f"• {diff}: {count} questions")
                
                # Option to use uploaded questions
                use_uploaded = st.checkbox(
                    "Include uploaded questions in generation",
                    value=True,
                    help="If checked, uploaded questions will be mixed with newly generated ones"
                )
                
                if not use_uploaded:
                    uploaded_questions = []
                
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
            st.info("Please ensure your CSV file has the correct format and encoding.")
    
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
        offline_mode = st.checkbox("Offline Mode (Template-based only)", value=True)
    
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
            ["Configure Topics", "Generate Questions", "View Questions", "Download"]
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
    
    elif page == "View Questions":
        render_questions_display()
    
    elif page == "Download":
        render_download_section()
    
    # Footer
    st.markdown("---")
    st.markdown("**MPPSC Question Generator** | Built with Streamlit | © 2025")

if __name__ == "__main__":
    main()
