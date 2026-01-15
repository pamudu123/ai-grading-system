"""
Question Generator - Main Entry Point

This is the main script to run the question generation workflow.
Uses LangGraph with multi-agent architecture for question generation.

Usage:
    python -m src.question_generator.main
"""
from pathlib import Path

from .graph import run_question_generator
from .output import create_iteration_folder, save_question_as_markdown, save_generation_summary
from .config import DIFFICULTY_LEVELS, QUESTION_TYPES, SUBJECTS


# ============================================================================
# SAMPLE INPUT VARIABLES (No argparse as per user rules)
# Modify these values to test different configurations
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
    
    print(f"\nConfiguration:")
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
    
    # Run the question generator workflow
    print("Running question generation workflow...")
    print("-" * 40)
    
    try:
        final_state = run_question_generator(
            subject=subject,
            difficulty=difficulty,
            question_type=question_type,
            num_options=num_options,
            output_path=str(output_folder),
            iteration_id=output_folder.name
        )
    except Exception as e:
        print(f"\nError during generation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("-" * 40)
    print("\nGeneration complete!")
    print()
    
    # Display results
    print("Generated Question:")
    print("-" * 40)
    print(final_state.get("question", "No question generated"))
    print()
    
    if question_type == "MCQ":
        print("Options:")
        for opt in final_state.get("options", []):
            print(f"  {opt}")
        print()
        print(f"Correct Answer: {final_state.get('correct_answer', 'N/A')}")
    
    elif question_type == "Short Answer":
        print(f"Answer: {final_state.get('correct_answer', 'N/A')}")
        print()
        print("Derivation:")
        print(final_state.get("answer_derivation", "No derivation"))
    
    elif question_type == "Long Answer":
        print(f"Answer: {final_state.get('correct_answer', 'N/A')[:200]}...")
        print()
        print("Marking Scheme:")
        for criteria, marks in final_state.get("marking_scheme", {}).items():
            print(f"  - {criteria}: {marks} marks")
    
    print()
    print(f"Review Status: {'Approved' if final_state.get('is_approved') else 'Not Approved'}")
    if final_state.get("review_feedback"):
        print(f"Feedback: {final_state.get('review_feedback')}")
    
    # Save outputs
    print("\nSaving outputs...")
    
    # Update state with output folder
    final_state["output_folder"] = str(output_folder)
    
    # Save question as markdown
    md_path = save_question_as_markdown(final_state, output_folder)
    print(f"  Question saved: {md_path}")
    
    # Save generation summary
    summary_path = save_generation_summary(final_state, output_folder)
    print(f"  Summary saved: {summary_path}")
    
    print()
    print("=" * 60)
    print(f"All outputs saved to: {output_folder}")
    print("=" * 60)


if __name__ == "__main__":
    main()
