import json
import os
import tomllib
from state import DocumentState
from typing import Dict, List, Any
from utils import extract_organization_letter, get_process_filename


def identify_gaps(state: DocumentState) -> DocumentState:
    """
    Node to identify gaps between current OLIMP answers and maximum level E
    for specific sections: TECHNOLOGIA I INFRASTRUKTURA, LUDZIE I KOMPETENCJE, ORGANIZACJA I PROCESY
    
    Args:
        state: The current state containing answers
        
    Returns:
        Updated state with gaps analysis
    """
    # Load target sections from configuration
    try:
        with open("./config/areas_for_improvement.toml", "rb") as f:
            config = tomllib.load(f)
        target_sections = config["gap_analysis"]["target_sections"]
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Fallback to hardcoded sections
        target_sections = [
            "TECHNOLOGIA I INFRASTRUKTURA",
            "LUDZIE I KOMPETENCJE", 
            "ORGANIZACJA I PROCESY"
        ]
    
    # Answer level progression mapping
    level_progression = {
        'A': ['B', 'C', 'D', 'E'],
        'B': ['C', 'D', 'E'],
        'C': ['D', 'E'],
        'D': ['E'],
        'E': []  # Already at maximum
    }
    
    gaps = {}
    
    # Check if answers exist and contain OLIMP data
    if not state.get("answers") or "OLIMP" not in state["answers"]:
        print("No OLIMP answers found in state")
        return {
            **state,
            "gaps": {}
        }
    
    olimp_data = state["answers"]["OLIMP"]
    
    # Check if sections exist
    if "sections" not in olimp_data:
        print("No sections found in OLIMP data")
        return {
            **state,
            "gaps": {}
        }
    
    # Process each target section
    for section in olimp_data["sections"]:
        section_name = section.get("section_name", "")
        
        if section_name in target_sections:
            gaps[section_name] = {}
            
            # Process each question in the section
            for question in section.get("questions", []):
                question_text = question.get("question_text", "")
                selected_answer = question.get("selected_answer", "")
                answer_options = question.get("answer_options", {})
                
                if selected_answer and selected_answer in level_progression:
                    steps_to_e = level_progression[selected_answer]
                    
                    # Get verbose descriptions for present state and steps
                    present_verbose = answer_options.get(selected_answer, "")
                    steps_verbose = []
                    for step in steps_to_e:
                        step_verbose = answer_options.get(step, "")
                        steps_verbose.append({
                            "level": step,
                            "description": step_verbose
                        })
                    
                    gaps[section_name][question_text] = {
                        "present": {
                            "level": selected_answer,
                            "description": present_verbose
                        },
                        "steps": steps_verbose
                    }
    
    # Print essential summary
    total_questions = sum(len(section_gaps) for section_gaps in gaps.values())
    print(f"Gaps analysis completed: {total_questions} questions across {len(gaps)} sections")
    
    # Save gaps to JSON file
    # Determine the output filename based on organization letter
    org_letter = extract_organization_letter()
    output_filename = get_process_filename("gaps.json", org_letter)
    
    output_path = f"./data/process/{output_filename}"
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(gaps, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error saving gaps to file: {e}")
    
    # Update state with gaps
    return {
        **state,
        "gaps": gaps
    }