"""
Image Generator Tool - Generates AI images using Gemini 3 Pro via OpenRouter.
"""
import base64
import requests
import os
from pathlib import Path
from ..config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_IMAGE_NAME

def generate_ai_image(prompt: str, output_path: str) -> str:
    """
    Generate an image using Google's Gemini Image model via OpenRouter.
    
    Args:
        prompt: Detailed description of the image to generate
        output_path: Absolute path to save the generated image (PNG/JPG)
        
    Returns:
        Path to the saved image file
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://localhost", # Required by OpenRouter
        "X-Title": "AI Grading System",
        "Content-Type": "application/json"
    }

    # Gemini Image Model specific payload
    payload = {
        "model": MODEL_IMAGE_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "modalities": ["image", "text"] # Required for OpenRouter image models
    }

    try:
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # Parse response for image data
        # Looking for 'images' field in message content as per OpenRouter docs for this model
        try:
            message = data['choices'][0]['message']
            
            # Case 1: 'images' array in message object (common for multimodal output)
            if 'images' in message and message['images']:
                img_data = message['images'][0] # Base64 string
                if "," in img_data:
                    img_data = img_data.split(",", 1)[1]
                
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_data))
            
            # Case 2: Content contains URL or other format (fallback check)
            elif 'content' in message and "http" in message['content']:
                # Simple heuristic: if the content is just a URL
                content = message['content'].strip()
                if content.startswith("http"):
                    img_resp = requests.get(content)
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                else:
                    raise ValueError("Content not a direct URL")
            
            else:
                # Debugging info
                raise ValueError(f"No image data found. Response keys: {data.keys()}")

        except Exception as parse_err:
            raise ValueError(f"Failed to parse image from response: {parse_err}. Data: {str(data)[:200]}")

        return output_path

    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}")
