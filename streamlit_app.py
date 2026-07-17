import os

import streamlit as st

from debate_coach import generate_debate_content, rate_opening_statement




def get_secret_api_key() -> str | None:
    try:
        if hasattr(st, "secrets"):
            value = st.secrets.get("OpenAI_Key")
            if value:
                return str(value)
    except Exception:
        pass

    value = os.getenv("OPENAI_KEY")
    return str(value) if value else None


st.set_page_config(page_title="AI Debate Coach", page_icon="🎤", layout="centered")
st.title("🎤 AI Debate Coach")
st.write("Prepare balanced debate arguments, key points, rebuttals, and a strong conclusion.")

with st.sidebar:
    st.header("Session setup")
    topic = st.text_input("Debate topic", "Should AI be regulated?")
    stance = st.radio("Your position", ["For", "Against"], horizontal=True)
    style = st.selectbox("Speaking style", ["Balanced", "Logical", "Aggressive"])
    api_key_input = st.text_input("OpenAI API key (optional)", type="password", help="Leave blank to use the stored secret if available.")
    secret_api_key = get_secret_api_key()
    if secret_api_key:
        st.caption("Using the stored OpenAI secret.")

mode = st.radio("Choose an action", ["Generate a draft", "Rate my own opening"], horizontal=True)
user_opening = ""
if mode == "Rate my own opening":
    user_opening = st.text_area(
        "Paste your opening statement",
        placeholder="Write your opening statement here...",
        height=180,
    )

col1, col2 = st.columns(2)
with col1:
    if st.button("Run", use_container_width=True):
        if mode == "Generate a draft":
            result = generate_debate_content(topic, stance, style, api_key=api_key_input or secret_api_key or None)
        else:
            result = rate_opening_statement(user_opening, topic, stance)
            result["opening_statement"] = user_opening or "No opening statement provided."
            result["key_points"] = [
                "State your claim more clearly.",
                "Add one supporting example.",
                "Make your closing line more memorable.",
            ]
            result["possible_rebuttals"] = [
                "Consider the strongest counterargument to your thesis.",
                "Prepare a response to objections about fairness or practicality.",
            ]
            result["concluding_statement"] = "Refine your conclusion so it reinforces your main claim."
            result["source"] = "user"
        st.session_state["coaching_result"] = result

with col2:
    if st.button("Clear results", use_container_width=True):
        st.session_state.pop("coaching_result", None)

if "coaching_result" in st.session_state:
    result = st.session_state["coaching_result"]
    st.success(f"Generated with: {result.get('source', 'fallback')}")

    st.subheader("Opening statement")
    st.write(result.get("opening_statement", "No opening statement available."))

    st.subheader("Key points")
    key_points = result.get("key_points") or result.get("rebuttal_points") or []
    for point in key_points:
        st.markdown(f"- {point}")

    st.subheader("Possible rebuttals")
    possible_rebuttals = result.get("possible_rebuttals") or result.get("rebuttal_points") or []
    for point in possible_rebuttals:
        st.markdown(f"- {point}")

    st.subheader("Concluding statement")
    st.write(result.get("concluding_statement", "No conclusion available."))

    st.subheader("Feedback")
    feedback = result.get("feedback", {})
    if isinstance(feedback, dict):
        feedback_payload = feedback
    else:
        feedback_payload = {
            "feedback": str(feedback or "No feedback available."),
            "score": result.get("score", 0),
            "word_count": 0,
        }

    score = result.get("score", feedback_payload.get("score", 0))
    st.metric("Score", f"{score}/100")
    st.write(feedback_payload.get("feedback", "No feedback available."))
    st.caption(f"Word count: {feedback_payload.get('word_count', 0)}")