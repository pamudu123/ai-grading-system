"""
Output Generation - Creates iteration folders and saves questions as markdown.
"""
from pathlib import Path
from datetime import datetime

from .state import QuestionState
from .config import OUTPUT_DIR


def create_iteration_folder(base_path: Path | None = None) -> Path:
    """
    Create a timestamped folder for this generation iteration.
    
    Args:
        base_path: Base path for output (defaults to OUTPUT_DIR from config)
    
    Returns:
        Path to the created folder
    """
    if base_path is None:
        base_path = OUTPUT_DIR
    
    # Create timestamp-based folder name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = base_path / timestamp
    
    # Create the directory
    folder_path.mkdir(parents=True, exist_ok=True)
    
    return folder_path


def format_mcq_markdown(state: QuestionState) -> str:
    """Format MCQ question as markdown."""
    content = []
    content.append("# MCQ Question\n")
    content.append(f"**Subject:** {state.get('subject', 'N/A')}\n")
    content.append(f"**Difficulty:** {state.get('difficulty', 'N/A')}\n")
    content.append(f"**Topic:** {state.get('topic', 'N/A')}\n")
    content.append("\n---\n")
    
    content.append("## Question\n")
    content.append(f"{state.get('question', 'No question generated')}\n")
    
    # Add question image if exists
    if state.get('question_image_path'):
        content.append(f"\n![Question Graph]({state['question_image_path']})\n")
    
    content.append("\n## Options\n")
    options = state.get('options', [])
    for option in options:
        content.append(f"- {option}\n")
    
    content.append("\n---\n")
    content.append("## Answer Key\n")
    content.append(f"**Correct Answer:** {state.get('correct_answer', 'N/A')}\n")
    
    if state.get('answer_derivation'):
        content.append("\n### Explanation\n")
        content.append(f"{state['answer_derivation']}\n")
    
    # Add review status
    content.append("\n---\n")
    content.append("## Review Status\n")
    content.append(f"**Approved:** {'Yes' if state.get('is_approved') else 'No'}\n")
    if state.get('review_feedback'):
        content.append(f"**Feedback:** {state['review_feedback']}\n")
    
    return "".join(content)


def format_short_answer_markdown(state: QuestionState) -> str:
    """Format Short Answer question as markdown."""
    content = []
    content.append("# Short Answer Question\n")
    content.append(f"**Subject:** {state.get('subject', 'N/A')}\n")
    content.append(f"**Difficulty:** {state.get('difficulty', 'N/A')}\n")
    content.append(f"**Topic:** {state.get('topic', 'N/A')}\n")
    content.append("\n---\n")
    
    content.append("## Question\n")
    content.append(f"{state.get('question', 'No question generated')}\n")
    
    # Add question image if exists
    if state.get('question_image_path'):
        content.append(f"\n![Question Graph]({state['question_image_path']})\n")
    
    content.append("\n---\n")
    content.append("## Answer Key\n")
    content.append(f"**Correct Answer:** {state.get('correct_answer', 'N/A')}\n")
    
    content.append("\n### Answer Derivation\n")
    derivation = state.get('answer_derivation', 'No derivation provided')
    # Format derivation with proper line breaks
    derivation = derivation.replace("\\n", "\n")
    content.append(f"{derivation}\n")
    
    # Add review status
    content.append("\n---\n")
    content.append("## Review Status\n")
    content.append(f"**Approved:** {'Yes' if state.get('is_approved') else 'No'}\n")
    if state.get('review_feedback'):
        content.append(f"**Feedback:** {state['review_feedback']}\n")
    
    return "".join(content)


def format_long_answer_markdown(state: QuestionState) -> str:
    """Format Long Answer question as markdown with marking scheme."""
    content = []
    content.append("# Long Answer Question\n")
    content.append(f"**Subject:** {state.get('subject', 'N/A')}\n")
    content.append(f"**Difficulty:** {state.get('difficulty', 'N/A')}\n")
    content.append(f"**Topic:** {state.get('topic', 'N/A')}\n")
    content.append("**Total Marks:** 100\n")
    content.append("\n---\n")
    
    content.append("## Question\n")
    content.append(f"{state.get('question', 'No question generated')}\n")
    
    # Add question image if exists
    if state.get('question_image_path'):
        content.append(f"\n![Question Graph]({state['question_image_path']})\n")
    
    content.append("\n---\n")
    content.append("## Marking Scheme\n")
    content.append("| Criteria | Marks |\n")
    content.append("|----------|-------|\n")
    
    marking_scheme = state.get('marking_scheme', {})
    total_marks = 0
    for criteria, marks in marking_scheme.items():
        content.append(f"| {criteria} | {marks} |\n")
        total_marks += marks if isinstance(marks, int) else int(marks)
    
    content.append(f"| **Total** | **{total_marks}** |\n")
    
    content.append("\n---\n")
    content.append("## Model Answer\n")
    answer = state.get('answer_derivation', state.get('correct_answer', 'No answer provided'))
    content.append(f"{answer}\n")
    
    # Add review status
    content.append("\n---\n")
    content.append("## Review Status\n")
    content.append(f"**Approved:** {'Yes' if state.get('is_approved') else 'No'}\n")
    if state.get('review_feedback'):
        content.append(f"**Feedback:** {state['review_feedback']}\n")
    
    return "".join(content)


def save_question_as_markdown(state: QuestionState, folder: Path | str) -> str:
    """
    Generate and save markdown file for the question.
    
    Args:
        state: The QuestionState with all question data
        folder: Folder path to save the markdown file
    
    Returns:
        Path to the saved markdown file
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    
    question_type = state.get('question_type', 'MCQ')
    
    # Generate appropriate markdown content
    if question_type == "MCQ":
        content = format_mcq_markdown(state)
        filename = "mcq_question.md"
    elif question_type == "Short Answer":
        content = format_short_answer_markdown(state)
        filename = "short_answer_question.md"
    elif question_type == "Long Answer":
        content = format_long_answer_markdown(state)
        filename = "long_answer_question.md"
    else:
        content = f"# Unknown Question Type: {question_type}\n"
        filename = "question.md"
    
    # Save the file
    file_path = folder / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Saved question to: {file_path}")
    return str(file_path)


def save_generation_summary(state: QuestionState, folder: Path | str) -> str:
    """
    Save a summary JSON file with all generation metadata.
    
    Args:
        state: The QuestionState with all data
        folder: Folder path to save the summary
    
    Returns:
        Path to the saved summary file
    """
    import json
    
    folder = Path(folder)
    
    summary = {
        "subject": state.get("subject"),
        "difficulty": state.get("difficulty"),
        "question_type": state.get("question_type"),
        "topic": state.get("topic"),
        "is_approved": state.get("is_approved"),
        "revision_count": state.get("revision_count"),
        "generated_at": datetime.now().isoformat()
    }
    
    file_path = folder / "generation_summary.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    return str(file_path)
