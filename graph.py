import os
from typing import Literal
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from state import DocumentState
from nodes.extract_answers import extract_answers
from nodes.identify_gaps import identify_gaps
from nodes.recommend import recommend
from nodes.evaluation import evaluation

# Load environment variables if needed
try:
    load_dotenv(override=True)
except ImportError:
    print("dotenv not installed, skipping environment variable loading")

def should_continue_evaluation(state: DocumentState) -> Literal["recommend", END]:
    """
    Conditional edge function to determine if evaluation should continue or end.
    
    Returns:
        "recommend" if recommendations need revision
        END if recommendations are approved or max iterations reached
    """
    # Check if recommendations are approved
    if state.get("recommendation_approved", False):
        print("✅ Recommendations approved - ending evaluation loop")
        return END
    
    # Check iteration limit (safety mechanism)
    max_iterations = 3
    current_iterations = state.get("evaluation_iterations", 0)
    
    if current_iterations >= max_iterations:
        print(f"⚠️ Maximum iterations ({max_iterations}) reached - ending evaluation loop")
        return END
    
    print(f"🔄 Revision needed - returning to recommend node (iteration {current_iterations + 1})")
    return "recommend"

def create_graph():
    """
    Create a document processing graph with evaluation loop:
    1. extract_answers - Read PDF files and extract questionnaire data using Gemini
    2. identify_gaps - Analyze gaps between current OLIMP answers and maximum level E
    3. recommend - Generate recommendations for smooth transition to level E using configurable LLM
    4. evaluation - Evaluate recommendations using OpenAI o3 and provide feedback
    
    The graph includes an evaluation loop between recommend and evaluation nodes,
    similar to the writer-editor pattern in ref_evaluation.py
    
    Returns:
        Compiled graph
    """
    # Create the graph
    graph_builder = StateGraph(DocumentState)
    
    # Add nodes
    graph_builder.add_node("extract_answers", extract_answers)
    graph_builder.add_node("identify_gaps", identify_gaps)
    graph_builder.add_node("recommend", recommend)
    graph_builder.add_node("evaluation", evaluation)
    
    # Add edges for sequential flow with evaluation loop
    graph_builder.add_edge(START, "extract_answers")
    graph_builder.add_edge("extract_answers", "identify_gaps")
    graph_builder.add_edge("identify_gaps", "recommend")
    graph_builder.add_edge("recommend", "evaluation")
    
    # Conditional edge for evaluation loop
    graph_builder.add_conditional_edges(
        "evaluation",
        should_continue_evaluation,
        {
            "recommend": "recommend",  # Go back to recommend for revision
            END: END  # End if approved or max iterations reached
        }
    )
    
    # Compile the graph
    return graph_builder.compile()

# Create the graph with evaluation loop
app = create_graph()
