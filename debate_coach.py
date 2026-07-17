from __future__ import annotations

from typing import Any, Dict


def _normalize_feedback(feedback: Any, score: int, word_count: int) -> Dict[str, Any]:
    if isinstance(feedback, dict):
        return {
            "score": int(feedback.get("score", score)),
            "feedback": feedback.get("feedback", "No feedback available."),
            "word_count": int(feedback.get("word_count", word_count)),
        }

    return {
        "score": int(score),
        "feedback": str(feedback or "No feedback available."),
        "word_count": int(word_count),
    }


def rate_opening_statement(statement: str, topic: str, stance: str) -> Dict[str, object]:
    clean_statement = (statement or "").strip()
    topic_text = (topic or "this issue").strip() or "this issue"
    stance_text = (stance or "For").strip().lower()

    words = len(clean_statement.split()) if clean_statement else 0
    score = min(100, 40 + min(40, words // 4))

    if stance_text in {"for", "against"}:
        score += 10

    if clean_statement and topic_text.lower() in clean_statement.lower():
        score = min(100, score + 5)

    if words < 20:
        feedback_text = "Expand the opening with a clearer claim and more supporting detail."
    elif words < 40:
        feedback_text = "Your opening is serviceable, but it would be stronger with a concrete example and sharper structure."
    else:
        feedback_text = "Your opening is strong and well developed. Keep your position explicit and add one memorable example."

    feedback = _normalize_feedback(feedback_text, score, words)

    return {
        "score": feedback["score"],
        "feedback": feedback,
        "word_count": feedback["word_count"],
        "source": "user",
    }


def generate_debate_content(topic: str, stance: str, style: str, api_key: str | None = None) -> Dict[str, object]:
    topic_text = (topic or "this issue").strip() or "this issue"
    stance_text = (stance or "For").strip().lower()
    style_text = (style or "Balanced").strip().lower()

    if stance_text == "against":
        support_statement = f"I oppose {topic_text}."
        rebuttal_focus = "Highlight why the proposal may create unintended harms or inefficiencies."
        conclusion = f"In conclusion, {topic_text} should be rejected because it creates more risk than benefit."
        side_name = "Opposing side"
    else:
        support_statement = f"I support {topic_text}."
        rebuttal_focus = "Highlight why the proposal is practical and beneficial."
        conclusion = f"In conclusion, {topic_text} should be adopted because it offers the strongest practical path forward."
        side_name = "Supporting side"

    if style_text == "aggressive":
        tone = "forceful and confrontational"
    elif style_text == "logical":
        tone = "clear and analytical"
    else:
        tone = "balanced and persuasive"

    opening_statement = (
        f"{support_statement}\n"
        f"My position is {tone}, and I will show why this approach is the strongest choice."
    )

    key_points = [
        f"Define the core issue behind {topic_text}.",
        "Explain the main values or outcomes at stake.",
        "Present the strongest evidence or example that supports your side.",
    ]

    possible_rebuttals = [
        f"Prepare an answer to the claim that {topic_text} is impractical.",
        "Prepare a response to the strongest argument from the opposing side.",
        rebuttal_focus,
        "Show how your side handles trade-offs and unintended consequences.",
    ]

    concluding_statement = conclusion

    feedback = {
        "score": 88,
        "feedback": "Your structure is strong. Add at least one concrete example to make the case even more persuasive.",
        "word_count": len(opening_statement.split()),
    }

    source = "fallback"
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            prompt = (
                f"Create a concise debate prep brief for the topic '{topic_text}'. "
                f"The user is on the {side_name.lower()} and wants a {style_text} tone. "
                "Include an opening statement, three key points, two rebuttals, and a conclusion."
            )
            response = client.responses.create(model="gpt-4.1-mini", input=prompt)
            if getattr(response, "output_text", None):
                opening_statement = response.output_text.strip()
                source = "ai"
        except Exception:
            source = "fallback"

    return {
        "opening_statement": opening_statement,
        "key_points": key_points,
        "possible_rebuttals": possible_rebuttals,
        "concluding_statement": concluding_statement,
        "feedback": feedback,
        "source": source,
        "score": feedback["score"],
    }
