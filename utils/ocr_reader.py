from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import torch

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load BLIP2 processor and model
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b").to(device)

def extract_text_from_image(image_path):
    """
    Uses BLIP2 (OPT 2.7B) to read and describe handwritten or printed text in image.
    """
    image = Image.open(image_path).convert("RGB")
    prompt = "What is written in this image?"

    # Process the image and prompt
    inputs = processor(image, prompt, return_tensors="pt").to(device)

    # Generate response
    output = model.generate(**inputs, max_new_tokens=300)

    # Decode and return the caption
    text = processor.decode(output[0], skip_special_tokens=True)
    return text
