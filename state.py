from typing import TypedDict, Dict, Any, Optional

class DocumentState(TypedDict):
    """State for document processing"""
    document_content: str
    answers: Dict[str, Any]
    gaps: Dict[str, Any]
    recommendations: Optional[str]  # Generated recommendation report
    evaluation_feedback: Optional[str]  # Feedback from evaluator
    evaluation_iterations: int  # Number of evaluation iterations
    recommendation_approved: bool  # Whether recommendations are approved
