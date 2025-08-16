# Architecture

This minimal app bundles a Streamlit UI and a Watson OCR–powered backend. It can operate in a reduced, offline-friendly mode for question generation while still relying on online services for OCR and grammar.

## Components
- integrated_mppsc_platform.py (UI)
  - Home: overview and stats
  - Answer Sheet Evaluation: OCR + similarity scoring, CSV mode
  - Grammar & Spell: text/image modes, highlighting and corrections
  - Questions: template/AI-enhanced generator, sample paper builder
  - Analytics: illustrative charts
  - Settings: marking scheme, OCR engine (Watson), grammar options
- watson_backend.py (Backend)
  - Orchestrates OCR (via Watson), grammar checking (LanguageTool API)
  - Exposes methods used by the UI
- watson_ocr.py (OCR)
  - Wraps IBM watsonx.ai vision model `meta-llama/llama-3-2-90b-vision-instruct`
  - PDF → images (PyMuPDF), then per-page OCR via watsonx.ai
  - Aggregates and extracts answers from textual content
- SSDigimark-Question-generator/generate_mppsc_questions.py (Optional)
  - Template and optional AI-based question generation
- start_platform.py (Launcher)
  - Sets Hugging Face caches to D: and launches Streamlit
- config.py
  - Paths, temp dirs, marking defaults, and feature flags

## Data Flow (OCR and Evaluation)
1) User uploads Answer Key (PDF or image) and Answer Sheets.
2) watson_ocr converts PDFs to images; each image is fed to the vision model.
3) Extracted text is parsed into Q/A fragments.
4) The UI computes similarity between student answers and the expected answers.
5) Marks are assigned using configurable thresholds.
6) Results are presented and can be exported.

## External Dependencies
- IBM watsonx.ai (vision model)
- LanguageTool public API for grammar
- Hugging Face caches (optional for question generation)

## Storage and Temp
- Working directories under `temp/` (uploads, answer_sheets, intermediate images, exports).
- HF caches default to `D:/huggingface_cache` (edit in `start_platform.py` and UI file if needed).
