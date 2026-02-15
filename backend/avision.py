import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import io

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=KEY)

def photo_bytes_to_claim(image_bytes):
    """
    Takes an image bytes, looks at it with 'ADHD-Friendly Eyes', 
    and returns a single, actionable CLAIM string.
    """
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    img = Image.open(io.BytesIO(image_bytes))

    prompt = """
    You are an AI assistant for a user with ADHD/Executive Dysfunction.
    Analyze this image and identify the SINGLE most important task or context.
    
    Rules:
    1. Ignore background clutter. Focus on the main object or mess.
    2. If it's a mess, identify the starting point (e.g., "The user needs to organize the laundry").
    3. If it's a document/screen, summarize the core action (e.g., "The user needs to pay the electric bill of $50").
    4. Output ONE clear sentence starting with "The user needs to..." or "The user wants to...".
    5. Do not include filler words like "The image shows...".
    """
    
    response = model.generate_content([prompt, img])
    
    return response.text.strip()

# img_path = "high-angle-messy-home-concept.jpg"

# claim = photo_bytes_to_claim(img_path)
# print("Generated Claim:", claim)
