import sys
import json
import os
import webbrowser
import pyttsx3
import pyautogui
import pywhatkit
import psutil
import speech_recognition as sr
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QMessageBox

# Initialize TTS engine
engine = pyttsx3.init()

# Load contacts
CONTACTS_FILE = "contacts.json"
if not os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump({"John": "+911234567890", "Alice": "+919876543210"}, f)

with open(CONTACTS_FILE, 'r') as f:
    contacts = json.load(f)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        speak(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""

def execute_command(command):
    if 'open gmail' in command:
        speak("Opening Gmail.")
        webbrowser.open("https://mail.google.com")
    
    elif 'open youtube' in command:
        speak("Opening YouTube.")
        webbrowser.open("https://youtube.com")
    
    elif 'shutdown' in command:
        speak("Shutting down system.")
        os.system("shutdown /s /t 1")
    
    elif 'battery' in command:
        battery = psutil.sensors_battery()
        speak(f"Battery is at {battery.percent} percent")
    
    elif 'send whatsapp message' in command:
        try:
            contact_name = command.split("to ")[-1]
            if contact_name in contacts:
                speak(f"What message should I send to {contact_name}?")
                msg = listen_command()
                pywhatkit.sendwhatmsg_instantly(contacts[contact_name], msg)
                speak("Message sent successfully.")
            else:
                speak("Contact not found.")
        except Exception as e:
            speak("There was an error sending the message.")
    else:
        speak("I don't understand that command.")

# GUI
class JarvisGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI - Voice Assistant")
        self.setGeometry(300, 300, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Jarvis is Ready")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        btn_listen = QPushButton("🎙️ Give Command")
        btn_contacts = QPushButton("📋 View Contacts")

        btn_listen.clicked.connect(self.handle_command)
        btn_contacts.clicked.connect(self.show_contacts)

        layout.addWidget(self.label)
        layout.addWidget(self.output)
        layout.addWidget(btn_listen)
        layout.addWidget(btn_contacts)

        self.setLayout(layout)

    def handle_command(self):
        command = listen_command()
        if command:
            self.output.append(f"👤 User: {command}")
            execute_command(command)

    def show_contacts(self):
        contact_list = "\n".join([f"{name}: {number}" for name, number in contacts.items()])
        QMessageBox.information(self, "Saved Contacts", contact_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = JarvisGUI()
    gui.show()
    speak("Jarvis AI Activated!")
    sys.exit(app.exec())
