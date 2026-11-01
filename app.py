import os
import streamlit as st
from sarvamai import SarvamAI

st.set_page_config(page_title='Samjho AI', page_icon='🧠', layout='centered')
st.title('🧠 Samjho AI')
st.caption('Your thinking matters more than your answer. • Powered by Sarvam AI')

key = os.getenv('SARVAM_API_KEY')
if not key:
    key = st.text_input('Sarvam API key (not saved)', type='password')

language = st.selectbox('Explain back to me in', ['Hinglish', 'English', 'Hindi', 'Marathi', 'Gujarati'])
subject = st.selectbox('Subject', ['Physics', 'Mathematics', 'Chemistry', 'Biology', 'General knowledge'])
mode = st.radio('How will you explain your thinking?', ['Type', 'Record voice'], horizontal=True)

if 'student_text' not in st.session_state:
    st.session_state.student_text = ''

if mode == 'Record voice':
    audio = st.audio_input('Explain your reasoning (up to 30 seconds)')
    if audio and st.button('🎙️ Transcribe my explanation'):
        if not key:
            st.error('Please enter your API key first.')
        else:
            try:
                client = SarvamAI(api_subscription_key=key)
                with st.spinner('Listening with Saaras...'):
                    result = client.speech_to_text.transcribe(file=('recording.wav', audio.getvalue(), 'audio/wav'), model='saaras:v4', mode='transcribe')
                st.session_state.student_text = result.transcript
                st.success('Transcribed! Review the text below.')
            except Exception as e:
                st.error(f'Transcription failed: {e}. You can type your explanation instead.')

student_text = st.text_area('What do you think? Explain your reasoning.', value=st.session_state.student_text, height=125, placeholder='Example: Heavy objects fall faster because gravity pulls them more...')

if st.button('🔍 Find my misconception', type='primary', use_container_width=True):
    if not key:
        st.error('Please enter your Sarvam API key.')
    elif not student_text.strip():
        st.warning('Please type or record your explanation.')
    else:
        try:
            client = SarvamAI(api_subscription_key=key)
            prompt = f'''You are Samjho AI, an encouraging and scientifically accurate tutor.
Subject: {subject}. Respond in {language}.
Student reasoning: {student_text}
Identify whether there is a genuine conceptual misconception. Do NOT invent one if reasoning is correct.
Use exactly these headings, concise and clear:
### 🧠 What I understood
Summarize their reasoning in one sentence.
### 🔎 Misconception check
State the precise error, or say the reasoning is correct. Distinguish uncertainty from error.
### 💡 Aha! Moment
Give a correct, simple explanation with a relatable Indian everyday-life analogy. Avoid misleading analogies.
### 🎯 Your challenge
Ask ONE short conceptual follow-up question without giving its answer.
Be friendly, precise and keep the whole answer under 220 words.'''
            with st.spinner('Samjho AI is analyzing your thinking...'):
                response = client.chat.completions(
    model="sarvam-105b",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=1500,
    reasoning_effort=None
)
            print("SARVAM RESPONSE:", response)
            st.markdown(response.choices[0].message.content or 'No answer returned. Please try again.')
        except Exception as e:
            st.error(f'API request failed: {e}')

st.divider()
st.caption('Prototype for learning support. AI explanations may be imperfect; verify important facts.')
