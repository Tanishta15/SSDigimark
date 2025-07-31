"""
Convert MPPSC Question Bank to PDF using reportlab
"""

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import csv
    import os
    
    print("Creating PDF using reportlab...")
    
    # Define file paths
    csv_file = r"d:\internship\Digimark\question paper prediction model\mppsc_comprehensive_question_bank.csv"
    sample_file = r"d:\internship\Digimark\question paper prediction model\mppsc_sample_question_paper.txt"
    pdf_file = r"d:\internship\Digimark\question paper prediction model\MPPSC_Question_Bank_and_Sample_Paper.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, 
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
    
    # Add title
    story.append(Paragraph("MPPSC Comprehensive Question Bank", title_style))
    story.append(Paragraph("Madhya Pradesh Public Service Commission", styles['Heading3']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Total Questions: 91 | Generated: 2025", styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Read CSV and organize by subject
    questions_by_subject = {}
    
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                subject = row['subject']
                if subject not in questions_by_subject:
                    questions_by_subject[subject] = []
                questions_by_subject[subject].append(row)
    
    # Add questions by subject
    for subject, questions in questions_by_subject.items():
        # Add section header
        subject_title = subject.replace('_', ' ').title()
        story.append(Paragraph(subject_title, section_style))
        
        for q in questions:
            question_text = f"Q{q['id']}. {q['question']}"
            
            # Clean up the question text
            question_text = question_text.replace('\n', '<br/>')
            
            story.append(Paragraph(question_text, question_style))
            
            # Add metadata
            meta_text = f"Topic: {q['topic']} | Type: {q['type']} | Difficulty: {q['difficulty']}"
            story.append(Paragraph(f"<i>{meta_text}</i>", styles['Normal']))
            story.append(Spacer(1, 6))
    
    # Add sample paper
    story.append(PageBreak())
    story.append(Paragraph("MPPSC Practice Question Paper", title_style))
    
    if os.path.exists(sample_file):
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_content = f.read()
            
        # Split into paragraphs and add to story
        paragraphs = sample_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Check if it's a section header
                if para.startswith('Section'):
                    story.append(Paragraph(para, section_style))
                elif para.startswith('MPPSC') or para.startswith('Subject:') or para.startswith('Time:'):
                    story.append(Paragraph(para, styles['Heading3']))
                else:
                    story.append(Paragraph(para.replace('\n', '<br/>'), styles['Normal']))
                story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    print(f"PDF successfully created: {pdf_file}")
    
except ImportError:
    print("reportlab is not installed. Installing it now...")
    import subprocess
    import sys
    
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    
    # Re-run the script after installation
    exec(open(__file__).read())
    
except Exception as e:
    print(f"Error creating PDF: {e}")
    print("Falling back to simple text-based approach...")
    
    # Fallback: Create a simple text file that can be easily converted
    try:
        txt_file = r"d:\internship\Digimark\question paper prediction model\MPPSC_Question_Bank_Clean.txt"
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("MPPSC COMPREHENSIVE QUESTION BANK\n")
            f.write("=" * 50 + "\n\n")
            f.write("Madhya Pradesh Public Service Commission\n")
            f.write("Total Questions: 91 | Generated: 2025\n\n")
            
            # Read and write CSV data
            if os.path.exists(csv_file):
                with open(csv_file, 'r', encoding='utf-8') as csv_f:
                    reader = csv.DictReader(csv_f)
                    current_subject = ""
                    
                    for row in reader:
                        if row['subject'] != current_subject:
                            current_subject = row['subject']
                            f.write(f"\n{current_subject.replace('_', ' ').upper()}\n")
                            f.write("-" * 40 + "\n\n")
                        
                        f.write(f"Q{row['id']}. {row['question']}\n")
                        f.write(f"Topic: {row['topic']} | Type: {row['type']} | Difficulty: {row['difficulty']}\n\n")
            
            # Add sample paper
            f.write("\n\nSAMPLE QUESTION PAPER\n")
            f.write("=" * 50 + "\n\n")
            
            if os.path.exists(sample_file):
                with open(sample_file, 'r', encoding='utf-8') as sample_f:
                    f.write(sample_f.read())
        
        print(f"Clean text file created: {txt_file}")
        print("You can open this in Word and save as PDF, or use an online text-to-PDF converter.")
        
    except Exception as e2:
        print(f"Error creating text file: {e2}")
        print("Please use the HTML file and convert it manually using your browser.")
