"""
Context Retrieval Agent - Fetches relevant content from subject documents.
"""
from langchain_openai import ChatOpenAI

from ..config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME, TEMPERATURE
from ..state import QuestionState
from ..tools.context_retriever import retrieve_context, get_available_subjects


def create_context_llm() -> ChatOpenAI:
    """Create the LLM instance for context processing."""
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=TEMPERATURE,
    )


def context_retrieval_node(state: QuestionState) -> dict:
    """
    LangGraph node that retrieves relevant context for question generation.
    
    This agent:
    1. Validates the subject exists in doc_info.yaml
    2. Retrieves markdown content for the subject
    3. Optionally uses LLM to extract most relevant sections
    
    Args:
        state: Current QuestionState with subject specified
    
    Returns:
        Updated state dict with 'context' and 'topic' fields
    """
    subject = state.get("subject", "physics")
    difficulty = state.get("difficulty", "Medium")
    question_type = state.get("question_type", "MCQ")
    
    # Check available subjects
    available = get_available_subjects()
    if subject.lower() not in [s.lower() for s in available]:
        return {
            "context": f"Subject '{subject}' not found. Available subjects: {available}",
            "topic": "Unknown"
        }
    
    # Retrieve raw context from markdown files
    raw_context = retrieve_context(subject)
    
    if not raw_context or "No content available" in raw_context:
        return {
            "context": raw_context,
            "topic": "Unknown"
        }
    
    # Use LLM to extract relevant topic based on content
    llm = create_context_llm()
    
    topic_prompt = f"""Analyze the following educational content and identify the main topics covered.
Return a brief comma-separated list of 3-5 key topics suitable for {difficulty} level {question_type} questions.

Content excerpt (first 3000 chars):
{raw_context[:3000]}

Return ONLY the topic list, nothing else."""

    try:
        response = llm.invoke(topic_prompt)
        topics = response.content.strip()
    except Exception as e:
        print(f"Error extracting topics: {e}")
        topics = "General Physics"
    
    return {
        "context": raw_context,
        "topic": topics
    }
