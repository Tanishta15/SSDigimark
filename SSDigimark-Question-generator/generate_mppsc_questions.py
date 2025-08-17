import os
import pandas as pd
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    pipeline
)
from typing import List, Dict
import re
import random

# Set Hugging Face cache directory to D drive BEFORE importing transformers
os.environ['HF_HOME'] = 'D:/huggingface_cache'
os.environ['HF_HUB_CACHE'] = 'D:/huggingface_cache/hub'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
if 'HF_TOKEN' in os.environ:
    del os.environ['HF_TOKEN']

class MPPSCQuestionGenerator:
    def __init__(self, model_name: str = "google/flan-t5-small", offline_mode: bool = False, custom_topics: Dict[str, List[str]] = None):
        self.model_name = model_name
        self.offline_mode = offline_mode
        self.tokenizer = None
        self.model = None
        self.generator = None
        self.custom_topics = custom_topics
        self.mppsc_topics = self._load_mppsc_curriculum()
        self.question_templates = self._load_question_templates()
        if not offline_mode:
            self.setup_model()
        else:
            print("Running in offline mode - AI generation disabled, using template-based questions only")
    
    def _load_mppsc_curriculum(self) -> Dict[str, List[str]]:
        """Load MPPSC-specific topics by subject - supports custom topics"""
        # If custom topics are provided, use them
        if self.custom_topics:
            return self.custom_topics
            
        # Default topics if no custom topics provided
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
                'Scientific Research', 'Science and Technology Policy'
            ],
            'current_affairs': [
                'Government Schemes', 'Policy Initiatives', 'National Events', 'International Events',
                'Sports', 'Awards', 'Important Personalities', 'Books and Authors',
                'Science and Technology News', 'Economic Developments', 'Political Developments'
            ]
        }
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """Load question templates for different categories"""
        return {
            'madhya_pradesh_specific': [
                "What is the significance of {} in Madhya Pradesh's history?",
                "Explain the role of {} in Madhya Pradesh's development.",
                "Describe the importance of {} for Madhya Pradesh.",
                "Write about the contribution of {} to Madhya Pradesh's culture."
            ],
            'analytical': [
                "Analyze the impact of {} on Madhya Pradesh's development.",
                "Evaluate the significance of {} in Indian context.",
                "How does {} contribute to Madhya Pradesh's economy?",
                "What are the challenges related to {} in Madhya Pradesh?"
            ],
            'application': [
                "What measures can be taken to strengthen {} in Madhya Pradesh?",
                "How can {} be improved to address current challenges?",
                "What reforms are needed in {} to make it more effective?",
                "What steps should the government take to promote {}?"
            ],
            'descriptive': [
                "Discuss the historical development of {} in Madhya Pradesh.",
                "Elaborate on the role of {} in modern Madhya Pradesh.",
                "Explain the significance of {} with examples.",
                "Write a detailed note on {} and its importance."
            ]
        }
    
    def setup_model(self):
        """Initialize the FLAN-T5 model"""
        if self.offline_mode:
            print("Offline mode enabled - skipping model loading")
            return
            
        print(f"Loading {self.model_name} for MPPSC question generation...")
        
        cache_dir = "D:/huggingface_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
                token=False,
                local_files_only=True  # Try local first
            )
            
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                token=False,
                local_files_only=True  # Try local first
            )
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(device)
            print(f"Device set to use {device}")
            
            self.generator = pipeline(
                "text2text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                max_length=150,
                do_sample=True,
                temperature=0.7
            )
            
            print("MPPSC question generator loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load model: {e}")
            print("Falling back to offline mode with template-based questions only")
            self.offline_mode = True
            self.tokenizer = None
            self.model = None
            self.generator = None
    
    def generate_subject_wise_questions(self, subject: str, num_questions: int = 8) -> List[Dict]:
        """Generate template-based questions for a subject"""
        
        if subject not in self.mppsc_topics:
            return []
        
        topics = self.mppsc_topics[subject]
        questions = []
        
        # Generate questions using templates
        template_categories = list(self.question_templates.keys())
        
        for i in range(num_questions):
            topic = random.choice(topics)
            template_category = random.choice(template_categories)
            template = random.choice(self.question_templates[template_category])
            
            # Format question with topics
            if '{}' in template:
                if template.count('{}') == 1:
                    question_text = template.format(topic)
                elif template.count('{}') == 2:
                    topic2 = random.choice([t for t in topics if t != topic])
                    question_text = template.format(topic, topic2)
                else:
                    related_topics = random.sample(topics, min(template.count('{}'), len(topics)))
                    question_text = template.format(*related_topics)
            else:
                question_text = template
            
            questions.append({
                'question': question_text,
                'subject': subject,
                'topic': topic,
                'type': template_category,
                'difficulty': 'moderate'
            })
        
        return questions
    
    def generate_ai_enhanced_questions(self, subject: str, num_questions: int = 5) -> List[Dict]:
        """Generate AI-enhanced questions for better contextual coverage"""
        
        if self.offline_mode or self.generator is None:
            print(f"AI generation skipped for {subject} (offline mode)")
            return self._generate_fallback_questions(subject, num_questions)
        
        if subject not in self.mppsc_topics:
            return []
        
        questions = []
        topics = self.mppsc_topics[subject]
        
        for i in range(num_questions):
            topic = random.choice(topics)
            
            # Create prompts for different question types
            prompts = [
                f"Generate a descriptive question about {topic} for MPPSC examination in Madhya Pradesh.",
                f"Create a question about {topic} relevant to Madhya Pradesh Public Service Commission exam.",
                f"Write an analytical question on {topic} focusing on Madhya Pradesh context."
            ]
            
            prompt = random.choice(prompts)
            
            try:
                # Generate using AI
                result = self.generator(prompt, max_length=100, num_return_sequences=1)
                ai_question = result[0]['generated_text'].strip()
                
                # Clean and format the question
                if ai_question and len(ai_question) > 10:
                    questions.append({
                        'question': ai_question,
                        'subject': subject,
                        'topic': 'ai_generated',
                        'type': 'ai_enhanced',
                        'difficulty': 'moderate'
                    })
                    
            except Exception as e:
                print(f"AI generation failed for {topic}: {e}")
                continue
        
        return questions
    
    def _generate_fallback_questions(self, subject: str, num_questions: int) -> List[Dict]:
        """Generate fallback questions when AI is not available"""
        if subject not in self.mppsc_topics:
            return []
        
        questions = []
        topics = self.mppsc_topics[subject]
        
        # Enhanced templates for offline mode
        offline_templates = [
            "What is the historical significance of {} in Madhya Pradesh?",
            "Explain the role of {} in Madhya Pradesh's development.",
            "Describe the importance of {} for the state of Madhya Pradesh.",
            "Discuss the contribution of {} to Madhya Pradesh's heritage.",
            "Analyze the impact of {} on Madhya Pradesh's progress."
        ]
        
        for i in range(num_questions):
            topic = random.choice(topics)
            template = random.choice(offline_templates)
            
            question_text = template.format(topic)
            
            questions.append({
                'question': question_text,
                'subject': subject,
                'topic': topic,
                'type': 'template_enhanced',
                'difficulty': 'moderate'
            })
        
        return questions
    
    def create_comprehensive_question_paper(self, output_dir: str = ".") -> pd.DataFrame:
        """Create a comprehensive MPPSC question paper in one file"""
        
        print("Creating comprehensive MPPSC question bank...")
        
        all_questions = []
        
        # Generate questions for each subject
        for subject in self.mppsc_topics.keys():
            print(f"Generating questions for {subject}...")
            
            # Template-based questions (high quality, guaranteed)
            template_questions = self.generate_subject_wise_questions(subject, 8)
            
            # AI-enhanced questions (contextual) or fallback questions
            if self.offline_mode:
                ai_questions = self.generate_ai_enhanced_questions(subject, 5)  # Will use fallback
            else:
                ai_questions = self.generate_ai_enhanced_questions(subject, 3)
            
            # Combine questions
            subject_questions = template_questions + ai_questions
            all_questions.extend(subject_questions)
            print(f"Generated {len(subject_questions)} questions for {subject}")
        
        # Create single comprehensive question bank
        master_df = pd.DataFrame(all_questions)
        master_df['id'] = range(1, len(all_questions) + 1)
        master_df['source'] = 'mppsc_generator'
        master_df['year'] = '2025'
        
        # Reorder columns for better readability
        column_order = ['id', 'question', 'subject', 'topic', 'type', 'difficulty', 'source', 'year']
        master_df = master_df[column_order]
        
        # Save to single file
        master_file = os.path.join(output_dir, "mppsc_comprehensive_question_bank.csv")
        master_df.to_csv(master_file, index=False, encoding='utf-8')
        
        # Create sample question paper
        sample_paper = self.create_sample_question_paper(all_questions)
        sample_file = os.path.join(output_dir, "mppsc_sample_question_paper.txt")
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_paper)
        
        print(f"\n=== MPPSC Comprehensive Question Bank Created ===")
        print(f"Total questions generated: {len(all_questions)}")
        print(f"Single file: {master_file}")
        print(f"Sample paper: {sample_file}")
        
        # Print subject breakdown
        subject_counts = master_df['subject'].value_counts()
        print(f"\nQuestion breakdown by subject:")
        for subject, count in subject_counts.items():
            print(f"  {subject.replace('_', ' ').title()}: {count} questions")
        
        return master_df
    
    def create_sample_question_paper(self, all_questions: List[Dict]) -> str:
        """Create a formatted sample question paper"""
        
        df = pd.DataFrame(all_questions)
        
        paper = """MPPSC Practice Question Paper
===============================

Subject: Madhya Pradesh Public Service Commission
Time: 2 Hours                    Max Marks: 100
Instructions: Answer all questions. Write detailed answers with examples.

"""
        
        # Select questions for the paper
        question_num = 1
        for i, subject in enumerate(['madhya_pradesh_gk', 'current_affairs', 'indian_history', 'indian_geography', 'indian_polity']):
            if subject in df['subject'].values:
                subject_questions = df[df['subject'] == subject].head(3)  # 3 questions per subject
                
                paper += f"\nSection {i+1}: {subject.replace('_', ' ').title()}\n"
                paper += "-" * 40 + "\n"
                
                for idx, row in subject_questions.iterrows():
                    paper += f"\n{question_num}. {row['question']}\n"
                    paper += f"   Difficulty: {row['difficulty']} | Type: {row['type']}\n"
                    question_num += 1
        
        paper += "\n\n" + "="*50 + "\n"
        paper += "Note: These are descriptive questions requiring detailed answers.\n"
        paper += "Generated by MPPSC Question Generator\n"
        
        return paper

def main():
    """Main function to create MPPSC question bank"""
    
    generator = MPPSCQuestionGenerator()
    
    print("Creating MPPSC comprehensive question bank...")
    
    # Generate comprehensive question bank
    result_df = generator.create_comprehensive_question_paper()
    
    print("\n=== MPPSC Question Generation Complete ===")
    print(f"Total questions: {len(result_df)}")
    print("All questions saved in: mppsc_comprehensive_question_bank.csv")
    
    # Show sample questions from different subjects
    print("\n=== Sample MPPSC Questions ===")
    for subject in result_df['subject'].unique()[:3]:
        sample_q = result_df[result_df['subject'] == subject].iloc[0]
        print(f"\n{subject.upper().replace('_', ' ')}:")
        print(f"Q: {sample_q['question'][:100]}...")
        print(f"Type: {sample_q['type']}")

if __name__ == "__main__":
    main()
