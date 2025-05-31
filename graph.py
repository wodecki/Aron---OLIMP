import os
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from state import DocumentState
from nodes.extract_answers import extract_answers

# Load environment variables if needed
try:
    load_dotenv(override=True)
except ImportError:
    print("dotenv not installed, skipping environment variable loading")

def create_graph():
    """
    Create a simple document processing graph with one node:
    1. extract_answers - Read PDF files and extract questionnaire data using Gemini
    
    Returns:
        Compiled graph
    """
    # Create the graph
    graph_builder = StateGraph(DocumentState)
    
    # Add node
    graph_builder.add_node("extract_answers", extract_answers)
    
    # Add edges for simple flow
    graph_builder.add_edge(START, "extract_answers")
    graph_builder.add_edge("extract_answers", END)
    
    # Compile the graph
    return graph_builder.compile()

# Create the graph
app = create_graph()
