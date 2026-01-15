"""
Question Generator Agent - Creates questions based on type and difficulty.

Handles:
- MCQ: Question + Options + Correct Answer
- Short Answer: Question + Correct Answer + Derivation
- Long Answer: Question + Correct Answer + Marking Scheme (100 points)
"""
import json
from langchain_openai import ChatOpenAI

from ..config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    MODEL_NAME, 
    TEMPERATURE,
    TOTAL_MARKS,
    DEFAULT_NUM_OPTIONS
)
from ..state import QuestionState


def create_question_llm() -> ChatOpenAI:
    """Create the LLM instance for question generation."""
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=TEMPERATURE,
    )


def generate_mcq_prompt(context: str, difficulty: str, num_options: int, topic: str) -> str:
    """Generate prompt for MCQ question creation."""
    return f"""You are an expert educational question generator. Create a {difficulty} difficulty Multiple Choice Question (MCQ) based on the following context.

CONTEXT:
{context[:8000]}

TOPIC FOCUS: {topic}

REQUIREMENTS:
1. Create exactly ONE question appropriate for {difficulty} difficulty level
2. Generate exactly {num_options} options (labeled A, B, C, D, etc.)
3. Only ONE option should be correct
4. Distractors should be plausible but clearly incorrect
5. The question should test understanding, not just memorization
6. If the question involves graphs or mathematical relationships, describe what graph would be needed

OUTPUT FORMAT (JSON):
{{
    "question": "The question text here",
    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
    "correct_answer": "A",
    "correct_answer_full": "A. Option 1",
    "explanation": "Brief explanation of why this is correct",
    "needs_graph": false,
    "graph_description": null
}}

Return ONLY valid JSON, no additional text."""


def generate_short_answer_prompt(context: str, difficulty: str, topic: str) -> str:
    """Generate prompt for Short Answer question creation."""
    return f"""You are an expert educational question generator. Create a {difficulty} difficulty Short Answer question based on the following context.

CONTEXT:
{context[:8000]}

TOPIC FOCUS: {topic}

REQUIREMENTS:
1. Create exactly ONE short answer question appropriate for {difficulty} difficulty
2. The answer should be concise (1-3 sentences or a specific value/term)
3. Provide step-by-step derivation of how to arrive at the answer
4. The question should test understanding and application
5. If the question involves graphs or calculations, describe what would be needed

OUTPUT FORMAT (JSON):
{{
    "question": "The question text here",
    "correct_answer": "The concise correct answer",
    "answer_derivation": "Step 1: ...\\nStep 2: ...\\nStep 3: ...",
    "key_concepts": ["concept1", "concept2"],
    "needs_graph": false,
    "graph_description": null
}}

Return ONLY valid JSON, no additional text."""


def generate_long_answer_prompt(context: str, difficulty: str, topic: str) -> str:
    """Generate prompt for Long Answer question creation with marking scheme."""
    return f"""You are an expert educational question generator. Create a {difficulty} difficulty Long Answer question with a detailed marking scheme based on the following context.

CONTEXT:
{context[:8000]}

TOPIC FOCUS: {topic}

REQUIREMENTS:
1. Create exactly ONE comprehensive long answer question for {difficulty} difficulty
2. The question should require a detailed response (multiple paragraphs or steps)
3. Create a marking scheme that totals EXACTLY {TOTAL_MARKS} marks
4. Break down marks into logical components (introduction, main points, conclusion, etc.)
5. The question should test deep understanding and analytical skills

OUTPUT FORMAT (JSON):
{{
    "question": "The detailed question text here",
    "correct_answer": "A model answer covering all marking scheme points",
    "marking_scheme": {{
        "Introduction and context (define key terms)": 10,
        "Main concept explanation 1": 25,
        "Main concept explanation 2": 25,
        "Application or example": 20,
        "Diagram/illustration if applicable": 10,
        "Conclusion": 10
    }},
    "total_marks": {TOTAL_MARKS},
    "key_points": ["point1", "point2", "point3"],
    "needs_graph": false,
    "graph_description": null
}}

CRITICAL: The marking_scheme values MUST sum to exactly {TOTAL_MARKS}.

Return ONLY valid JSON, no additional text."""


def question_generator_node(state: QuestionState) -> dict:
    """
    LangGraph node that generates questions based on type and difficulty.
    """
    context = state.get("context", "")
    difficulty = state.get("difficulty", "Medium")
    question_type = state.get("question_type", "MCQ")
    num_options = state.get("num_options", DEFAULT_NUM_OPTIONS)
    topic = state.get("topic", "General")
    revision_count = state.get("revision_count", 0)
    review_feedback = state.get("review_feedback", "")
    output_folder = state.get("output_folder", "")
    
    llm = create_question_llm()
    
    # Select appropriate prompt based on question type
    if question_type == "MCQ":
        prompt = generate_mcq_prompt(context, difficulty, num_options, topic)
    elif question_type == "Short Answer":
        prompt = generate_short_answer_prompt(context, difficulty, topic)
    elif question_type == "Long Answer":
        prompt = generate_long_answer_prompt(context, difficulty, topic)
    else:
        return {"question": f"Unknown question type: {question_type}"}
    
    # Add revision context
    if revision_count > 0 and review_feedback:
        prompt += f"\n\nPREVIOUS FEEDBACK (please address these issues):\n{review_feedback}"
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean up response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        # Parse JSON response
        result = json.loads(content)
        
    except Exception as e:
        print(f"Error generating question: {e}")
        return {
            "question": f"Error: {str(e)}",
            "revision_count": revision_count + 1
        }
    
    # Build output based on question type
    output = {
        "question": result.get("question", ""),
        "correct_answer": result.get("correct_answer", ""),
        "revision_count": revision_count
    }
    
    # Handle Graph Options specifically for MCQ
    if question_type == "MCQ" and result.get("graph_options") and output_folder:
        graph_options = result.get("graph_options")
        image_options = []
        
        for i, opt in enumerate(graph_options):
            label = opt.get("label", str(i+1))
            g_type = opt.get("type")
            path = Path(output_folder) / f"option_{label}.png"
            
            try:
                if g_type == "linear":
                    generate_linear_graph(
                        m=opt.get("m", 1), 
                        c=opt.get("c", 0), 
                        output_path=str(path),
                        title=f"Option {label}"
                    )
                elif g_type == "quadratic":
                    generate_quadratic_graph(
                        a=opt.get("a", 1),
                        b=opt.get("b", 0),
                        c=opt.get("c", 0),
                        output_path=str(path),
                        title=f"Option {label}"
                    )
                
                # Add markdown image link as option
                image_options.append(f"**{label}.** ![{label}]({path.name})")
            except Exception as e:
                print(f"Failed to generate graph for option {label}: {e}")
                image_options.append(f"**{label}.** [Graph Generation Failed]")
        
        if image_options:
            output["options"] = image_options
    
    if question_type == "MCQ" and "options" not in output:
        output["options"] = result.get("options", [])
        output["answer_derivation"] = result.get("explanation", "")
        
    elif question_type == "Short Answer":
        output["answer_derivation"] = result.get("answer_derivation", "")
        
    elif question_type == "Long Answer":
        output["marking_scheme"] = result.get("marking_scheme", {})
        output["answer_derivation"] = result.get("correct_answer", "")
    
    # Check if graph is needed for Question itself
    if result.get("needs_graph") and result.get("graph_description"):
        output["graph_description"] = result.get("graph_description")
    
    return output
