import requests
import torch
import os
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes

def check_grammar(text):
    api_url = "https://api.languagetool.org/v2/check"
    data = {
        "text": text,
        "language": "en-US"
    }

    response = requests.post(api_url, data=data)
    result = response.json()

    errors = []
    for match in result.get("matches", []):
        better = match.get("replacements", [])
        suggestion = better[0]['value'] if better else match['context']['text'][match['context']['offset']:match['context']['offset'] + match['length']]

        errors.append({
            "offset": match["offset"],
            "length": match["length"],
            "message": match["message"],
            "better": suggestion
        })

    return errors

def correct_text_with_llm(text):
    """
    Use IBM Watsonx AI with Llama model for grammar correction
    """
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # IBM Watsonx AI credentials
        credentials = {
            "url": os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            "apikey": os.getenv("WATSONX_API_KEY") or os.getenv("IBM_API_KEY")
        }
        
        project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("IBM_PROJECT_ID")
        
        if not credentials["apikey"] or not project_id:
            print("IBM API key or project ID not found in environment variables")
            return None
        
        # Initialize the model
        model = Model(
            model_id="meta-llama/llama-2-13b-chat",  # Using supported model
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 200,
                GenParams.TEMPERATURE: 0.1,
                GenParams.REPETITION_PENALTY: 1.1
            },
            credentials=credentials,
            project_id=project_id
        )
        
        # Create a prompt for grammar correction
        prompt = f"""You are a grammar correction assistant. Please correct the following text for grammar, spelling, and clarity while maintaining the original meaning. Only return the corrected text without any explanations.

Original text: {text}

Corrected text:"""
        
        # Generate the correction
        response = model.generate_text(prompt=prompt)
        
        if response and response.strip() != text.strip():
            return response.strip()
        
        return None
        
    except Exception as e:
        print(f"IBM Watsonx AI correction failed: {e}")
        return None

def correct_text(text):
    """
    Correct text using IBM Watsonx AI first, then fallback to API
    """
    import re
    
    # Try IBM Watsonx AI with Llama first
    try:
        llm_corrected = correct_text_with_llm(text)
        if llm_corrected and llm_corrected != text and len(llm_corrected) > 10:
            # Basic post-processing only
            corrected = llm_corrected.strip()
            
            # Fix capitalization
            if corrected and corrected[0].islower():
                corrected = corrected[0].upper() + corrected[1:]
            
            # Ensure proper punctuation
            if not corrected.endswith(('.', '?', '!')):
                corrected += '.'
            
            # Fix multiple spaces
            corrected = re.sub(r'\s+', ' ', corrected)
            
            return corrected
    except Exception as e:
        print(f"LLM correction failed, using API fallback: {e}")
    
    # Fallback to API-based correction
    errors = check_grammar(text)
    corrected = text
    
    # Apply API suggestions in reverse order to avoid offset issues
    for error in sorted(errors, key=lambda x: -x["offset"]):
        start = error["offset"]
        end = start + error["length"]
        suggestion = error["better"]
        
        corrected = corrected[:start] + suggestion + corrected[end:]
    
    # Basic post-processing only
    # Fix capitalization
    if corrected and corrected[0].islower():
        corrected = corrected[0].upper() + corrected[1:]
    
    # Ensure proper punctuation
    corrected = corrected.strip()
    if not corrected.endswith(('.', '?', '!')):
        corrected += '.'
    
    # Fix multiple spaces
    corrected = re.sub(r'\s+', ' ', corrected)
    
    return corrected
