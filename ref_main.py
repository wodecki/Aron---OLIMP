import os
import sys
import traceback
from pprint import pprint

# Import the application
from ref_graph import app
from logger import get_logger

# Get logger instance
logger = get_logger()

def main():
    """
    Main function to run the exam evaluation graph
    """
    # Get session information from environment variables
    upload_id = os.environ.get('UPLOAD_ID', 'unknown')
    session_start_time = os.environ.get('SESSION_START_TIME', 'unknown')
    
    logger.info(f"Starting exam evaluation process... [Session: {upload_id}, Started: {session_start_time}]")
    
    # Initialize empty state
    initial_state = {
        "exam_content": {},
        "criteria": {},
        "evaluation": {},
        "report": ""
    }
    
    # Invoke the app with the initial state
    try:
        response = app.invoke(initial_state)
        
        # Print the final report
        logger.info("=" * 50)
        logger.info("EVALUATION COMPLETE")
        logger.info("=" * 50)
        
        # Print the report
        print(response["report"])  # Keep this for console output
        logger.info("Report generated successfully")
        
        # Save report to file
        report_path = "data/results/evaluation_report.txt"
        
        # Ensure the results directory exists
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(response["report"])
        
        logger.info(f"Report saved to {report_path}")
        
    except Exception as e:
        error_msg = f"Error running the evaluation: {e}"
        logger.error(error_msg, exc_info=True)
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"Error running the evaluation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
