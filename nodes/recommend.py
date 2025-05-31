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
            
            if "recommend" not in prompts_config:
                # Create default prompt if not in config
                recommendation_prompt = """
Jesteś ekspertem ds. transformacji cyfrowej i implementacji AI w organizacjach. 

Na podstawie analizy luk w obszarach OLIMP, przygotuj szczegółowy raport z rekomendacjami dla firmy, która chce płynnie przejść z obecnego stanu do poziomu E (maksymalnego) poprzez stany przejściowe.

Dane wejściowe to analiza luk w formacie JSON, która zawiera:
- Dla każdej sekcji (TECHNOLOGIA I INFRASTRUKTURA, LUDZIE I KOMPETENCJE, ORGANIZACJA I PROCESY)
- Dla każdego pytania: obecny poziom (present) i kroki do poziomu E (steps)
- Każdy poziom zawiera literę (A-E) i szczegółowy opis

STRUKTURA RAPORTU:
1. **Streszczenie wykonawcze**
   - Ogólna ocena obecnego stanu organizacji
   - Kluczowe obszary wymagające uwagi
   - Priorytety transformacji

2. **Analiza według obszarów**
   - Dla każdego obszaru (TECHNOLOGIA I INFRASTRUKTURA, LUDZIE I KOMPETENCJE, ORGANIZACJA I PROCESY):
     - Obecny stan i główne wyzwania
     - Rekomendowane ścieżki rozwoju
     - Konkretne działania do podjęcia

3. **Plan implementacji**
   - Faza 1 (0-6 miesięcy): Działania pilotażowe i podstawy
   - Faza 2 (6-18 miesięcy): Rozwój i skalowanie
   - Faza 3 (18-36 miesięcy): Optymalizacja i doskonałość

4. **Zasoby i budżet**
   - Szacowany budżet dla każdej fazy
   - Potrzebne zasoby ludzkie
   - Technologie i narzędzia do wdrożenia

5. **Wskaźniki sukcesu i monitoring**
   - KPI dla każdego obszaru
   - Sposoby mierzenia postępu
   - Punkty kontrolne

WYMAGANIA:
- Raport w języku polskim
- Konkretne, wykonalne rekomendacje
- Uwzględnienie specyfiki biznesowej
- Realistyczne timeline'y
- Fokus na płynne przejście między poziomami

Dane do analizy:
{gaps_data}

Przygotuj profesjonalny raport w formacie Markdown.
"""
            else:
                recommendation_prompt = prompts_config["recommend"]["recommendation_prompt"]
                
        except Exception as e:
            print(f"Error loading prompt config: {e}, using default prompt")
            # Use the default prompt from above
            recommendation_prompt = """
Jesteś ekspertem ds. transformacji cyfrowej i implementacji AI w organizacjach. 

Na podstawie analizy luk w obszarach OLIMP, przygotuj szczegółowy raport z rekomendacjami dla firmy, która chce płynnie przejść z obecnego stanu do poziomu E (maksymalnego) poprzez stany przejściowe.

Dane wejściowe to analiza luk w formacie JSON, która zawiera:
- Dla każdej sekcji (TECHNOLOGIA I INFRASTRUKTURA, LUDZIE I KOMPETENCJE, ORGANIZACJA I PROCESY)
- Dla każdego pytania: obecny poziom (present) i kroki do poziomu E (steps)
- Każdy poziom zawiera literę (A-E) i szczegółowy opis

STRUKTURA RAPORTU:
1. **Streszczenie wykonawcze**
   - Ogólna ocena obecnego stanu organizacji
   - Kluczowe obszary wymagające uwagi
   - Priorytety transformacji

2. **Analiza według obszarów**
   - Dla każdego obszaru (TECHNOLOGIA I INFRASTRUKTURA, LUDZIE I KOMPETENCJE, ORGANIZACJA I PROCESY):
     - Obecny stan i główne wyzwania
     - Rekomendowane ścieżki rozwoju
     - Konkretne działania do podjęcia

3. **Plan implementacji**
   - Faza 1 (0-6 miesięcy): Działania pilotażowe i podstawy
   - Faza 2 (6-18 miesięcy): Rozwój i skalowanie
   - Faza 3 (18-36 miesięcy): Optymalizacja i doskonałość

4. **Zasoby i budżet**
   - Szacowany budżet dla każdej fazy
   - Potrzebne zasoby ludzkie
   - Technologie i narzędzia do wdrożenia

5. **Wskaźniki sukcesu i monitoring**
   - KPI dla każdego obszaru
   - Sposoby mierzenia postępu
   - Punkty kontrolne

WYMAGANIA:
- Raport w języku polskim
- Konkretne, wykonalne rekomendacje
- Uwzględnienie specyfiki biznesowej
- Realistyczne timeline'y
- Fokus na płynne przejście między poziomami

Dane do analizy:
{gaps_data}

Przygotuj profesjonalny raport w formacie Markdown.
"""
        
        # Format gaps data as JSON string for the prompt
        gaps_json = json.dumps(state["gaps"], ensure_ascii=False, indent=2)
        formatted_prompt = recommendation_prompt.format(gaps_data=gaps_json)
        
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