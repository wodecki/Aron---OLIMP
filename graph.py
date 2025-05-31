import os
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from state import DocumentState
from nodes.extract_answers import extract_answers
from nodes.identify_gaps import identify_gaps
from nodes.recommend import recommend

# Load environment variables if needed
try:
    load_dotenv(override=True)
except ImportError:
    print("dotenv not installed, skipping environment variable loading")

def create_graph():
    """
    Create a document processing graph with three nodes:
    1. extract_answers - Read PDF files and extract questionnaire data using Gemini
    2. identify_gaps - Analyze gaps between current OLIMP answers and maximum level E
    3. recommend - Generate recommendations for smooth transition to level E using Gemini
    
    Returns:
        Compiled graph
    """
    # Create the graph
    graph_builder = StateGraph(DocumentState)
    
    # Add nodes
    graph_builder.add_node("extract_answers", extract_answers)
    graph_builder.add_node("identify_gaps", identify_gaps)
    graph_builder.add_node("recommend", recommend)
    
    # Add edges for sequential flow
    graph_builder.add_edge(START, "extract_answers")
    graph_builder.add_edge("extract_answers", "identify_gaps")
    graph_builder.add_edge("identify_gaps", "recommend")
    graph_builder.add_edge("recommend", END)
    
    # Compile the graph
    return graph_builder.compile()

# Create the graph
app = create_graph()
