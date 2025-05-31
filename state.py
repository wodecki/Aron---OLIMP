from typing import TypedDict

class DocumentState(TypedDict):
    """State for document processing"""
    document_content: str
    summary: str
