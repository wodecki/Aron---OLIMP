"""
Utility functions for dynamic file naming based on PDF input files
"""
import glob
import os
from pathlib import Path


def extract_organization_letter() -> str:
    """
    Extract the organization letter from PDF files in ./data/input/
    
    Returns:
        str: The first letter of PDF files (e.g., 'A', 'B', 'C', 'D')
             Defaults to 'A' if no matching files found
    """
    # Look for PDF files in the input directory
    pdf_pattern = "./data/input/*_*.pdf"
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print("Warning: No PDF files found in ./data/input/ - defaulting to 'A'")
        return 'A'
    
    # Extract the first letter from the first PDF file
    first_file = Path(pdf_files[0]).stem  # e.g., "A_1" or "B_2"
    letter = first_file.split('_')[0]  # Extract first part before underscore
    
    print(f"Detected organization letter: {letter}")
    return letter


def get_pdf_pattern(org_letter: str = None) -> str:
    """
    Get the PDF file pattern for the organization
    
    Args:
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: PDF file pattern (e.g., "./data/input/A_*.pdf")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"./data/input/{org_letter}_*.pdf"


def get_process_filename(base_name: str, org_letter: str = None) -> str:
    """
    Get process filename with organization prefix
    
    Args:
        base_name: Base filename (e.g., "gaps.json", "recommendations.md")
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Filename with organization prefix (e.g., "A_gaps.json")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_{base_name}"


def get_reports_filename(base_name: str, org_letter: str = None) -> str:
    """
    Get reports filename with organization prefix
    
    Args:
        base_name: Base filename (e.g., "recommendations.md")
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Filename with organization prefix (e.g., "A_recommendations.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_{base_name}"


def get_branch_filename(base_name: str, branch_suffix: str, provider: str, org_letter: str = None) -> str:
    """
    Get branch-specific filename with organization prefix
    
    Args:
        base_name: Base filename part (e.g., "recommendations", "evaluation")
        branch_suffix: Branch suffix ('A', 'B', 'C')
        provider: Provider name ('openai', 'anthropic', 'gemini')
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Full filename (e.g., "A_recommendations_branch_A_openai.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_{base_name}_branch_{branch_suffix}_{provider}.md"


def get_evaluation_filename(branch_suffix: str, provider: str, iteration: int, org_letter: str = None) -> str:
    """
    Get evaluation filename with organization prefix
    
    Args:
        branch_suffix: Branch suffix ('A', 'B', 'C')
        provider: Provider name ('openai', 'anthropic', 'gemini')
        iteration: Iteration number
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Full filename (e.g., "A_evaluation_branch_A_openai_iter_1.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_evaluation_branch_{branch_suffix}_{provider}_iter_{iteration}.md"


def get_final_branch_filename(branch_suffix: str, provider: str, org_letter: str = None) -> str:
    """
    Get final branch recommendation filename with organization prefix
    
    Args:
        branch_suffix: Branch suffix ('A', 'B', 'C')
        provider: Provider name ('openai', 'anthropic', 'gemini')
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Full filename (e.g., "A_recommendations_FINAL_branch_A_openai.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_recommendations_FINAL_branch_{branch_suffix}_{provider}.md"


def get_consensus_filename(org_letter: str = None) -> str:
    """
    Get consensus filename with organization prefix
    
    Args:
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Full filename (e.g., "A_recommendations_CONSENSUS_FINAL.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_recommendations_CONSENSUS_FINAL.md"


def get_consensus_summary_filename(org_letter: str = None) -> str:
    """
    Get consensus summary filename with organization prefix
    
    Args:
        org_letter: Organization letter (if None, auto-detect)
        
    Returns:
        str: Full filename (e.g., "A_consensus_summary.md")
    """
    if org_letter is None:
        org_letter = extract_organization_letter()
    
    return f"{org_letter}_consensus_summary.md"