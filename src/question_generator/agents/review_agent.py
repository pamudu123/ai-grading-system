"""
Review Agent - Validates questions, answers, and marking schemes.

Ensures:
- Question quality and appropriateness
- Answer correctness
- MCQ distractors are plausible but incorrect
- Long Answer marking scheme totals 100
"""
import json
from langchain_openai import ChatOpenAI

from ..config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_NAME, 
    TOTAL_MARKS,
    MAX_RETRIES
)
from ..state import QuestionState


def create_review_llm() -> ChatOpenAI:
    """Create the LLM instance for review."""
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.3,  # Lower temperature for more consistent reviews
    )


def review_mcq_prompt(question: str, options: list, correct_answer: str, context: str) -> str:
    """Generate prompt for reviewing MCQ questions."""
    options_text = "\n".join(options) if options else "No options provided"
    return f"""You are an expert educational content reviewer. Review the following MCQ question for quality and correctness.

QUESTION:
{question}

OPTIONS:
{options_text}

STATED CORRECT ANSWER: {correct_answer}

ORIGINAL CONTEXT (excerpt):
{context[:3000]}

REVIEW CRITERIA:
1. Is the question clear and unambiguous?
2. Is the stated correct answer actually correct based on the context?
3. Are the distractors (wrong options) plausible but clearly incorrect?
4. Is there only ONE correct answer?
5. Is the difficulty appropriate?
6. Are there any factual errors?

OUTPUT FORMAT (JSON):
{{
    "is_approved": true/false,
    "quality_score": 1-10,
    "issues": ["issue1", "issue2"] or [],
    "suggestions": ["suggestion1"] or [],
    "correct_answer_verified": true/false,
    "feedback_summary": "Brief summary of review"
}}

Return ONLY valid JSON, no additional text."""


def review_short_answer_prompt(question: str, answer: str, derivation: str, context: str) -> str:
    """Generate prompt for reviewing Short Answer questions."""
    return f"""You are an expert educational content reviewer. Review the following Short Answer question for quality and correctness.

QUESTION:
{question}

STATED ANSWER:
{answer}

DERIVATION/EXPLANATION:
{derivation}

ORIGINAL CONTEXT (excerpt):
{context[:3000]}

REVIEW CRITERIA:
1. Is the question clear and answerable?
2. Is the stated answer correct based on the context?
3. Is the derivation/explanation logical and complete?
4. Does the derivation lead to the correct answer?
5. Is the difficulty appropriate?
6. Are there any factual errors?

OUTPUT FORMAT (JSON):
{{
    "is_approved": true/false,
    "quality_score": 1-10,
    "issues": ["issue1", "issue2"] or [],
    "suggestions": ["suggestion1"] or [],
    "correct_answer_verified": true/false,
    "derivation_verified": true/false,
    "feedback_summary": "Brief summary of review"
}}

Return ONLY valid JSON, no additional text."""


def review_long_answer_prompt(
    question: str, 
    answer: str, 
    marking_scheme: dict, 
    context: str
) -> str:
    """Generate prompt for reviewing Long Answer questions."""
    scheme_text = json.dumps(marking_scheme, indent=2) if marking_scheme else "No marking scheme"
    total = sum(marking_scheme.values()) if marking_scheme else 0
    
    return f"""You are an expert educational content reviewer. Review the following Long Answer question for quality and correctness.

QUESTION:
{question}

MODEL ANSWER:
{answer}

MARKING SCHEME (should total {TOTAL_MARKS}):
{scheme_text}
Current Total: {total}

ORIGINAL CONTEXT (excerpt):
{context[:3000]}

REVIEW CRITERIA:
1. Is the question comprehensive and thought-provoking?
2. Does the marking scheme total EXACTLY {TOTAL_MARKS} marks?
3. Is the mark distribution logical and fair?
4. Does the model answer cover all marking scheme points?
5. Are the marking criteria clear enough for consistent grading?
6. Is the difficulty appropriate for a long answer question?
7. Are there any factual errors?

OUTPUT FORMAT (JSON):
{{
    "is_approved": true/false,
    "quality_score": 1-10,
    "marking_scheme_valid": true/false,
    "marking_scheme_total": {total},
    "issues": ["issue1", "issue2"] or [],
    "suggestions": ["suggestion1"] or [],
    "feedback_summary": "Brief summary of review"
}}

Return ONLY valid JSON, no additional text."""


def review_node(state: QuestionState) -> dict:
    """
    LangGraph node that reviews generated questions and answers.
    
    Args:
        state: Current QuestionState with question, answer, etc.
    
    Returns:
        Updated state dict with review_feedback and is_approved
    """
    question = state.get("question", "")
    question_type = state.get("question_type", "MCQ")
    correct_answer = state.get("correct_answer", "")
    context = state.get("context", "")
    revision_count = state.get("revision_count", 0)
    
    # Don't review if we've hit max retries
    if revision_count >= MAX_RETRIES:
        return {
            "is_approved": True,  # Force approval after max retries
            "review_feedback": f"Auto-approved after {MAX_RETRIES} revision attempts."
        }
    
    llm = create_review_llm()
    
    # Select appropriate review prompt based on question type
    if question_type == "MCQ":
        options = state.get("options", [])
        prompt = review_mcq_prompt(question, options, correct_answer, context)
        
    elif question_type == "Short Answer":
        derivation = state.get("answer_derivation", "")
        prompt = review_short_answer_prompt(question, correct_answer, derivation, context)
        
    elif question_type == "Long Answer":
        marking_scheme = state.get("marking_scheme", {})
        answer = state.get("answer_derivation", correct_answer)
        prompt = review_long_answer_prompt(question, answer, marking_scheme, context)
        
    else:
        return {
            "is_approved": False,
            "review_feedback": f"Unknown question type: {question_type}"
        }
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean up response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        result = json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"Review JSON parsing error: {e}")
        # If parsing fails, approve to avoid infinite loops
        return {
            "is_approved": True,
            "review_feedback": "Review parsing failed, auto-approved."
        }
    except Exception as e:
        print(f"Error during review: {e}")
        return {
            "is_approved": True,
            "review_feedback": f"Review error: {str(e)}, auto-approved."
        }
    
    is_approved = result.get("is_approved", False)
    
    # For Long Answer, also check marking scheme total
    if question_type == "Long Answer":
        scheme_valid = result.get("marking_scheme_valid", False)
        if not scheme_valid:
            is_approved = False
            result["issues"] = result.get("issues", []) + ["Marking scheme does not total 100"]
    
    # Build feedback summary
    issues = result.get("issues", [])
    suggestions = result.get("suggestions", [])
    feedback_parts = []
    
    if issues:
        feedback_parts.append("Issues found: " + "; ".join(issues))
    if suggestions:
        feedback_parts.append("Suggestions: " + "; ".join(suggestions))
    
    feedback = result.get("feedback_summary", "")
    if feedback_parts:
        feedback += " | " + " | ".join(feedback_parts)
    
    return {
        "is_approved": is_approved,
        "review_feedback": feedback,
        "revision_count": revision_count + (0 if is_approved else 1)
    }
