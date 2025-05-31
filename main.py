import os
import sys
import traceback

# Import the application
from graph import app

def main():
    """
    Main function to run the document processing process
    """
    print("Starting document processing process...")
    
    # Initialize empty state
    initial_state = {
        "document_content": "",
        "answers": {}
    }
    
    # Invoke the app with the initial state
    try:
        response = app.invoke(initial_state)
        
        # Print the results
        print("=" * 50)
        print("DOCUMENT PROCESSING COMPLETE")
        print("=" * 50)
        
        print("\nDocument Content:")
        print("-" * 20)
        print(response["document_content"][:500] + "..." if len(response["document_content"]) > 500 else response["document_content"])
        
    except Exception as e:
        error_msg = f"Error running the processing: {e}"
        print(error_msg)
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
