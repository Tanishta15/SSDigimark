# MPPSC Integrated Platform (Minimal App)

All‑in‑one Streamlit app for MPPSC preparation: answer‑sheet evaluation, grammar checking, and question generation. This minimal distribution bundles the Streamlit UI and a Watson OCR–powered backend so you can run locally on Windows.

## Highlights
- Answer Sheet Evaluation: OCR (PDF/images) → text extraction → similarity‑based scoring with configurable thresholds and CSV mode.
- Grammar & Spell Check: Text or image input, inline highlights, metrics, and corrected text.
- Question Generator: Template and optional AI‑enhanced generation, subject filters, export (TXT/Excel/PDF).
- One‑click start script and configured Hugging Face caches on D: to save C: drive space.

## Architecture (at a glance)
- `integrated_mppsc_platform.py`: Streamlit UI with tabs (Home, Answer Sheet, Grammar, Questions, Analytics, Settings).
- `watson_backend.py`: Thin backend that orchestrates OCR and grammar checks.
- `watson_ocr.py`: IBM watsonx.ai Vision model wrapper (meta-llama/llama-3-2-90b-vision-instruct) for OCR over images/PDFs.
- `SSDigimark-Question-generator/.../generate_mppsc_questions.py`: Optional generator; UI falls back to template mode if import fails.
- `start_platform.py`: Launcher that pre-sets HF caches to `D:\huggingface_cache` and boots Streamlit on port 8502.
- `config.py`: Paths and defaults (temp dirs, marking scheme, etc.).

## Requirements
- Windows 10/11 (PowerShell)
- Python 3.10–3.12 (recommended)
- Internet for: LanguageTool grammar API and IBM watsonx.ai OCR
- Disk space: Models/cache default to D:\ (customizable)

Install the Python packages listed in `requirements.txt` (see Install below). The app uses these notable services:
- IBM watsonx.ai: Vision model for OCR over images/PDF pages.
- LanguageTool public API: Grammar check for text; image grammar check first uses OCR, then LanguageTool.

## Setup

1) Create a virtual environment
- PowerShell (Windows):
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install dependencies
```powershell
pip install -r requirements.txt
```

3) Configure IBM credentials (.env)
Create a `.env` file next to this README (or copy `.env.example`) with:
```
IBM_API_KEY=your_api_key_here
IBM_SERVICE_URL=https://us-south.ml.cloud.ibm.com
IBM_PROJECT_ID=your_project_id_here
```
Notes:
- You must have an IBM Cloud project with watsonx.ai enabled and your API key scoped to that project.
- These credentials are required for OCR features (Answer Sheet evaluation and image grammar checks).

4) Ensure D: cache (optional but recommended)
- By default, the launcher and app set the following env vars to use D: for models/cache:
	- `HF_HOME=D:/huggingface_cache`
	- `HF_HUB_CACHE=D:/huggingface_cache/hub`
	- `TRANSFORMERS_CACHE=D:/huggingface_cache/transformers`
	- `HF_DATASETS_CACHE=D:/huggingface_cache/datasets`
- If you do not have a D: drive, edit `start_platform.py` and `integrated_mppsc_platform.py` to point to another location (e.g., `C:/Users/<you>/.cache/hf`).

## Run

Option A — Launcher (recommended)
```powershell
python start_platform.py
```
This starts Streamlit on http://localhost:8502 and prepares model caches.

Option B — Direct Streamlit
```powershell
streamlit run integrated_mppsc_platform.py --server.port 8502
```

## Using the App

1) Home
- Overview and quick stats.

2) Answer Sheet Evaluation
- Upload an Answer Key (PDF or image) and one or more Answer Sheets (PDFs or images).
- Choose Difficulty preset or Customize thresholds:
	- full_marks, high_marks, mid_marks, low_marks → similarity thresholds mapping to 100/75/50/25% of per‑question marks.
- Set Total Marks per Question.
- Evaluation Mode:
	- Image/PDF Processing: uses IBM watsonx.ai OCR and compares extracted answers to the key.
	- CSV Mode: upload answer key CSV and student answers CSV for direct evaluation.
