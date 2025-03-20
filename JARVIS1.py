import sys
import os
import time
import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QRectF, QPointF, QThread, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
import random
import math

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
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        try:
            query = r.recognize_google(audio)
            print(f"User said: {query}")
            speak(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
            speak("Speech service is down.")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

# Voice Worker Thread
class VoiceWorker(QThread):
    status_update = pyqtSignal(str)
    command_detected = pyqtSignal(str)

    def run(self):
        while True:
            self.status_update.emit("SYSTEM ONLINE")
            query = take_command()
            if query:
                self.command_detected.emit(query)
            time.sleep(1)

# Holographic Panel
class HoloPanel(QWidget):
    def __init__(self, parent, text, x, y):
        super().__init__(parent)
        self.setGeometry(x, y, 250, 150)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.text = text
        self.setStyleSheet("background-color: rgba(0, 100, 255, 30); border: 1px solid rgba(0, 255, 255, 100);")
        self.label = QLabel(text, self)
        self.label.setFont(QFont("Orbitron", 14, QFont.Weight.Bold))
        self.label.setStyleSheet("color: cyan; background: none;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 50, 250, 50)

        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(2000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.finished.connect(self.fade_out)
        self.anim.start()

    def fade_out(self):
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.start()
        QTimer.singleShot(2000, self.close)

# GUI Class
class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS AI Assistant")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #0A0A0A;")
        
        # Title Label
        self.title = QLabel("J.A.R.V.I.S", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 20, 1000, 80)
        self.title.setFont(QFont("Orbitron", 36, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #00FFFF; background: none;")

        # Status Label
        self.status_label = QLabel("SYSTEM ONLINE", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setGeometry(0, 620, 1000, 40)
        self.status_label.setFont(QFont("Orbitron", 12))
        self.status_label.setStyleSheet("color: #00CED1;")

        # System Status Widget
        self.status_widget = QWidget(self)
        self.status_widget.setGeometry(50, 150, 200, 100)
        self.status_widget.setStyleSheet("background-color: rgba(0, 100, 255, 20); border: 1px solid cyan;")
        self.status_text = QLabel("POWER: 100%", self.status_widget)
        self.status_text.setFont(QFont("Orbitron", 10))
        self.status_text.setStyleSheet("color: cyan; background: none;")
        self.status_text.setGeometry(10, 40, 180, 20)

        # Animation variables
        self.rotation_angle = 0
        self.pulse_factor = 0
        self.listening = False
        self.waveform_points = [0] * 30
        self.scan_line_y = 0
        self.particles = [{'x': 0, 'y': 0, 'angle': random.uniform(0, 360), 'speed': random.uniform(1, 3)} for _ in range(20)]
        self.ripple_size = 0
        self.color_phase = 0

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        # Startup sound
        self.beep = QSoundEffect()
        self.beep.setSource(QUrl.fromLocalFile(os.path.abspath("beep.wav")))
        self.beep.setVolume(0.5)
        self.beep.play()

        # Voice worker
        self.voice_worker = VoiceWorker()
        self.voice_worker.status_update.connect(self.update_status)
        self.voice_worker.command_detected.connect(self.handle_command)
        self.voice_worker.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y = self.width() / 2, self.height() / 2

        # Background Holographic Noise
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(50):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            painter.setBrush(QColor(0, 255, 255, random.randint(5, 20)))
            painter.drawEllipse(x, y, 2, 2)

        # Arc Reactor Core
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)
        for i in range(3):
            radius = 150 - i * 40
            pen = QPen(QColor(0, 255, 255, 100 - i * 20), 2 + i)
            painter.setPen(pen)
            painter.setBrush(QColor(0, 255, 255, 20))
            painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.restore()

        # Particle Effects
        painter.setPen(Qt.PenStyle.NoPen)
        for particle in self.particles:
            particle['angle'] += particle['speed']
            x = center_x + math.cos(math.radians(particle['angle'])) * 150
            y = center_y + math.sin(math.radians(particle['angle'])) * 150
            painter.setBrush(QColor(0, 255, 255, 100))
            painter.drawEllipse(int(x), int(y), 5, 5)
            particle['x'], particle['y'] = x, y

        # Core Pulse
        glow_size = 50 + math.sin(self.pulse_factor * math.pi) * 20
        gradient = QLinearGradient(center_x, center_y - glow_size, center_x, center_y + glow_size)
        gradient.setColorAt(0, QColor(0, 255, 255, 150))
        gradient.setColorAt(1, QColor(0, 255, 255, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - glow_size / 2), int(center_y - glow_size / 2), int(glow_size), int(glow_size))

        # HUD Grid
        painter.setPen(QPen(QColor(0, 191, 255, 50), 1, Qt.PenStyle.DotLine))
        for x in range(0, self.width(), 50):
            painter.drawLine(x, 100, x, self.height() - 100)
        for y in range(100, self.height() - 100, 50):
            painter.drawLine(0, y, self.width(), y)

        # Scan Line
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 255, 255, 30))
        painter.drawRect(0, self.scan_line_y, self.width(), 5)

        # Waveform with Ripple Effect
        if self.listening:
            painter.setPen(QPen(QColor(0, 255, 255, 150), 2))
            path = QPainterPath()
            path.moveTo(350, 600)
            for i, height in enumerate(self.waveform_points):
                x = 350 + i * 20
                y = 600 - height
                path.lineTo(x, y)
            painter.drawPath(path)
            if self.ripple_size > 0:
                painter.setPen(QPen(QColor(0, 255, 255, 100 - int(self.ripple_size * 2)), 2))
                painter.drawEllipse(500, 550, int(self.ripple_size), int(self.ripple_size))
                self.ripple_size -= 5
                if self.ripple_size < 0:
                    self.ripple_size = 0

        # Glowing Title with Color Transition
        r = int(0 + 50 * math.sin(self.color_phase))
        g = int(191 + 64 * math.cos(self.color_phase))
        b = 255
        painter.setFont(QFont("Orbitron", 36, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(r, g, b, 100), 3))
        painter.drawText(QRectF(0, 20, 1000, 80), Qt.AlignmentFlag.AlignCenter, "J.A.R.V.I.S")
        painter.setPen(QPen(QColor(r, g, b, 255), 1))
        painter.drawText(QRectF(0, 20, 1000, 80), Qt.AlignmentFlag.AlignCenter, "J.A.R.V.I.S")

        # Update animations
        self.rotation_angle = (self.rotation_angle + 3) % 360
        self.pulse_factor = (self.pulse_factor + 0.05) % 1
        self.scan_line_y = (self.scan_line_y + 2) % (self.height() - 100)
        self.color_phase = (self.color_phase + 0.03) % (2 * math.pi)
        if self.listening:
            self.waveform_points = [random.randint(0, 50) * math.sin(i * 0.5 + self.pulse_factor) for i in range(30)]

    def update_status(self, status):
        self.status_label.setText(status)
        self.listening = (status == "SYSTEM ONLINE")

    def handle_command(self, query):
        self.ripple_size = 50  # Trigger ripple effect on command
        if "open youtube" in query:
            self.status_label.setText("LAUNCHING YOUTUBE")
            HoloPanel(self, "Opening YouTube", 700, 150)
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif "open gmail" in query:
            self.status_label.setText("LAUNCHING GMAIL")
            HoloPanel(self, "Opening Gmail", 700, 150)
            speak("Opening Gmail")
            webbrowser.open("https://mail.google.com")
        elif "send message to" in query:
            name = query.split("send message to")[-1].strip()
            HoloPanel(self, f"WhatsApp: {name}", 700, 150)
            speak(f"Preparing WhatsApp for {name}. What should I say?")
            message = take_command()
            pywhatkit.sendwhatmsg_instantly(f"+{name}", message)
            self.status_label.setText(f"MESSAGE SENT TO {name.upper()}")
            HoloPanel(self, f"Sent to {name}", 700, 350)
            speak(f"Message sent to {name}")
        elif "exit" in query or "shutdown" in query:
            self.status_label.setText("SYSTEM SHUTTING DOWN")
            HoloPanel(self, "Shutting Down", 700, 150)
            speak("Shutting down, goodbye")
            QApplication.quit()

    def closeEvent(self, event):
        self.timer.stop()
        self.beep.stop()
        engine.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    speak("Initializing JARVIS interface. Systems online.")
    sys.exit(app.exec())