from typing import TypedDict, Dict, Any, Optional, Annotated
from operator import add

def merge_branch_data(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Custom reducer for merging branch-specific data"""
    result = left.copy() if left else {}
    if right:
        result.update(right)
    return result

class DocumentState(TypedDict):
    """State for document processing with parallel execution support"""
    # Shared state (read-only after identify_gaps)
    document_content: str
    answers: Dict[str, Any]
    gaps: Dict[str, Any]
    
    # Branch-specific data using custom reducer to handle parallel updates
    branch_data: Annotated[Dict[str, Any], merge_branch_data]
    
    # Consensus state
    consensus_recommendation: Optional[str]  # Final synthesized recommendation
    
    # Legacy fields (for backward compatibility)
    recommendations: Optional[str]
    evaluation_feedback: Optional[str]
    evaluation_iterations: int
    recommendation_approved: bool
