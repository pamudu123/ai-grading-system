# Question Generator System - Design Considerations

## 1. Architecture Overview
The system implements a **multi-agent workflow using LangGraph** to generate high-quality educational questions. It is designed to be modular, scalable, and verifiable.

### 1.1 Diagram
```mermaid
graph TD
    Start[User Inputs] --> ContextNode
    ContextNode[Context Retrieval Agent] -->|State + Context| GenNode
    GenNode[Question Generator Agent] -->|Draft Question| ReviewNode
    ReviewNode[Review Agent] -->|Feedback| Check{Approved?}
    Check -->|No (Retry)| GenNode
    Check -->|Yes| Output[Final Output]
```

## 2. Core Components

### 2.1 Agents
1.  **Context Retrieval Agent (`context_agent.py`)**
    *   **Role:** Identify and fetch relevant subject matter.
    *   **Logic:** Reads `doc_info.yaml` to locate markdown files. Extracts specific topics based on the subject (e.g., "Physics" -> "Mechanics").
    *   **Design Decision:** Direct file reading is used for simplicity and accuracy over vector databases for this scope.

2.  **Question Generator Agent (`question_agent.py`)**
    *   **Role:** Create questions (MCQ, Short, Long) based on context and difficulty.
    *   **Features:**
        *   **MCQ:** Supports 2-6 options. Capable of generating **Graph Options** (linear/quadratic plots) upon request.
        *   **Short Answer:** Includes step-by-step derivation for verifyability.
        *   **Long Answer:** Generates a detailed 100-point marking scheme.
    *   **Tool Usage:** Uses `graph_generator` for plotting options but relies on **LLM reasoning** for calculations (Calculator tool explicitly disabled).

3.  **Review Agent (`review_agent.py`)**
    *   **Role:** QA gatekeeper. Transforms the "Draft" into "Final".
    *   **Criteria:** Checks for correctness, clarty, adherence to curriculum, and marking scheme validity.
    *   **Feedback Loop:** Returns specific feedback to the Generator if rejected, enabling iterative improvement.

### 2.2 State Management
*   **`QuestionState` (TypedDict):** Shared state object passed between nodes.
*   **Persistence:** The state carries `iteration_id`, `input` parameters, `generated_artifacts` (paths to images), and `review_history`.

## 3. Tooling & Constraints

### 3.1 Graph Generation
*   **Library:** `matplotlib` (via `tools/graph_generator.py`).
*   **Capabilities:**
    *   Linear Graphs (`y = mx + c`)
    *   Quadratic Graphs (`y = ax^2 + bx + c`)
    *   Custom Plotting
*   **Integration:** Images are saved as PNGs in the iteration folder and embedded in Markdown via relative links.

### 3.2 Disabled Tools (Safety & Policy)
As per strict design requirements:
*   **Python Interpreter:** ❌ **DISABLED/COMMENTED OUT**. Code execution functionality is limited to specific, safe graph generation functions.
*   **Calculator:** ❌ **DISABLED/COMMENTED OUT**. Math logic must be performed by the model's internal reasoning or pre-defined logic.

## 4. Data Flow & Output

### 4.1 Input Configuration
*   **`config.py`:** Centralized configuration for API keys (`OPENROUTER_API_KEY`), model selection (`gemini-2.0-flash`), and paths.
*   **`doc_info.yaml`:** Registry of available subject content.

### 4.2 Output Structure
Each run creates a unique, timestamped directory:
```
output/questions/YYYYMMDD_HHMMSS/
├── mcq_question.md        # The final question
├── generation_summary.json # Meta-data (metrics, feedback)
├── option_A.png           # (Optional) Generated graph asset
└── option_B.png           # (Optional) Generated graph asset
```

## 5. Implementation Decisions

1.  **Format Enforcing:** Agents are prompted to return strict JSON to ensure reliable parsing by the system.
2.  **Plugin-Style Graphs:** Graph options are generated as separate files and "plugged in" to the text content, separating the *content generation* (LLM) from the *asset creation* (Python).
3.  **Prompt Engineering:**
    *   **MCQ:** Enforced "plausible distractors".
    *   **Long Answer:** Enforced "EXACTLY 100 marks" constraint for marking schemes.
    *   **Short Answer:** Enforced "Derivation steps" for transparency.

## 6. Future Considerations
*   **Vector Search:** For larger document sets, replace direct file reading with RAG (Retrieval Augmented Generation).
*   **Dynamic Topics:** Allow user to specify sub-topics (e.g., "Thermodynamics") directly in `input`.
*   **PDF Support:** Integrate the PDF conversion pipeline directly into the loop (currently separate).