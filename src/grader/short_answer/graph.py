from langgraph.graph import StateGraph, END

from .state import GraderState
from .agent import grading_node

def build_grader_graph() -> StateGraph:
    """
    Builds the LangGraph for short answer grading.
    """
    workflow = StateGraph(GraderState)
    
    workflow.add_node("grader", grading_node)
    
    workflow.set_entry_point("grader")
    workflow.add_edge("grader", END)
    
    return workflow.compile()
