import os
import json
import tomllib
from pathlib import Path
import google.generativeai as genai
from state import DocumentState


def recommend(state: DocumentState) -> DocumentState:
    """
    Node to generate recommendations based on gaps analysis using Gemini
    
    Args:
        state: The current state containing gaps analysis
        
    Returns:
        Updated state with recommendation report
    """
    print("Generating recommendations based on gaps analysis...")
    
    # Check if gaps exist
    if not state.get("gaps"):
        print("No gaps found in state - skipping recommendations")
        return state
    
    try:
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06"))
        
        # Load recommendation prompt from config
        try:
            with open("./config/prompts.toml", "rb") as f:
                prompts_config = tomllib.load(f)
            
            if "recommend" not in prompts_config or "recommendation_prompt" not in prompts_config["recommend"]:
                print("Error: recommendation_prompt not found in config/prompts.toml")
                return state
            
            recommendation_prompt = prompts_config["recommend"]["recommendation_prompt"]
                
        except Exception as e:
            print(f"Error loading prompt config: {e}")
            return state
        
        # Load supplementary questionnaire answers for context
        supplementary_answers = None
        try:
            with open("./data/process/A_1.json", "r", encoding="utf-8") as f:
                supplementary_answers = json.load(f)
            print("Loaded supplementary questionnaire data (A_1.json) for context")
        except FileNotFoundError:
            print("A_1.json not found - proceeding without supplementary context")
        except Exception as e:
            print(f"Error loading A_1.json: {e} - proceeding without supplementary context")
        
        # Format gaps data and supplementary context as JSON strings for the prompt
        gaps_json = json.dumps(state["gaps"], ensure_ascii=False, indent=2)
        
        if supplementary_answers:
            supplementary_json = json.dumps(supplementary_answers, ensure_ascii=False, indent=2)
            formatted_prompt = recommendation_prompt.format(
                gaps_data=gaps_json,
                supplementary_context=supplementary_json
            )
        else:
            # If no supplementary data, format prompt without it
            formatted_prompt = recommendation_prompt.format(
                gaps_data=gaps_json,
                supplementary_context="Brak dodatkowych danych z kwestionariusza."
            )
        
        print("Generating recommendations with Gemini...")
        
        # Generate recommendations using Gemini
        response = model.generate_content(formatted_prompt)
        
        if not response.text:
            print("Error: No response from Gemini")
            return state
            
        # Clean the response - remove markdown code block markers if present
        recommendation_report = response.text.strip()
        if recommendation_report.startswith('```markdown'):
            recommendation_report = recommendation_report[11:]
        if recommendation_report.startswith('```'):
            recommendation_report = recommendation_report[3:]
        if recommendation_report.endswith('```'):
            recommendation_report = recommendation_report[:-3]
        recommendation_report = recommendation_report.strip()
        
        # Determine output filename based on main file
        output_filename = "A_recommendations.md"  # Default
        if os.path.exists("./data/process/A.json"):
            output_filename = "A_recommendations.md"
        
        # Ensure reports directory exists
        reports_dir = "./data/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save report to markdown file
        output_path = f"{reports_dir}/{output_filename}"
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(recommendation_report)
            print(f"Recommendations saved to {output_path}")
        except Exception as e:
            print(f"Error saving recommendations: {e}")
            return state
        
        print("Recommendations generated successfully")
        
        return state
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return state