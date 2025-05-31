import os
import sys
import traceback

# Import the application
from graph import app

def main():
    """
    Main function to run the document summarization process
    """
    print("Starting document summarization process...")
    
    # Initialize empty state
    initial_state = {
        "document_content": "",
        "summary": ""
    }
    
    # Invoke the app with the initial state
    try:
        response = app.invoke(initial_state)
        
        # Print the results
        print("=" * 50)
        print("DOCUMENT SUMMARIZATION COMPLETE")
        print("=" * 50)
        
        print("\nDocument Content:")
        print("-" * 20)
        print(response["document_content"][:500] + "..." if len(response["document_content"]) > 500 else response["document_content"])
        
        print("\nSummary:")
        print("-" * 20)
        print(response["summary"])
        
        # Save summary to file
        summary_path = "data/results/summary.txt"
        
        # Ensure the results directory exists
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"Document Summary\n")
            f.write(f"================\n\n")
            f.write(f"Original Document Length: {len(response['document_content'])} characters\n\n")
            f.write(f"Summary:\n")
            f.write(f"{response['summary']}\n\n")
            f.write(f"Full Document Content:\n")
            f.write(f"{response['document_content']}")
        
        print(f"\nSummary saved to {summary_path}")
        
    except Exception as e:
        error_msg = f"Error running the summarization: {e}"
        print(error_msg)
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
