import sys
import os
import time
import pyttsx3
import speech_recognition as sr
import webbrowser
import pywhatkit
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QRectF, QPointF, QThread, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
import random
import math

# Text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('voice', r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0')  # Male voice, raw string

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
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 255, 255, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)  # Apply shadow to the panel
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
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #0A0A0A;")
        
        # Boot sequence
        self.booting = True
        self.boot_phase = 0

        # Title Label
        self.title = QLabel("J.A.R.V.I.S", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setGeometry(0, 20, 1200, 80)
        self.title.setFont(QFont("Orbitron", 36, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #00FFFF; background: none;")
        title_shadow = QGraphicsDropShadowEffect(self)
        title_shadow.setBlurRadius(20)
        title_shadow.setColor(QColor(0, 255, 255, 200))
        title_shadow.setOffset(0, 0)
        self.title.setGraphicsEffect(title_shadow)  # Apply shadow to title

        # Status Label
        self.status_label = QLabel("INITIALIZING...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setGeometry(0, 720, 1200, 40)
        self.status_label.setFont(QFont("Orbitron", 12))
        self.status_label.setStyleSheet("color: #00CED1;")
        status_shadow = QGraphicsDropShadowEffect(self)
        status_shadow.setBlurRadius(10)
        status_shadow.setColor(QColor(0, 255, 255, 150))
        status_shadow.setOffset(0, 0)
        self.status_label.setGraphicsEffect(status_shadow)  # Apply shadow to status

        # Caption Label
        self.caption_label = QLabel("", self)
        self.caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.caption_label.setGeometry(0, 680, 1200, 30)
        self.caption_label.setFont(QFont("Orbitron", 10))
        self.caption_label.setStyleSheet("color: #00FFFF;")
        caption_shadow = QGraphicsDropShadowEffect(self)
        caption_shadow.setBlurRadius(10)
        caption_shadow.setColor(QColor(0, 255, 255, 150))
        caption_shadow.setOffset(0, 0)
        self.caption_label.setGraphicsEffect(caption_shadow)  # Apply shadow to caption

        # Dynamic Panels
        self.cpu_panel = QWidget(self)
        self.cpu_panel.setGeometry(50, 150, 200, 100)
        self.cpu_panel.setStyleSheet("background-color: rgba(0, 100, 255, 20); border: 1px solid cyan;")
        self.cpu_label = QLabel(f"CPU: {int(psutil.cpu_percent())}%", self.cpu_panel)
        self.cpu_label.setGeometry(10, 40, 180, 20)
        self.cpu_label.setFont(QFont("Orbitron", 10))
        self.cpu_label.setStyleSheet("color: cyan; background: none;")
        cpu_shadow = QGraphicsDropShadowEffect(self)
        cpu_shadow.setBlurRadius(15)
        cpu_shadow.setColor(QColor(0, 255, 255, 150))
        cpu_shadow.setOffset(0, 0)
        self.cpu_panel.setGraphicsEffect(cpu_shadow)  # Apply shadow to CPU panel

        self.time_panel = QWidget(self)
        self.time_panel.setGeometry(50, 270, 200, 100)
        self.time_panel.setStyleSheet("background-color: rgba(0, 100, 255, 20); border: 1px solid cyan;")
        self.time_label = QLabel(time.strftime("%H:%M:%S"), self.time_panel)
        self.time_label.setGeometry(10, 40, 180, 20)
        self.time_label.setFont(QFont("Orbitron", 10))
        self.time_label.setStyleSheet("color: cyan; background: none;")
        time_shadow = QGraphicsDropShadowEffect(self)
        time_shadow.setBlurRadius(15)
        time_shadow.setColor(QColor(0, 255, 255, 150))
        time_shadow.setOffset(0, 0)
        self.time_panel.setGraphicsEffect(time_shadow)  # Apply shadow to time panel

        self.history_panel = QWidget(self)
        self.history_panel.setGeometry(950, 150, 200, 200)
        self.history_panel.setStyleSheet("background-color: rgba(0, 100, 255, 20); border: 1px solid cyan;")
        self.history_label = QLabel("Command History:\n", self.history_panel)
        self.history_label.setGeometry(10, 20, 180, 160)
        self.history_label.setFont(QFont("Orbitron", 8))
        self.history_label.setStyleSheet("color: cyan; background: none;")
        history_shadow = QGraphicsDropShadowEffect(self)
        history_shadow.setBlurRadius(15)
        history_shadow.setColor(QColor(0, 255, 255, 150))
        history_shadow.setOffset(0, 0)
        self.history_panel.setGraphicsEffect(history_shadow)  # Apply shadow to history panel

        # Animation variables
        self.rotation_angle = 0
        self.pulse_factor = 0
        self.listening = False
        self.waveform_points = [0] * 30
        self.scan_line_y = 0
        self.radar_angle = 0
        self.particles = [{'x': 0, 'y': 0, 'angle': random.uniform(0, 360), 'speed': random.uniform(1, 3), 'trail': []} for _ in range(20)]
        self.sparks = []
        self.ripple_rings = []
        self.color_mode = "cyan"  # cyan, red, green, purple
        self.hex_angle = 0

        # Sounds
        self.hum = QSoundEffect()
        self.hum.setSource(QUrl.fromLocalFile(os.path.abspath("hum.wav")))
        self.hum.setLoopCount(-1)
        self.hum.setVolume(0.2)
        self.ui_sound = QSoundEffect()
        self.ui_sound.setSource(QUrl.fromLocalFile(os.path.abspath("ui.wav")))
        self.ui_sound.setVolume(0.3)
        self.startup_sound = QSoundEffect()
        self.startup_sound.setSource(QUrl.fromLocalFile(os.path.abspath("startup.wav")))
        self.startup_sound.setVolume(0.5)
        self.startup_sound.play()
        self.hum.play()

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        # Voice worker
        self.voice_worker = VoiceWorker()
        self.voice_worker.status_update.connect(self.update_status)
        self.voice_worker.command_detected.connect(self.handle_command)
        QTimer.singleShot(5000, self.voice_worker.start)  # Start after boot

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y = self.width() / 2, self.height() / 2
        colors = {
            "cyan": (0, 255, 255), "red": (255, 50, 50), "green": (50, 255, 50), "purple": (200, 0, 255)
        }
        base_color = colors[self.color_mode]

        # Boot Sequence
        if self.booting:
            if self.boot_phase < 50:
                painter.setBrush(QColor(0, 0, 0, 200))
                painter.drawRect(0, 0, self.width(), self.height())
                painter.setPen(QPen(QColor(*base_color, 100), 1))
                for i in range(0, self.width(), 50):
                    for j in range(0, self.height(), 50):
                        painter.drawPolygon(QPointF(i, j), QPointF(i + 25, j), QPointF(i + 25, j + 25), QPointF(i, j + 25))
                painter.setFont(QFont("Orbitron", 10))
                for i in range(5):
                    painter.drawText(50, 200 + i * 30, f"Initializing module {i + 1}...")
                self.boot_phase += 1
            elif self.boot_phase < 100:
                painter.setBrush(QColor(0, 0, 0, 255 - self.boot_phase * 2))
                painter.drawRect(0, 0, self.width(), self.height())
                self.boot_phase += 1
            else:
                self.booting = False
                speak("JARVIS online.")
                self.status_label.setText("SYSTEM ONLINE")
            return

        # Background Holographic Noise
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(50):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            painter.setBrush(QColor(*base_color, random.randint(5, 20)))
            painter.drawEllipse(x, y, 2, 2)

        # Hex Grid Overlay
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.hex_angle)
        painter.setPen(QPen(QColor(*base_color, 30), 1))
        for i in range(-5, 6):
            for j in range(-5, 6):
                x = i * 60 + j * 30
                y = j * 50
                painter.drawPolygon(QPointF(x, y), QPointF(x + 30, y), QPointF(x + 45, y + 25), QPointF(x + 30, y + 50), QPointF(x, y + 50), QPointF(x - 15, y + 25))
        painter.restore()
        self.hex_angle = (self.hex_angle + 1) % 360

        # Arc Reactor Core
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)
        for i in range(3):
            radius = 150 - i * 40
            gradient = QLinearGradient(-radius, -radius, radius, radius)
            gradient.setColorAt(0, QColor(*base_color, 100 - i * 20))
            gradient.setColorAt(1, QColor(*base_color, 20))
            painter.setPen(QPen(QBrush(gradient), 2 + i))
            painter.setBrush(QColor(*base_color, 20))
            painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.restore()

        # Radar Sweep
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.radar_angle)
        painter.setBrush(QColor(*base_color, 30))
        painter.drawPie(-150, -150, 300, 300, 0, 60 * 16)
        painter.restore()
        self.radar_angle = (self.radar_angle + 3) % 360

        # Particle Effects with Trails
        painter.setPen(Qt.PenStyle.NoPen)
        for particle in self.particles:
            particle['angle'] += particle['speed']
            x = center_x + math.cos(math.radians(particle['angle'])) * 150
            y = center_y + math.sin(math.radians(particle['angle'])) * 150
            particle['trail'].append((x, y))
            if len(particle['trail']) > 5:
                particle['trail'].pop(0)
            for i, (tx, ty) in enumerate(particle['trail']):
                painter.setBrush(QColor(*base_color, 100 - i * 20))
                painter.drawEllipse(int(tx), int(ty), 5 - i, 5 - i)
            particle['x'], particle['y'] = x, y

        # Sparks
        for spark in self.sparks[:]:
            spark['life'] -= 1
            if spark['life'] <= 0:
                self.sparks.remove(spark)
                continue
            x = spark['x'] + math.cos(math.radians(spark['angle'])) * spark['speed']
            y = spark['y'] + math.sin(math.radians(spark['angle'])) * spark['speed']
            painter.setBrush(QColor(*base_color, spark['life'] * 10))
            painter.drawEllipse(int(x), int(y), 5, 5)
            spark['x'], spark['y'] = x, y

        # Core Pulse with Bloom
        glow_size = 50 + math.sin(self.pulse_factor * math.pi) * 20
        gradient = QLinearGradient(center_x, center_y - glow_size, center_x, center_y + glow_size)
        gradient.setColorAt(0, QColor(*base_color, 200))
        gradient.setColorAt(1, QColor(*base_color, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - glow_size / 2), int(center_y - glow_size / 2), int(glow_size), int(glow_size))

        # HUD Grid
        painter.setPen(QPen(QColor(*base_color, 50), 1, Qt.PenStyle.DotLine))
        for x in range(0, self.width(), 50):
            painter.drawLine(x, 100, x, self.height() - 100)
        for y in range(100, self.height() - 100, 50):
            painter.drawLine(0, y, self.width(), y)

        # Scan Line with Sound
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*base_color, 30))
        painter.drawRect(0, self.scan_line_y, self.width(), 5)
        if self.scan_line_y % 100 == 0:
            self.ui_sound.play()

        # Waveform with Ripple
        if self.listening:
            painter.setPen(QPen(QColor(*base_color, 150), 2))
            path = QPainterPath()
            path.moveTo(350, 600)
            for i in range(len(self.waveform_points) - 1):
                x1, y1 = 350 + i * 20, 600 - self.waveform_points[i]
                x2, y2 = 350 + (i + 1) * 20, 600 - self.waveform_points[i + 1]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                path.quadTo(x1, y1, cx, cy)
            painter.drawPath(path)
            for ring in self.ripple_rings[:]:
                ring['size'] += 5
                ring['alpha'] -= 10
                if ring['alpha'] <= 0:
                    self.ripple_rings.remove(ring)
                    continue
                painter.setPen(QPen(QColor(*base_color, ring['alpha']), 2))
                painter.drawEllipse(int(center_x - ring['size'] / 2), int(600 - ring['size'] / 2), int(ring['size']), int(ring['size']))

        # Glowing Title with Lens Flare
        r, g, b = [int(c + 50 * math.sin(self.pulse_factor)) for c in base_color]
        painter.setFont(QFont("Orbitron", 36, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(r, g, b, 100), 3))
        painter.drawText(QRectF(0, 20, 1200, 80), Qt.AlignmentFlag.AlignCenter, "J.A.R.V.I.S")
        painter.setPen(QPen(QColor(r, g, b, 255), 1))
        painter.drawText(QRectF(0, 20, 1200, 80), Qt.AlignmentFlag.AlignCenter, "J.A.R.V.I.S")
        painter.setBrush(QColor(r, g, b, 50))
        painter.drawEllipse(600, 40, 20, 20)  # Lens flare

        # Update animations
        self.rotation_angle = (self.rotation_angle + 3) % 360
        self.pulse_factor = (self.pulse_factor + 0.05) % (2 * math.pi)
        self.scan_line_y = (self.scan_line_y + 2) % (self.height() - 100)
        if self.listening:
            self.waveform_points = [random.randint(0, 50) * math.sin(i * 0.5 + self.pulse_factor) for i in range(30)]
        self.cpu_label.setText(f"CPU: {int(psutil.cpu_percent())}%")
        self.time_label.setText(time.strftime("%H:%M:%S"))

    def update_status(self, status):
        self.status_label.setText(status)
        self.listening = (status == "SYSTEM ONLINE")

    def handle_command(self, query):
        self.ripple_rings.append({'size': 50, 'alpha': 100})
        self.sparks.extend([{'x': 600, 'y': 600, 'angle': random.uniform(0, 360), 'speed': random.uniform(2, 5), 'life': 20} for _ in range(5)])
        self.ui_sound.play()
        self.caption_label.setText(query.upper())
        self.history_label.setText(self.history_label.text() + f"{query}\n")
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
            self.color_mode = "red"
            HoloPanel(self, "Shutting Down", 700, 150)
            speak("Shutting down, goodbye")
            QApplication.quit()
        elif "change theme" in query:
            if "red" in query:
                self.color_mode = "red"
            elif "green" in query:
                self.color_mode = "green"
            elif "purple" in query:
                self.color_mode = "purple"
            else:
                self.color_mode = "cyan"
            speak(f"Switching to {self.color_mode} mode.")

    def closeEvent(self, event):
        self.timer.stop()
        self.hum.stop()
        self.ui_sound.stop()
        engine.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.show()
    sys.exit(app.exec())