# src/utils/evaluation.py
"""
A small placeholder evaluation (LangSmith-like).
In production you would call LangSmith SDK to log/examine predictions.
"""

def evaluate_response(question: str, answer: str, sources: list) -> dict:
    """
    Very basic evaluation:
      - checks if answer non-empty
      - counts sentences
      - returns a small score
    """
    score = 0.0
    if answer and len(answer.strip()) > 10:
        score += 0.6
    # higher score if sources present
    if sources and len(sources) > 0:
        score += 0.4
    metadata = {"question_len": len(question), "answer_len": len(answer)}
    return {"score": round(score, 2), "meta": metadata}
