import os
import json
import tomllib
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from state import DocumentState

# Load environment variables
load_dotenv()

# Maximum number of evaluation iterations
MAX_EVALUATION_ITERATIONS = 3
# Minimum score threshold for approval (out of 100)
MIN_APPROVAL_SCORE = 80

def evaluation(state: DocumentState) -> DocumentState:
    """
    Node to evaluate recommendation reports using OpenAI o3
    
    Args:
        state: The current state containing recommendations
        
    Returns:
        Updated state with evaluation feedback and approval status
    """
    print("Evaluating recommendation report...")
    
    # Check if recommendations exist
    if not state.get("recommendations"):
        print("No recommendations found in state - skipping evaluation")
        return state
    
    # Initialize evaluation metadata if not present
    if "evaluation_iterations" not in state:
        state["evaluation_iterations"] = 0
    if "recommendation_approved" not in state:
        state["recommendation_approved"] = False
    
    try:
        # Initialize OpenAI o3 model for evaluation
        model_name = os.getenv("OPENAI_MODEL", "o3-2025-04-16")
        
        # o3 models don't support custom temperature, use default
        if "o3" in model_name:
            evaluator_llm = ChatOpenAI(
                model=model_name,
                # o3 models only support default temperature (1)
                max_tokens=None,
                timeout=None,
                max_retries=2,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            evaluator_llm = ChatOpenAI(
                model=model_name,
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=None,
                timeout=None,
                max_retries=2,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
        print(f"Initialized OpenAI evaluator: {os.getenv('OPENAI_MODEL', 'o3-2025-04-16')}")
        
        # Load evaluation prompt from config
        try:
            with open("./config/prompts.toml", "rb") as f:
                prompts_config = tomllib.load(f)
            
            if "evaluate" not in prompts_config or "evaluation_prompt" not in prompts_config["evaluate"]:
                print("Error: evaluation_prompt not found in config/prompts.toml")
                return state
            
            evaluation_prompt = prompts_config["evaluate"]["evaluation_prompt"]
                
        except Exception as e:
            print(f"Error loading evaluation prompt config: {e}")
            return state
        
        # Prepare evaluation context
        gaps_context = json.dumps(state.get("gaps", {}), ensure_ascii=False, indent=2)
        
        # Load supplementary context if available
        supplementary_context = ""
        try:
            with open("./data/process/A_1.json", "r", encoding="utf-8") as f:
                supplementary_data = json.load(f)
                supplementary_context = json.dumps(supplementary_data, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            supplementary_context = "Brak dodatkowych danych z kwestionariusza."
        except Exception as e:
            print(f"Warning: Error loading supplementary context: {e}")
            supplementary_context = "Brak dodatkowych danych z kwestionariusza."
        
        # Format the evaluation prompt
        formatted_prompt = evaluation_prompt.format(
            recommendations_report=state["recommendations"],
            original_gaps_data=gaps_context,
            original_supplementary_context=supplementary_context
        )
        
        print(f"Conducting evaluation (iteration {state['evaluation_iterations'] + 1})...")
        
        # Create message for evaluation
        message = HumanMessage(content=formatted_prompt)
        
        # Generate evaluation using OpenAI o3
        response = evaluator_llm.invoke([message])
        
        if not response.content:
            print("Error: No response from evaluation model")
            return state
        
        evaluation_feedback = response.content.strip()
        
        # Increment iteration counter
        state["evaluation_iterations"] += 1
        
        # Store evaluation feedback
        state["evaluation_feedback"] = evaluation_feedback
        
        # Parse evaluation result - look for approval indicators
        evaluation_lower = evaluation_feedback.lower()
        
        # Check for explicit approval/rejection keywords or score
        approved = False
        
        # Look for score patterns
        import re
        score_patterns = [
            r'łączny wynik.*?(\d+)/100',
            r'wynik.*?(\d+)/100',
            r'punktów.*?(\d+)/100',
            r'(\d+)/100\s*punktów'
        ]
        
        score = None
        for pattern in score_patterns:
            match = re.search(pattern, evaluation_lower)
            if match:
                score = int(match.group(1))
                break
        
        # Determine approval based on score or keywords
        if score is not None:
            approved = score >= MIN_APPROVAL_SCORE
            print(f"Evaluation score: {score}/100 (threshold: {MIN_APPROVAL_SCORE})")
        else:
            # Fallback to keyword detection
            approval_keywords = ["doskonały", "bardzo dobry", "akceptuję", "approved", "zatwierdzone"]
            rejection_keywords = ["wymaga poprawy", "niewystarczający", "revision_needed", "odrzucone"]
            
            if any(keyword in evaluation_lower for keyword in approval_keywords):
                approved = True
            elif any(keyword in evaluation_lower for keyword in rejection_keywords):
                approved = False
            else:
                # Default to approval if max iterations reached
                approved = state["evaluation_iterations"] >= MAX_EVALUATION_ITERATIONS
        
        state["recommendation_approved"] = approved
        
        if approved:
            print("✅ Recommendations APPROVED by evaluator")
        else:
            print(f"❌ Recommendations need revision (iteration {state['evaluation_iterations']}/{MAX_EVALUATION_ITERATIONS})")
        
        # Save detailed evaluation to file
        evaluation_filename = f"A_evaluation_iter_{state['evaluation_iterations']}.md"
        reports_dir = "./data/reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        evaluation_path = f"{reports_dir}/{evaluation_filename}"
        try:
            with open(evaluation_path, "w", encoding="utf-8") as f:
                f.write(f"# Evaluation Report - Iteration {state['evaluation_iterations']}\\n\\n")
                f.write(f"**Status**: {'APPROVED' if approved else 'REVISION_NEEDED'}\\n")
                if score is not None:
                    f.write(f"**Score**: {score}/100\\n")
                f.write(f"**Timestamp**: {Path().absolute()}\\n\\n")
                f.write("## Detailed Evaluation\\n\\n")
                f.write(evaluation_feedback)
            print(f"Evaluation saved to {evaluation_path}")
        except Exception as e:
            print(f"Warning: Could not save evaluation to file: {e}")
        
        print("Evaluation completed successfully")
        
        return state
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        # On error, approve after max iterations to prevent infinite loops
        if state.get("evaluation_iterations", 0) >= MAX_EVALUATION_ITERATIONS:
            state["recommendation_approved"] = True
            state["evaluation_feedback"] = f"Evaluation error after {MAX_EVALUATION_ITERATIONS} iterations. Auto-approved."
        return state