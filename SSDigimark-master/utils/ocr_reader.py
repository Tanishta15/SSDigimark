import os
import base64
from typing import Optional

from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load environment variables (IBM_API_KEY, IBM_SERVICE_URL, IBM_PROJECT_ID)
load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
SERVICE_URL = os.getenv("IBM_SERVICE_URL")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

if not (API_KEY and SERVICE_URL and PROJECT_ID):
    raise RuntimeError(
        "Missing IBM Watsonx configuration. Please set IBM_API_KEY, IBM_SERVICE_URL, and IBM_PROJECT_ID in your environment/.env."
    )

# Initialize Watsonx client and model (vision instruct model)
_credentials = Credentials(url=SERVICE_URL, api_key=API_KEY)
_client = APIClient(credentials=_credentials)
_client.set.default_project(PROJECT_ID)

_MODEL_ID = "meta-llama/llama-3-2-90b-vision-instruct"
_PARAMS = {"decoding_method": "greedy", "max_new_tokens": 500}

_model = ModelInference(
    model_id=_MODEL_ID,
    credentials=_credentials,
    project_id=PROJECT_ID,
    params=_PARAMS,
)

_EXTRACTION_PROMPT = (
    "You are an expert in handwriting recognition and text extraction. "
    "Your task is to extract only the text exactly as it appears in the image. "
    "Do not add any descriptions, explanations, or formatting notes. "
    "Strictly maintain: Original structure (paragraphs, sections, equations), subscripts, superscripts, and mathematical symbols as they appear. "
    "If any part is scribbled or unreadable, simply ignore it. "
    "Do not include anything written in hindi or any other language. "
    "Do not fix spelling or grammar errors. "
    "Only return the extracted text, formatted exactly as it appears and please do maintain the structure."
)


def _encode_image_to_b64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_text_from_image(image_path: str) -> Optional[str]:
    """Extract text from an image using IBM Watsonx vision model.

    Returns the extracted text, or None on failure.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    image_b64 = _encode_image_to_b64(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _EXTRACTION_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        }
    ]

    try:
        response = _model.chat(messages=messages)
        return (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
            if response
            else None
        )
    except Exception:
        # Let callers decide how to handle None; keeps function side-effect free
        return None
