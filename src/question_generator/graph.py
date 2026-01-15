"""
LangGraph Workflow - Orchestrates the multi-agent question generation pipeline.

Workflow:
START -> context_retrieval -> question_generator -> review -> conditional_edge
                                                         |
                                               (if not approved) -> question_generator
                                               (if approved) -> END
"""
from langgraph.graph import StateGraph, END

from .state import QuestionState
from .agents.context_agent import context_retrieval_node
from .agents.question_agent import question_generator_node
from .agents.review_agent import review_node
from .config import MAX_RETRIES


def should_regenerate(state: QuestionState) -> str:
    """
    Conditional edge function to determine if question should be regenerated.
    
    Returns:
        "regenerate" if not approved and under max retries
        "end" if approved or max retries reached
    """
    is_approved = state.get("is_approved", False)
    revision_count = state.get("revision_count", 0)
    
    if is_approved:
        return "end"
    
    if revision_count >= MAX_RETRIES:
        print(f"Max retries ({MAX_RETRIES}) reached. Forcing approval.")
        return "end"
    
    return "regenerate"


def build_question_generator_graph() -> StateGraph:
    """
    Build the LangGraph StateGraph for question generation.
    
    The workflow consists of:
    1. context_retrieval: Fetch relevant content from subject documents
    2. question_generator: Generate question based on type and difficulty
    3. review: Validate question, answer, and marking scheme
    4. Conditional edge: Regenerate if not approved, otherwise end
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the state graph
    workflow = StateGraph(QuestionState)
    
    # Add nodes
    workflow.add_node("context_retrieval", context_retrieval_node)
    workflow.add_node("question_generator", question_generator_node)
    workflow.add_node("review", review_node)
    
    # Set entry point
    workflow.set_entry_point("context_retrieval")
    
    # Add edges
    workflow.add_edge("context_retrieval", "question_generator")
    workflow.add_edge("question_generator", "review")
    
    # Add conditional edge from review
    workflow.add_conditional_edges(
        "review",
        should_regenerate,
        {
            "regenerate": "question_generator",
            "end": END
        }
    )
    
    # Compile the graph
    compiled_graph = workflow.compile()
    
    return compiled_graph


def run_question_generator(
    subject: str,
    difficulty: str,
    question_type: str,
    num_options: int = 4,
    iteration_id: str | None = None
) -> QuestionState:
    """
    Execute the question generation workflow.
    
    Args:
        subject: The subject for question generation (e.g., 'physics')
        difficulty: Difficulty level ('Easy', 'Medium', 'Hard')
        question_type: Type of question ('MCQ', 'Short Answer', 'Long Answer')
        num_options: Number of options for MCQ (default: 4)
        iteration_id: Optional ID for this generation iteration
    
    Returns:
        Final QuestionState with generated question and all metadata
    """
    # Build the graph
    graph = build_question_generator_graph()
    
    # Prepare initial state
    initial_state: QuestionState = {
        "subject": subject,
        "difficulty": difficulty,
        "question_type": question_type,
        "num_options": num_options,
        "iteration_id": iteration_id or "",
        "revision_count": 0,
        "is_approved": False,
        "context": "",
        "question": "",
        "options": [],
        "correct_answer": "",
        "answer_derivation": "",
        "marking_scheme": {},
        "review_feedback": "",
        "graph_paths": []
    }
    
    # Execute the graph
    final_state = graph.invoke(initial_state)
    
    return final_state
