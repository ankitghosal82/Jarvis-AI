import streamlit as st
import datetime
import random
import wikipedia
import webbrowser
import pyttsx3
import speech_recognition as sr
import pywhatkit
import fitz
import langdetect
import os
import cohere

# === Page config ===
st.set_page_config(page_title="JARVIS AI", layout="wide", initial_sidebar_state="collapsed")

# === ChatGPT-style CSS ===
st.markdown("""
    <style>
    .jarvis-response {
        font-size: 22px;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 500;
        background-color: #1e1e2f;
        color: #f0f0f0;
        padding: 20px;
        border-radius: 14px;
        margin-top: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    }
    .memory-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #2b2b35;
        color: #eeeeee;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 2px 14px rgba(0,0,0,0.3);
        z-index: 999;
    }
    input[type="text"] {
        font-size: 20px !important;
        padding: 16px !important;
    }
    .stTextInput>div>div>input {
        height: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# === API key ===
co = cohere.Client("")  # Replace with your Cohere API key

# === TTS Setup ===
engine = pyttsx3.init()
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# === Memory ===
memory_log = []

# === Functions ===
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_time():
    return datetime.datetime.now().strftime("%H:%M")

def get_date():
    return datetime.datetime.now().strftime("%A, %d %B %Y")

def tell_joke():
    return random.choice([
        "Why did the developer go broke? Because he used up all his cache.",
        "Debugging: Being the detective in a crime movie where you're also the murderer.",
        "Why don’t programmers like nature? Too many bugs.",
    ])

def ask_cohere(prompt):
    try:
        response = co.chat(model='command-r', message=prompt, temperature=0.7)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def detect_language(text):
    try:
        lang = langdetect.detect(text)
        return f"Language detected: {lang}"
    except:
        return "Couldn't detect language."

def read_pdf(path):
    try:
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text[:1000] or "PDF is empty."
    except Exception as e:
        return f"Error reading PDF: {e}"

def open_local_file(app_name):
    try:
        os.system(app_name)
        return f"Opening {app_name}..."
    except:
        return f"Couldn't open {app_name}."

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="en-in")
            st.success(f"🧠 You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech recognition error."

# === UI ===
st.title("🤖 JARVIS - AI Voice Assistant")
st.markdown("Welcome, Ankit! Your JARVIS assistant is ready to help.")

col1, _ = st.columns([2, 0.1])

with col1:
    st.header("🎙️ Talk to JARVIS")
    if st.button("🎤 Speak Now"):
        query = listen()
        st.session_state["query"] = query

    query_text = st.text_input("Type your command:", value=st.session_state.get("query", ""), key="textinput")

    if st.button("🚀 Run"):
        command = query_text.lower()
        memory_log.append(command)

        if "time" in command:
            response = f"The time is {get_time()}"
        elif "date" in command:
            response = f"Today's date is {get_date()}"
        elif "joke" in command:
            response = tell_joke()
        elif "wikipedia" in command:
            topic = command.replace("wikipedia", "").strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                response = f"According to Wikipedia: {summary}"
            except Exception as e:
                response = f"Couldn't fetch Wikipedia: {str(e)}"
        elif "youtube" in command:
            webbrowser.open("https://youtube.com")
            response = "Opening YouTube..."
        elif "google" in command:
            webbrowser.open("https://google.com")
            response = "Opening Google..."
        elif "play music" in command:
            song = st.text_input("Enter song name:")
            if song:
                pywhatkit.playonyt(song)
                response = f"Playing {song}"
            else:
                response = "Song not specified."
        elif "read pdf" in command:
            pdf_file = st.file_uploader("Upload a PDF", type="pdf")
            if pdf_file is not None:
                with open("temp.pdf", "wb") as f:
                    f.write(pdf_file.read())
                response = read_pdf("temp.pdf")
            else:
                response = "No file uploaded."
        elif "language" in command:
            lang_text = st.text_input("Enter text to detect language:")
            if lang_text:
                response = detect_language(lang_text)
            else:
                response = "No text provided."
        elif "open notepad" in command:
            response = open_local_file("notepad")
        elif "open code" in command:
            response = open_local_file("code")
        elif "show memory" in command:
            response = memory_log[-1] if memory_log else "Nothing remembered yet."
        else:
            response = ask_cohere(command)

        st.markdown(f'<div class="jarvis-response">🤖 <b>JARVIS:</b> {response}</div>', unsafe_allow_html=True)
        speak(response)

# === Floating Last Command ===
if memory_log:
    st.markdown(f'<div class="memory-box">🧠 Last command: {memory_log[-1]}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Built by Ankit💡.")


