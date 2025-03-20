import sys
import os
import time
import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect

# Text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Voice recognition
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio)
            print(f"User said: {query}")
            speak(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Speech service is down.")
            return ""

# GUI Class
class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS AI Assistant")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")
        self.label = QLabel("J.A.R.V.I.S", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 50, 800, 100)
        self.label.setFont(QFont("Orbitron", 40, QFont.Weight.Bold))
        self.label.setStyleSheet("color: cyan;")

        self.status_label = QLabel("Status: Listening...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setGeometry(0, 500, 800, 50)
        self.status_label.setFont(QFont("Orbitron", 14))
        self.status_label.setStyleSheet("color: white;")

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        # Play startup sound
        self.beep = QSoundEffect()
        self.beep.setSource(QUrl.fromLocalFile(os.path.abspath("beep.wav")))
        self.beep.setVolume(0.25)
        self.beep.play()

        # Start listening in background
        QTimer.singleShot(3000, self.process_voice_command)

    def paintEvent(self, event):
        painter = QPainter(self)
        center_x = self.width() / 2
        center_y = self.height() / 2
        pen = QPen(QColor("cyan"))
        pen.setWidth(2)
        painter.setPen(pen)

        # Outer Rings
        painter.drawEllipse(int(center_x - 200), int(center_y - 200), 400, 400)
        painter.drawEllipse(int(center_x - 150), int(center_y - 150), 300, 300)
        painter.drawEllipse(int(center_x - 100), int(center_y - 100), 200, 200)

        # Inner glow
        painter.setBrush(QColor(0, 255, 255, 50))
        painter.drawEllipse(int(center_x - 10), int(center_y - 10), 20, 20)

    def process_voice_command(self):
        while True:
            query = take_command()

            if "open youtube" in query:
                self.status_label.setText("Status: Opening YouTube")
                speak("Opening YouTube")
                webbrowser.open("https://www.youtube.com")
            elif "open gmail" in query:
                self.status_label.setText("Status: Opening Gmail")
                speak("Opening Gmail")
                webbrowser.open("https://mail.google.com")
            elif "send message to" in query:
                name = query.split("send message to")[-1].strip()
                speak(f"Preparing WhatsApp for {name}. What should I say?")
                message = take_command()
                # Make sure you have saved contact names in WhatsApp
                pywhatkit.sendwhatmsg_instantly(f"{name}", message)
                self.status_label.setText(f"Status: Sent message to {name}")
                speak(f"Message sent to {name}")
            elif "exit" in query or "shutdown" in query:
                self.status_label.setText("Status: Shutting Down")
                speak("Shutting down, goodbye")
                sys.exit()
            else:
                self.status_label.setText("Status: Listening...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    speak("Initializing JARVIS cinematic interface.")
    sys.exit(app.exec())
