from typing import TypedDict, Dict, Any

class DocumentState(TypedDict):
    """State for document processing"""
    document_content: str
    answers: Dict[str, Any]
