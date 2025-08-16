# Usage Guide

This guide walks through the main features in the Streamlit UI.

## Start the App
- PowerShell (Windows):
```
python start_platform.py
```
Or directly:
```
streamlit run integrated_mppsc_platform.py --server.port 8502
```

Open http://localhost:8502/

## 1) Answer Sheet Evaluation
- Upload an Answer Key (PDF or image) and Answer Sheets (one or many PDFs/images).
- Choose Difficulty preset or Customize thresholds. Thresholds map similarity → marks:
  - full_marks, high_marks, mid_marks, low_marks → 100/75/50/25% of per-question marks.
- Set Total Marks per Question.
- Pick Evaluation Mode:
  - Image/PDF Processing (OCR over files using IBM watsonx.ai)
  - CSV Mode (upload answer key CSV + student answers CSV)
- Press “Start Grading Process”
- Review results, export CSV/Excel, optionally PDF report.

## 2) Grammar & Spell Check
- Text Input: paste text and run.
- Image Upload: upload an image (or PDF); OCR + grammar check.
- Results include: corrections list, highlighted markers, corrected text, and error metrics.

## 3) Question Generator
- Choose subject, difficulty, number of questions.
- Select question type (Template, Multiple Choice, AI Enhanced).
- For comprehensive sample papers, use the “Complete Sample Paper Generation” section.
- Download results as TXT, Excel; PDF via reportlab.

## 4) Analytics
- Demo charts for usage and performance.

## 5) Settings
- Marking scheme options.
- OCR engine: IBM Watson (requires `.env`).
- OCR confidence and status check.
- Grammar options (LanguageTool).
- Question generator defaults.

## Exports
- CSV/Excel via pandas (XlsxWriter engine).
- PDF via reportlab.

## Notes
- OCR and grammar checking require internet access.
- For robust AI generation, ensure HF caches are available, or the app remains in template mode.
