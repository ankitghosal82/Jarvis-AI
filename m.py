# Advanced JARVIS with Memory, PDF Reader, Voice Confirmations, Notes, Language Detection

import cohere
import datetime
import random
import wikipedia
import webbrowser
import pyttsx3
import speech_recognition as sr
import pywhatkit
import fitz  # PyMuPDF for PDF reading
import langdetect
import os

# === Setup ===
co = cohere.Client("H2TbCV7bv8o19YZnaZT1BbUD3vXgxobdr9VkV2jg")

engine = pyttsx3.init()
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

memory_log = []
notes_file = "jarvis_notes.txt"

# === Functions ===
def speak(text):
    print("🤖 JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

def confirm(text):
    speak(f"✔️ {text}")

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="en-in")
            print(f"🧠 You said: {command}")
            return command
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech recognition error."

def get_time():
    return datetime.datetime.now().strftime("%H:%M")

def get_date():
    return datetime.datetime.now().strftime("%A, %d %B %Y")

def tell_joke():
    jokes = [
        "Why did the developer go broke? Because he used up all his cache.",
        "Debugging: Being the detective in a crime movie where you're also the murderer.",
        "Why don’t programmers like nature? Too many bugs.",
    ]
    return random.choice(jokes)

def ask_cohere(prompt):
    try:
        response = co.chat(
            model='command-r',
            message=prompt,
            temperature=0.7,
        )
        return response.text.strip()
    except Exception as e:
        return f"Error with Cohere: {e}"

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
        return text[:1000]  # Summarize first 1000 chars
    except Exception as e:
        return f"Error reading PDF: {e}"

def save_note(note):
    with open(notes_file, "a") as f:
        f.write(f"{datetime.datetime.now()}: {note}\n")
    return "Note saved."

def open_local_file(app_name):
    try:
        os.system(app_name)
        return f"Opening {app_name}..."
    except:
        return f"Couldn't open {app_name}."

def handle_command(command):
    command = command.lower()
    memory_log.append(command)

    if "time" in command:
        return f"The time is {get_time()}"
    elif "date" in command:
        return f"Today's date is {get_date()}"
    elif "joke" in command:
        return tell_joke()
    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            return f"According to Wikipedia: {summary}"
        except Exception as e:
            return f"Couldn't fetch Wikipedia: {str(e)}"
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube..."
    elif "open google" in command:
        webbrowser.open("https://google.com")
        return "Opening Google..."
    elif "play music" in command:
        speak("Which song should I play?")
        song = listen()
        if song:
            pywhatkit.playonyt(song)
            return f"Playing {song}"
        return "Song not understood."
    elif "read pdf" in command:
        speak("Provide PDF path:")
        pdf_path = input("Enter PDF file path: ")
        return read_pdf(pdf_path)
    elif "note" in command or "reminder" in command:
        speak("What should I remember?")
        note = listen()
        return save_note(note)
    elif "language" in command:
        speak("Say something to detect the language:")
        lang_input = listen()
        return detect_language(lang_input)
    elif "open notepad" in command:
        return open_local_file("notepad")
    elif "open code" in command:
        return open_local_file("code")
    elif "show memory" in command:
        return "\n".join(memory_log[-10:]) or "Nothing remembered yet."
    else:
        return ask_cohere(command)

# === Main ===
if __name__ == "__main__":
    speak("Hello, I am JARVIS! How can i help you?")
    while True:
        mode = input("\nType 'v' for voice or type your command: ").strip().lower()
        if mode == "v":
            user_input = listen()
        else:
            user_input = mode

        if user_input.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye, Ankit!")
            break

        reply = handle_command(user_input)
        confirm(reply)