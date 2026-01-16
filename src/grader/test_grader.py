import sys
from pathlib import Path
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.grader.short_answer.grader import grade_short_answer
from src.grader.mcq.mcq_grader import extract_answers

def test_short_answer_grader():
    print("Testing Short Answer Grader...")
    question = "What is Newton's Second Law of Motion?"
    correct = "Newton's second law of motion states that the force acting on an object is equal to the mass of that object times its acceleration (F=ma)."
    student = "Forces cause things to accelerate. F = ma."
    
    result = grade_short_answer(question, student, correct)
    print("Result:")
    print(json.dumps(result, indent=2))
    
    assert "assigned_score" in result
    assert "feedback" in result
    assert result["assigned_score"] >= 0
    print("Short Answer Grader Test PASSED")

def test_mcq_import():
    print("\nTesting MCQ Grader Import...")
    # Just checking if we can import logic without error
    assert extract_answers is not None
    print("MCQ Grader Import Test PASSED")

if __name__ == "__main__":
    test_short_answer_grader()
    test_mcq_import()
