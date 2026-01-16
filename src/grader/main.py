import os
import sys
from pathlib import Path
import json

# Ensure src is in pythonpath
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.grader.mcq_grader import extract_answers, grade_mcq

def main():
    # Path to sample image
    sample_image = project_root / "samples" / "mcq_answer_sheet_1.png"
    
    if not sample_image.exists():
        print(f"Error: Sample image not found at {sample_image}")
        return

    print(f"Processing: {sample_image}")
    
    try:
        # 1. Extract answers
        print("Extracting answers from image...")
        extracted_answers = extract_answers(str(sample_image))
        print("Extracted Answers:")
        print(json.dumps(extracted_answers, indent=2))
        
        # 2. Define Dummy Correct Answers (Mocking a key for now)
        # Assuming the sample has some questions, we'll create a key for the first few
        # In a real scenario, this would come from the database or teacher input
        # Let's assume there are 5 questions for this test run
        correct_answers = {
            "1": [2],
            "2": [3],
            "3": [1], 
            "4": [4],
            "5": [2]
        }
        
        if not extracted_answers:
             print("\nNo answers extracted. Check the image or the model prompt.")
             return

        # Adjust correct_answers keys to match extracted keys if needed (e.g., if extracted has more)
        # For this test, we just use the intersection or a predefined set
        
        print("\nGrading...")
        results = grade_mcq(extracted_answers, correct_answers)
        
        print("-" * 30)
        print("GRADING RESULTS")
        print("-" * 30)
        print(f"Score: {results['total_score']} / {results['max_score']}")
        print(f"Percentage: {results['percentage']:.1f}%")
        print("-" * 30)
        print("Details:")
        print(json.dumps(results['details'], indent=2))
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
