import base64
import json
import os
import requests
from typing import Any
from pathlib import Path

# Try to import config, assuming we are running from project root or src
try:
    from src.question_generator.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
except ImportError:
    # Fallback for running directly if needed, or if pythonpath isn't set
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.question_generator.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME

def encode_image(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_answers(image_path: str) -> dict[str, list[int]]:
    """
    Extracts answers from an MCQ answer sheet image using an LLM.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        A dictionary mapping question IDs (as strings) to lists of selected option indices (ints).
        Example: {'1': [2], '2': [1, 3]}
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set")

    base64_image = encode_image(image_path)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AI Grading System",
        "Content-Type": "application/json"
    }

    prompt = """
    Analyze this MCQ answer sheet.
    Extract the question numbers and the selected options for each question.
    
    Rules:
    1. Identify the question number.
    2. Identify which option(s) are marked/shaded.
    3. Return the result as a JSON object where keys are question numbers (as strings) and values are lists of integers representing selected options.
    4. Options are usually 1-indexed (1, 2, 3, 4) or (A=1, B=2, C=3, D=4).
    5. If no option is selected for a question, return an empty list.
    6. If multiple options are selected, include all of them in the list.
    
    Output ONLY valid JSON. No markdown formatting.
    Example format:
    {
      "1": [2],
      "2": [1, 3],
      "3": []
    }
    """

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "response_format": {"type": "json_object"} 
    }

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        content = data['choices'][0]['message']['content']
        # Clean up potential markdown code blocks if the model ignores the instruction
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content.strip())
        
    except Exception as e:
        raise RuntimeError(f"Failed to extract answers: {e}")

def grade_mcq(extracted_answers: dict[str, list[int]], correct_answers: dict[str, list[int]]) -> dict[str, Any]:
    """
    Grades the extracted answers against the correct answers.
    
    Args:
        extracted_answers: Dictionary of extracted answers.
        correct_answers: Dictionary of correct answers.
        
    Returns:
        A dictionary containing the total score and detailed breakdown.
    """
    total_score = 0
    max_score = len(correct_answers)
    details = {}
    
    for q_num, correct_opts in correct_answers.items():
        q_num = str(q_num) # Ensure string key
        selected_opts = extracted_answers.get(q_num, [])
        
        status = "wrong"
        score = 0
        
        if len(selected_opts) == 0:
            status = "unanswered"
        elif len(selected_opts) > 1:
            status = "multiple_selected" # Treated as wrong per requirements
        elif selected_opts == correct_opts:
            status = "correct"
            score = 1
        
        total_score += score
        details[q_num] = {
            "selected": selected_opts,
            "correct": correct_opts,
            "status": status,
            "score": score
        }
        
    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
        "details": details
    }
