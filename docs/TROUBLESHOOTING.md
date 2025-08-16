# Troubleshooting

## Common Issues

### "IBM Watson AI libraries not installed"
- Symptom: ImportError mentioning `ibm_watsonx_ai`.
- Fix: `pip install ibm-watsonx-ai` (already in requirements). Recreate venv if needed.

### "Missing IBM Watson credentials"
- Symptom: ValueError from `watson_ocr.py` about `.env`.
- Fix: Create `.env` from `.env.example` with correct `IBM_API_KEY`, `IBM_SERVICE_URL`, `IBM_PROJECT_ID`.

### OCR returns empty text
- Check file quality (resolution, contrast).
- Make sure the PDF is not password-protected/encrypted.
- Validate your IBM project permissions and API key.

### Grammar API error (HTTP 4xx/5xx)
- The public LanguageTool endpoint may be rate-limited or unavailable.
- Retry later, or self-host LanguageTool and update the endpoint in `watson_backend.py`.

### No D: drive available
- Edit cache paths in `start_platform.py` and `integrated_mppsc_platform.py` to a writable location.

### PDF export not available
- Ensure `reportlab` is installed and importable. Restart the venv.

### Excel export fails
- Ensure `XlsxWriter` is installed (it’s in requirements). Restart the venv.

### Generator stays in basic mode
- The optional module may not be importable. Ensure
  `SSDigimark-Question-generator/SSDigimark-Question-generator/generate_mppsc_questions.py`
  exists and is on `PYTHONPATH`. Otherwise, the UI will use templates.

## Logs and Temp
- Check console output where Streamlit is running.
- Temporary files live under `temp/`; safe to clear when the app is stopped.
