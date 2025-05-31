from state import ExamState
from logger import get_logger

# Get logger instance
logger = get_logger()

def generate_report(state: ExamState) -> ExamState:
    """
    Node to generate a report based on evaluation results
    
    Args:
        state: The current state with evaluation results
        
    Returns:
        Updated state with generated report
    """
    logger.info("Starting report generation...")
    
    exam_content = state.get("exam_content", {})
    evaluation = state.get("evaluation", {})
    evaluation_essay = state.get("evaluation_essay", {})
    
    # Debug output
    print(f"evaluation_essay: {evaluation_essay}")
    print(f"evaluation_essay keys: {evaluation_essay.keys() if evaluation_essay else 'None'}")
    if evaluation_essay and "Zadanie 19" in evaluation_essay:
        print(f"Zadanie 19 keys: {evaluation_essay['Zadanie 19'].keys()}")
    else:
        # If evaluation_essay is empty, try to find Zadanie 19 in exam_content and evaluate it directly
        if "Zadanie 19" in exam_content:
            print("Zadanie 19 found in exam_content, creating evaluation_essay data")
            from nodes.evaluate_3 import ask_llm_for_evaluation
            from langchain_openai import ChatOpenAI
            import os
            
            # Initialize the LLM
            model = "gpt-4.1"
            api_key = os.getenv("OPENAI_API_KEY")
            try:
                llm = ChatOpenAI(model=model, temperature=0, openai_api_key=api_key)
                
                # Get the student answer and topic number
                student_answer = exam_content["Zadanie 19"].get("Odpowiedź", "")
                topic_number = exam_content["Zadanie 19"].get("Temat", "1")
                
                # Create a simple criteria data
                criteria_data = {
                    "tytul": "Czy podróż może zmienić człowieka?" if topic_number == "1" else "Młodość – czas beztroski czy trudnych wyborów?",
                    "Rozumienie Pojeć": "See full criteria in the original YAML file"
                }
                
                # Get LLM evaluation
                llm_evaluation = ask_llm_for_evaluation(student_answer, criteria_data, llm)
                
                # Create evaluation_essay data
                evaluation_essay = {
                    "Zadanie 19": {
                        "question_id": "Zadanie 19",
                        "student_answer": student_answer,
                        "topic_number": topic_number,
                        "total_score": llm_evaluation["total_score"],
                        "sfwp_score": llm_evaluation["sfwp_score"],
                        "klik_score": llm_evaluation["klik_score"],
                        "kw_score": llm_evaluation["kw_score"],
                        "jw_score": llm_evaluation["jw_score"],
                        "llm_reasoning": llm_evaluation["reasoning"],
                        "llm_full_response": llm_evaluation["full_response"]
                    }
                }
                print(f"Created evaluation_essay: {evaluation_essay}")
            except Exception as e:
                print(f"Error creating evaluation_essay: {e}")
    
    # Calculate overall statistics
    total_questions = len(evaluation)
    
    # Human evaluation statistics
    correct_answers_human = sum(1 for q_data in evaluation.values() if q_data.get("is_correct", False))
    total_points_human = sum(int(q_data.get("student_score", 0)) for q_data in evaluation.values() if q_data.get("student_score", "").isdigit())
    
    # Calculate sum of Punktacja for questions 1-18 (excluding essay)
    punktacja_sum = sum(int(q_data.get("max_score", 0)) for q_data in evaluation.values() if q_data.get("max_score", "").isdigit())
    
    # AI evaluation statistics
    llm_correct_answers = sum(1 for q_data in evaluation.values() if q_data.get("llm_score", "").isdigit() and q_data.get("max_score", "").isdigit() and int(q_data.get("llm_score", 0)) == int(q_data.get("max_score", 0)))
    llm_total_points = sum(int(q_data.get("llm_score", 0)) for q_data in evaluation.values() if q_data.get("llm_score", "").isdigit())
    
    # Calculate total questions and points including essay
    total_questions_with_essay = total_questions + 1  # +1 for Zadanie 19 (essay)
    max_points_essay = 35  # Maximum points for essay (Zadanie 19)
    total_max_points = punktacja_sum + max_points_essay
    
    # Generate report
    report = f"""
RAPORT OCENY EGZAMINU
=====================

Podsumowanie
===========
Liczba wszystkich zadań: {total_questions_with_essay}
Maksymalna liczba punktów: {total_max_points}

Ocena człowieka:
- Liczba poprawnych odpowiedzi: {correct_answers_human}
- Suma punktów: {total_points_human}
- Procent maksymalnej liczby punktów: {(total_points_human / punktacja_sum * 100) if punktacja_sum > 0 else 0:.2f}%

Ocena AI:
- Liczba poprawnych odpowiedzi: {llm_correct_answers}
- Suma punktów: {llm_total_points}
- Procent maksymalnej liczby punktów: {(llm_total_points / punktacja_sum * 100) if punktacja_sum > 0 else 0:.2f}%

Części 1 i 2: Pytania
=====================
Liczba pytań: {total_questions}
Maksymalna liczba punktów: {punktacja_sum}

Ocena człowieka:
- Liczba poprawnych odpowiedzi: {correct_answers_human}
- Suma punktów: {total_points_human}
- Procent maksymalnej liczby punktów: {(total_points_human / punktacja_sum * 100) if punktacja_sum > 0 else 0:.2f}%

Ocena AI:
- Liczba poprawnych odpowiedzi: {llm_correct_answers}
- Suma punktów: {llm_total_points}
- Procent maksymalnej liczby punktów: {(llm_total_points / punktacja_sum * 100) if punktacja_sum > 0 else 0:.2f}%

Szczegółowa ocena odpowiedzi:
---------------------------
"""
    
    # Add details for each question
    for question_id, eval_data in evaluation.items():
        student_score = eval_data.get("student_score", "0")
        llm_score = eval_data.get("llm_score", "0")
        max_score = eval_data.get("max_score", "1")
        
        report += f"""
Pytanie {question_id}:
Punkty (Ocena człowieka): {student_score}/{max_score}
Punkty (Ocena AI): {llm_score}/{max_score}
Odpowiedź ucznia: {eval_data.get("student_answer", "Brak odpowiedzi")}
"""
        
        # Add LLM reasoning
        report += f"""
Uzasadnienie AI: {eval_data.get("llm_reasoning", "Brak uzasadnienia")}
"""
        
        if not eval_data.get("is_correct", False):
            report += f"""
Poprawna odpowiedź: {eval_data.get("correct_answer", "Nie podano")}
Przykładowa odpowiedź: {eval_data.get("example_answer", "Nie podano")}
"""
    
    # Add essay evaluation from evaluation_essay data
    if evaluation_essay and "Zadanie 19" in evaluation_essay:
        essay_data = evaluation_essay["Zadanie 19"]
        
        # Extract scores from the evaluation data - using the field names from evaluate_3.py
        total_score = essay_data.get("total_score", "0")
        sfwp_score = essay_data.get("sfwp_score", "0")
        klik_score = essay_data.get("klik_score", "0")
        
        # If not found, try alternative field name
        if klik_score == "0":
            klik_score = essay_data.get("klik_score", "0")
            
        kw_score = essay_data.get("kw_score", "0")
        jw_score = essay_data.get("jw_score", "0")
        
        # If we still don't have scores, try to extract from the full_response
        if total_score == "0" and "llm_full_response" in essay_data:
            full_response = essay_data.get("llm_full_response", "")
            
            # Try to extract scores from the full response
            if "Score:" in full_response:
                score_line = [line for line in full_response.split('\n') if line.startswith("Score:")][0]
                total_score = score_line.replace("Score:", "").strip().split('/')[0].strip()
                
            if "SFWP:" in full_response:
                sfwp_line = [line for line in full_response.split('\n') if line.startswith("SFWP:")][0]
                sfwp_score = sfwp_line.replace("SFWP:", "").strip().split('/')[0].strip()
                
            if "KLiK:" in full_response:
                klik_line = [line for line in full_response.split('\n') if line.startswith("KLiK:")][0]
                klik_score = klik_line.replace("KLiK:", "").strip().split('/')[0].strip()
                
            if "KW:" in full_response:
                kw_line = [line for line in full_response.split('\n') if line.startswith("KW:")][0]
                kw_score = kw_line.replace("KW:", "").strip().split('/')[0].strip()
                
            if "JW:" in full_response:
                jw_line = [line for line in full_response.split('\n') if line.startswith("JW:")][0]
                jw_score = jw_line.replace("JW:", "").strip().split('/')[0].strip()
        
        # Get the student's answer and topic number
        student_answer = essay_data.get("student_answer", "Brak odpowiedzi")
        topic_number = essay_data.get("topic_number", "1")
        
        # Get the reasoning from LLM
        llm_reasoning = essay_data.get("llm_reasoning", "Brak uzasadnienia")
        
        report += f"""

Część 3: Ocena wypracowania (Zadanie 19)
=======================================
Wynik całkowity: {total_score}/35
Ocena SFWP: {sfwp_score}/1
Ocena KLiK: {klik_score}/16
Ocena KW: {kw_score}/7
Ocena JW: {jw_score}/11

Odpowiedź ucznia:
{student_answer}

Uzasadnienie oceny:
{llm_reasoning}
"""
    else:
        # Fallback if no essay evaluation data is available
        report += f"""

Część 3: Ocena wypracowania (Zadanie 19)
=======================================
Brak danych do oceny wypracowania.
"""
    
    logger.info("Report generation completed successfully")
    
    # Update state with generated report
    return {
        **state,
        "report": report
    }
