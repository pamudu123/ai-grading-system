"""
State definitions for the LangGraph Question Generator workflow.
"""
from typing import TypedDict, Literal


class QuestionState(TypedDict, total=False):
    """
    State schema for the Question Generator LangGraph workflow.
    
    This state is passed between agents and modified at each step.
    """
    # Input parameters
    subject: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    question_type: Literal["MCQ", "Short Answer", "Long Answer"]
    num_options: int
    
    # Context retrieved from documents
    context: str
    topic: str
    
    # Generated question content
    question: str
    question_image_path: str | None
    
    # MCQ specific
    options: list[str]
    
    # Answer content
    correct_answer: str
    answer_derivation: str  # For Short Answer - how the answer is derived
    
    # Long Answer specific
    marking_scheme: dict[str, int]  # Breakdown of marks totaling 100
    
    # Review feedback
    review_feedback: str
    is_approved: bool
    revision_count: int
    
    # Output metadata
    iteration_id: str
    output_folder: str
    graph_paths: list[str]


class GraphRequest(TypedDict):
    """
    Request schema for graph generation.
    """
    expression: str
    graph_type: Literal["linear", "quadratic", "custom"]
    title: str
    x_label: str
    y_label: str
    x_range: tuple[float, float]
