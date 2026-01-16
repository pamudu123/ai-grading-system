"""
Question Generator - Main Entry Point

This is the main script to run the question generation workflow.
Uses LangGraph with multi-agent architecture for question generation.

Usage:
    python -m src.question_generator.main
"""
from pathlib import Path

from .graph import run_question_generator
from .output import create_iteration_folder, save_question_as_markdown, save_generation_summary, save_question_as_json, save_batch_json
from .config import DIFFICULTY_LEVELS, QUESTION_TYPES, SUBJECTS


# ============================================================================
# SAMPLE INPUT VARIABLES
# ============================================================================

# Subject to generate questions for (must exist in doc_info.yaml)
subject = "physics"

# Difficulty level: "Easy", "Medium", "Hard"
difficulty = "Medium"

# Question type: "MCQ", "Short Answer", "Long Answer"
question_type = "MCQ"

# Number of options for MCQ (2-6)
num_options = 4


def validate_inputs() -> bool:
    """Validate input parameters."""
    if difficulty not in DIFFICULTY_LEVELS:
        print(f"Invalid difficulty: {difficulty}")
        print(f"Valid options: {DIFFICULTY_LEVELS}")
        return False
    
    if question_type not in QUESTION_TYPES:
        print(f"Invalid question type: {question_type}")
        print(f"Valid options: {QUESTION_TYPES}")
        return False
    
    if question_type == "MCQ" and not (2 <= num_options <= 6):
        print(f"Invalid number of options: {num_options}")
        print("Must be between 2 and 6")
        return False
    
    return True


def main():
    """Main entry point for question generation."""
    print("=" * 60)
    print("Question Generator - LangGraph Multi-Agent System")
    print("=" * 60)
    
    # Validate inputs
    if not validate_inputs():
        return
    
    print(f"Configuration:")
    print(f"  Subject: {subject}")
    print(f"  Difficulty: {difficulty}")
    print(f"  Question Type: {question_type}")
    if question_type == "MCQ":
        print(f"  Number of Options: {num_options}")
    print()
    
    # Create iteration folder
    print("Creating output folder...")
    output_folder = create_iteration_folder()
    print(f"  Output folder: {output_folder}")
    print()
    
    # Prompt for custom instructions
    custom_instructions = 'Generate Calculations related Questions. Questions that needs visual figures'

    # Run the question generator workflow
    print("Running question generation workflow...")
    print("-" * 40)
    
    # Prompt for number of questions
    print("Enter number of questions to generate (Default 1):")
    try:
        num_str = input("> ").strip()
        num_questions = int(num_str) if num_str else 1
    except ValueError:
        print("Invalid number. Defaulting to 1.")
        num_questions = 1
    
    results = []
    previous_questions_text = []
    
    for i in range(num_questions):
        question_id = f"q{i+1}"
        print(f"\nProcessing Question {i+1}/{num_questions} (ID: {question_id})...")
        
        try:
            final_state = run_question_generator(
                subject=subject,
                difficulty=difficulty,
                question_type=question_type,
                num_options=num_options,
                output_path=str(output_folder),
                question_id=question_id,
                custom_instructions=custom_instructions,
                previous_questions=previous_questions_text,
                iteration_id=output_folder.name
            )
            results.append(final_state)
            
            # Add generated question to history to avoid duplicates
            if final_state.get("question"):
                previous_questions_text.append(final_state.get("question"))
                
            print(f"  Generated successfully.")
            
        except Exception as e:
            print(f"  Error generating question {question_id}: {e}")
            import traceback
            traceback.print_exc()

    print("-" * 40)
    print("Generation complete!")
    print()
    
    if results:
        # Save Batch JSON
        print("Saving batch results...")
        batch_path = save_batch_json(results, output_folder)
        print(f"  Batch JSON saved: {batch_path}")
        
        # Display first result as sample
        print("\nSample Result (Question 1):")
        print("-" * 20)
        sample = results[0]
        print(sample.get("question", "No question text"))
        print(f"Correct Answer: {sample.get('correct_answer', 'N/A')}")
    
    print()
    print("=" * 60)
    print(f"All outputs saved to: {output_folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()
