import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import io

def run_sparring_room(topic: str, stance: str, api_key: str | None):
    st.title("🎙️ Live AI Sparring Ring")
    st.subheader(f"Topic: {topic} ({stance})")
    st.write("Practice speaking your arguments out loud against a tough AI opponent.")

    # Guard clause ensuring an API key is provided
    if not api_key:
        st.error("Please provide an OpenAI API key in the sidebar or store it as a secret to use the Live Sparring Ring.")
        return

    # Instantiate the client with the provided active key
    client = OpenAI(api_key=api_key)

    # 1. Initialize session states to hold conversation history
    if "sparring_chat" not in st.session_state:
        st.session_state.sparring_chat = [
            {"role": "assistant", "content": f"Hello! We are debating the topic: '{topic}', and you are taking the position: '{stance}'. Go ahead and speak your opening argument whenever you are ready."}
        ]

    # 2. Display the current chat background
    for msg in st.session_state.sparring_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.write("---")
    st.write("👉 **Tap the microphone icon below to speak your response.** Click it once to start recording, speak naturally, and click it again to finish.")

    # 3. Audio Recording Widget
    audio_bytes = audio_recorder(
        text="Click to record speech",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_size="2x"
    )

    # 4. Process the recorded speech
    if audio_bytes:
        with st.spinner("Processing your speech..."):
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "speech.wav"

            try:
                # Transcribe speech to text using OpenAI Whisper
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                user_speech_text = transcript_response.text
                
                # Append the transcribed user response directly to the chat
                st.session_state.sparring_chat.append({"role": "user", "content": user_speech_text})

            except Exception as e:
                st.error(f"Could not transcribe audio: {e}")
                return

        # 5. Generate the AI coach's counter-rebuttal
        with st.spinner("AI Coach is formulating a counterargument..."):
            try:
                # Invert stance so the opponent naturally argues the opposite perspective
                opponent_stance = "Against" if stance == "For" else "For"
                system_instruction = (
                    f"You are a highly competitive debate opponent. You are debating the topic: '{topic}'. "
                    f"The user is defending the '{stance}' stance, which means you must firmly defend the '{opponent_stance}' stance. "
                    "Analyze their latest spoken text and point out one logical fallacy, weak assumption, or counter-evidence. "
                    "Ask them a sharp, direct question to challenge their point. Keep your response under 120 words "
                    "so the verbal back-and-forth feels fast and fluid."
                )

                # Format payload with system context followed by session chat logs
                messages_payload = [{"role": "system", "content": system_instruction}]
                messages_payload.extend(st.session_state.sparring_chat)

                ai_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages_payload
                )
                
                coach_reply = ai_response.choices[0].message.content

                # Append assistant reply to the session history log
                st.session_state.sparring_chat.append({"role": "assistant", "content": coach_reply})
                
                # Instantly rerun to cleanly render updates to the discussion window
                st.rerun()

            except Exception as e:
                st.error(f"Error connecting to AI Coach: {e}")