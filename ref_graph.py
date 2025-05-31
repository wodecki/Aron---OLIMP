import os
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
from state import ExamState
from nodes.ref_extract_exam import extract_exam
from nodes.read_exam import read_exam
from nodes.evaluate_12 import evaluate as evaluate_12
from nodes.evaluate_3 import evaluate as evaluate_3
from nodes.ref_generate_report import generate_report

# Load environment variables if needed
try:
    load_dotenv(override=True)
except ImportError:
    print("dotenv not installed, skipping environment variable loading")

def create_graph():
    """
    Create the exam evaluation graph with five nodes in sequential order:
    1. extract_exam - Extract exam content from PDF using OCR
    2. read_exam - Read exam content and criteria
    3. evaluate_12 - Evaluate exam answers for tasks 1 and 2
    4. evaluate_3 - Evaluate essay (Zadanie 9)
    5. generate_report - Generate evaluation report
    
    Returns:
        Compiled graph
    """
    # Create the graph
    graph_builder = StateGraph(ExamState)
    
    # Add nodes
    graph_builder.add_node("extract_exam", extract_exam)
    graph_builder.add_node("read_exam", read_exam)
    graph_builder.add_node("evaluate_12", evaluate_12)
    graph_builder.add_node("evaluate_3", evaluate_3)
    graph_builder.add_node("generate_report", generate_report)
    
    # Add edges for sequential flow
    graph_builder.add_edge(START, "extract_exam")
    graph_builder.add_edge("extract_exam", "read_exam")
    graph_builder.add_edge("read_exam", "evaluate_12")
    graph_builder.add_edge("evaluate_12", "evaluate_3")
    graph_builder.add_edge("evaluate_3", "generate_report")
    graph_builder.add_edge("generate_report", END)
    
    # Compile the graph
    return graph_builder.compile()

# Create the graph
app = create_graph()

# Graph visualization removed