- Results:
	- Per‑question comparisons with similarity scores and marks.
	- Summary metrics and CSV/Excel export. PDF export uses `reportlab`.

3) Grammar & Spell Checker
- Text Input: paste text and run a grammar check via LanguageTool.
- Image Upload: upload an image; app extracts text via Watson OCR and then runs grammar checks.
- Outputs: corrections list, highlighted markers `[!! … !!]`, corrected text, and error metrics.

4) Question Generator
- Subject, difficulty, and count selection; choose Template, Multiple Choice, or AI Enhanced.
- If the optional module cannot be imported, the UI uses a robust template‑based fallback.
- Generate complete sample papers and download as TXT, Excel; PDF via `reportlab`.
Notes:
- Advanced AI generation needs local models available in HF cache; otherwise it stays in offline/template mode.
- The module resides at `SSDigimark-Question-generator/SSDigimark-Question-generator/generate_mppsc_questions.py`. If import fails, either copy it next to the app or add its folder to `PYTHONPATH`.

5) Analytics
- Illustrative charts (usage/performance). Replace with your real metrics as needed.

6) Settings
- Marking scheme, OCR engine (IBM Watson), OCR confidence threshold, grammar options, and generator defaults.
- “Check Watson Status” validates your `.env`.

## Project Structure
```
minimal_app/
	integrated_mppsc_platform.py   # Streamlit frontend
	watson_backend.py              # Backend orchestrator (Watson OCR, grammar)
	watson_ocr.py                  # watsonx.ai Vision wrapper (OCR for images/PDF)
	start_platform.py              # Launcher + HF caches on D:
	config.py                      # Paths/defaults and temp dirs
	SSDigimark-Question-generator/
		SSDigimark-Question-generator/
			generate_mppsc_questions.py  # Optional generator module
	temp/                          # Working directory for PDF pages and outputs
	requirements.txt               # Python dependencies
	.env.example                   # Sample IBM credentials (copy to .env)
```

## Configuration Notes
- IBM Model: `meta-llama/llama-3-2-90b-vision-instruct` (via watsonx.ai) for OCR.
- Grammar: Uses LanguageTool public API (requires internet). Heavy usage may rate‑limit; consider self‑hosting LanguageTool for production.
- Caches: Default to D: to reduce C: usage; change the env vars if needed.

## Troubleshooting

Watson import error: `IBM Watson AI libraries not installed`
- Cause: `ibm-watsonx-ai` missing.
- Fix: `pip install ibm-watsonx-ai` (already listed in requirements; reinstall if needed).

Watson configuration error: “Missing IBM Watson credentials”
- Cause: `.env` not found or missing keys.
- Fix: Create `.env` (see `.env.example`). Ensure API key, service URL, and project ID are valid.

Image/PDF OCR returns empty text
- Check file clarity and size; ensure PDFs aren’t encrypted.
- Confirm your IBM credentials and project access.

Grammar check fails with HTTP error
- LanguageTool endpoint unreachable or rate‑limited. Retry or self‑host LanguageTool.

No D: drive available
- Edit HF cache paths in `start_platform.py` and `integrated_mppsc_platform.py` to a writable location.

PDF export button warns about `reportlab`
- Install `reportlab` (already in requirements). If still failing, restart the venv.

Optional generator stuck in “basic mode”
- Ensure `generate_mppsc_questions.py` is importable. Add its folder to `PYTHONPATH` or place the file alongside the app.

GPU/CPU notes (PyTorch)
- If CUDA isn’t present, the app runs on CPU. This is fine for most flows; model downloads are cached.

## Development tips
- Temp files live under `temp/`; safe to clear when the app isn’t running.
- Adjust grading thresholds and marks from the UI (Evaluation tab) or tweak logic in `integrated_mppsc_platform.py`.
- Extend OCR: Add new engines in `watson_backend.py` and surface in Settings.

## More docs
- Architecture: `docs/ARCHITECTURE.md`
- Usage guide: `docs/USAGE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

## License and data
- This app processes documents locally and calls external services (IBM watsonx.ai, LanguageTool). Don’t upload sensitive data unless your policies permit.
- License: internal/unspecified. Add a LICENSE if distributing.

—
Generated: 2025‑08‑17
