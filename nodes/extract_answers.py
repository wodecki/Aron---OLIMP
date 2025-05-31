import os
from docx import Document
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from state import DocumentState

def extract_answers(state: DocumentState) -> DocumentState:
    """
    Node to read DOCX file and summarize it using GPT-4o-mini
    
    Args:
        state: The current state
        
    Returns:
        Updated state with document content and summary
    """
    print("Reading DOCX file...")
    
    # Read the DOCX file
    doc_path = "./data/input/B.docx"
    
    try:
        doc = Document(doc_path)
        
        # Extract text from all paragraphs
        document_text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                document_text += paragraph.text + "\n"
        
        print(f"Document loaded successfully. Length: {len(document_text)} characters")
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create summarization prompt
        prompt = f"""Please provide a concise summary of the following document:

{document_text}

Summary:"""
        
        print("Generating summary with GPT-4o-mini...")
        
        # Get summary from LLM
        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
        
        print("Summary generated successfully")
        
        # Update state
        return {
            **state,
            "document_content": document_text,
            "summary": summary
        }
        
    except Exception as e:
        print(f"Error processing document: {e}")
        return {
            **state,
            "document_content": f"Error reading document: {e}",
            "summary": f"Could not generate summary due to error: {e}"
        }
