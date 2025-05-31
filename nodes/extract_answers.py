import os
import json
import glob
from pathlib import Path
import google.generativeai as genai
from state import DocumentState

def extract_answers(state: DocumentState) -> DocumentState:
    """
    Node to read PDF files and extract sections, questions, and answers using Gemini 2.5 Pro
    
    Args:
        state: The current state
        
    Returns:
        Updated state with document content and extracted answers
    """
    print("Reading PDF files...")
    
    # Find all PDF files starting with A_
    pdf_pattern = "./data/input/A_*.pdf"
    pdf_files = glob.glob(pdf_pattern)
    pdf_files.sort()  # Ensure consistent order
    
    if not pdf_files:
        return {
            **state,
            "document_content": "No PDF files found matching pattern A_*.pdf",
            "summary": "No files to process"
        }
    
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06"))
        
        all_results = {}
        processed_files = []
        
        for pdf_path in pdf_files:
            print(f"Processing {pdf_path}...")
            
            # Determine questionnaire type based on filename
            filename = Path(pdf_path).stem  # e.g., "A_1" or "A_2"
            if filename.endswith("_1"):
                questionnaire_type = "CLIMB_2"
            elif filename.endswith("_2"):
                questionnaire_type = "OLIMP"
            else:
                questionnaire_type = "UNKNOWN"
            
            # Read PDF file as bytes
            with open(pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            
            print(f"PDF loaded successfully. Size: {len(pdf_data)} bytes")
            
            # Upload the PDF to Gemini
            pdf_file_obj = genai.upload_file(pdf_path, mime_type="application/pdf")
            
            print(f"PDF uploaded to Gemini. Extracting sections, questions, and answers...")
            
            # Create extraction prompt
            extraction_prompt = f"""Analyze this Polish questionnaire PDF document and extract the structure in JSON format.

The document contains sections (OBSZAR), questions (PYTANIA), and answers (ODPOWIEDZI) with options A, B, C, D, E.
The selected answers are marked with "X" or "V" marks in the document. Look carefully at the visual layout:
- Each row represents a question
- Columns A, B, C, D, E contain the answer options
- The "X" or "V" mark appears in the column corresponding to the selected answer

IMPORTANT: Pay close attention to which column contains the "X" or "V" mark for each question. This indicates the selected answer option.

Please extract:
1. Section names and their question counts
2. All questions within each section
3. All answer options (A, B, C, D, E) for each question
4. Which answer option is selected (marked with X or V) for each question - look carefully at the visual positioning

Return the data in this JSON structure:
{{
  "questionnaire": "{questionnaire_type}",
  "questionnaire_title": "title of the questionnaire",
  "sections": [
    {{
      "section_name": "name of the section",
      "question_count": number_of_questions,
      "questions": [
        {{
          "question_text": "the question text",
          "answer_options": {{
            "A": "option A text",
            "B": "option B text", 
            "C": "option C text",
            "D": "option D text",
            "E": "option E text"
          }},
          "selected_answer": "A/B/C/D/E"
        }}
      ]
    }}
  ]
}}

Extract the data as JSON, making sure to correctly identify which column (A, B, C, D, or E) contains the "X" or "V" mark for each question."""
            
            # Get structured data from Gemini
            response = model.generate_content([pdf_file_obj, extraction_prompt])
            
            try:
                # Clean the response content to extract JSON
                response_content = response.text.strip()
                
                # Find JSON content between code blocks or extract JSON directly
                if '```json' in response_content:
                    # Extract content between ```json and ```
                    start_idx = response_content.find('```json') + 7
                    end_idx = response_content.find('```', start_idx)
                    if end_idx != -1:
                        response_content = response_content[start_idx:end_idx]
                    else:
                        # If no closing ```, take everything after ```json
                        response_content = response_content[start_idx:]
                elif '```' in response_content:
                    # Handle case where it starts with ``` but not ```json
                    start_idx = response_content.find('```') + 3
                    end_idx = response_content.find('```', start_idx)
                    if end_idx != -1:
                        response_content = response_content[start_idx:end_idx]
                    else:
                        response_content = response_content[start_idx:]
                
                response_content = response_content.strip()
                
                # Try to find the JSON object boundaries if parsing fails
                if response_content.startswith('{'):
                    # Find the matching closing brace
                    brace_count = 0
                    for i, char in enumerate(response_content):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                response_content = response_content[:i+1]
                                break
                
                # Parse the JSON response
                extracted_data = json.loads(response_content)
                
                # Save individual file result
                individual_path = f"./data/process/{filename}.json"
                os.makedirs(os.path.dirname(individual_path), exist_ok=True)
                
                with open(individual_path, "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                
                print(f"Individual extraction saved to {individual_path}")
                
                # Store for integration
                questionnaire_key = questionnaire_type
                all_results[questionnaire_key] = extracted_data
                processed_files.append(pdf_path)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response for {pdf_path}: {e}")
                print("Raw response:", response.text[:500])
                
                # Save error response
                error_data = {"error": "Failed to parse JSON", "raw_response": response.text}
                individual_path = f"./data/process/{filename}.json"
                os.makedirs(os.path.dirname(individual_path), exist_ok=True)
                
                with open(individual_path, "w", encoding="utf-8") as f:
                    json.dump(error_data, f, ensure_ascii=False, indent=2)
                
                processed_files.append(f"{pdf_path} (ERROR)")
            
            # Clean up uploaded file
            try:
                genai.delete_file(pdf_file_obj.name)
            except:
                pass  # Ignore cleanup errors
        
        # Create integrated file (A.json)
        if all_results:
            integrated_path = "./data/process/A.json"
            with open(integrated_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            
            print(f"Integrated results saved to {integrated_path}")
        
        # Create summary
        total_questionnaires = len(all_results)
        total_sections = 0
        total_questions = 0
        
        for questionnaire_data in all_results.values():
            if "sections" in questionnaire_data:
                sections = questionnaire_data["sections"]
                total_sections += len(sections)
                for section in sections:
                    total_questions += section.get("question_count", 0)
        
        summary = f"""Processing Complete:

Files processed: {len(processed_files)}
- {', '.join(processed_files)}

Questionnaires extracted: {total_questionnaires}
Total sections: {total_sections}
Total questions: {total_questions}

Individual files saved in ./data/process/
Integrated file: ./data/process/A.json"""
        
        document_content = f"Processed {len(pdf_files)} PDF files with Gemini {os.getenv('GEMINI_MODEL')}"
        
        print("All extractions completed successfully")
        
        # Update state
        return {
            **state,
            "document_content": document_content,
            "summary": summary
        }
        
    except Exception as e:
        print(f"Error processing documents: {e}")
        return {
            **state,
            "document_content": f"Error reading PDFs: {e}",
            "summary": f"Could not extract answers due to error: {e}"
        }
