from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

from src.question_generator.config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_NAME, 
    TEMPERATURE
)
from .state import GraderState

def create_grader_llm() -> ChatOpenAI:
    """Create the LLM instance for grading."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set in the environment.")
        
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=TEMPERATURE,
    )

def grading_node(state: GraderState) -> dict:
    """
    Grades the short answer provided by the student.
    
    Args:
        state: The current GraderState containing question, student_answer, correct_answer.
        
    Returns:
        Updated state with assigned_score, feedback, and confidence.
    """
    llm = create_grader_llm()
    
    prompt_text = """
    You are an expert academic grader. Your task is to grade a student's short answer based on a model answer and the question provided.
    
    Question: {question}
    Max Score: {max_score}
    
    Model Answer (Correct):
    {correct_answer}
    
    Student Answer:
    {student_answer}
    
    Instructions:
    1. Compare the Student Answer to the Model Answer.
    2. Determine if the student's answer captures the core meaning and necessary details of the model answer.
    3. Use your judgment to assign a score from 0 to {max_score} (integer only).
    4. Provide constructive feedback explaining why points were given or deducted.
    5. Estimate your confidence in this grading (0.0 to 1.0).
    
    Output Format:
    Return valid JSON ONLY with the following keys:
    {{
        "assigned_score": <int>,
        "feedback": "<string>",
        "confidence": <float>
    }}
    """
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "question": state.get("question", ""),
            "max_score": state.get("max_score", 10),
            "correct_answer": state.get("correct_answer", ""),
            "student_answer": state.get("student_answer", "")
        })
        
        content = response.content.strip()
        # Clean up code blocks if present
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        result = json.loads(content)
        
        return {
            "assigned_score": result.get("assigned_score", 0),
            "feedback": result.get("feedback", "No feedback provided."),
            "confidence": result.get("confidence", 0.0)
        }
        
    except Exception as e:
        print(f"Error during grading: {e}")
        return {
            "assigned_score": 0,
            "feedback": f"Error during grading process: {str(e)}",
            "confidence": 0.0
        }
