import sys
import time
import threading
from math import sqrt
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QMainWindow, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from playsound import playsound

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fishy Fish Pet")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 200, 200)

        # GIF
        self.label = QLabel(self)
        self.movie = QMovie("pet.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setScaledContents(True)
        self.label.setGeometry(0, 0, self.width(), self.height())

        # Physics
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5
        self.bounce_damping = 0.6
        self.friction = 0.98
        self.terminal_velocity = 15

        # Drag
        self.dragging = False
        self.drag_start_time = 0
        self.drag_start_pos = (0, 0)
        self.offset_x = 0
        self.offset_y = 0

        # Flags
        self.physics_paused = False
        self.exploding = False
        self.sound_ready = False
        self.blub_queue = []

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(30)

        # Preload audio in background thread, wait 2s before enabling blubs
        threading.Thread(target=self.preload_audio, daemon=True).start()

        self.show()

    def preload_audio(self):
        # Play a short silent dummy to initialize audio system
        threading.Thread(target=lambda: None, daemon=True).start()
        time.sleep(4)
        self.sound_ready = True

    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.height())

    # Mouse events
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.dragging:
                self.dragging = True
                self.drag_start_time = time.time()
                self.drag_start_pos = (self.x(), self.y())
                self.offset_x = event.x()
                self.offset_y = event.y()
                self.vx = 0
                self.vy = 0
        elif event.button() == Qt.RightButton:
            self.physics_paused = not self.physics_paused

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalX() - self.offset_x, event.globalY() - self.offset_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            end_pos = (self.x(), self.y())
            duration = max(time.time() - self.drag_start_time, 0.01)
            dx = end_pos[0] - self.drag_start_pos[0]
            dy = end_pos[1] - self.drag_start_pos[1]
            self.vx = (dx / duration) * 0.8
            self.vy = (dy / duration) * 0.8

    def closeEvent(self, event):
        if self.physics_paused:
            event.accept()
        elif not self.exploding:
            event.ignore()
            threading.Thread(target=self.cry_and_explode, daemon=True).start()
        else:
            event.accept()

    def cry_and_explode(self):
        if self.exploding:
            return
        self.exploding = True
        self.physics_paused = True
        self.dragging = False

        # Cry first
        playsound("crying.mp3")

        # Explosion GIF
        self.movie.stop()
        self.movie = QMovie("explosion.gif")
        self.label.setMovie(self.movie)
        self.movie.start()

        # Explosion sound
        playsound("explosion.mp3")

        # Close everything
        time.sleep(2)
        QApplication.quit()

    def update_position(self):
        if self.dragging or self.physics_paused or self.exploding:
            return

        screen = QApplication.primaryScreen().availableGeometry()
        x, y, w, h = self.x(), self.y(), self.width(), self.height()

        self.vy += self.gravity
        if self.vy > self.terminal_velocity:
            self.vy = self.terminal_velocity

        bounced = False
        if y + h >= screen.height():
            y = screen.height() - h
            self.vy = -self.vy * self.bounce_damping
            bounced = True
        if y <= 0:
            y = 0
            self.vy = -self.vy * self.bounce_damping
            bounced = True
        if x + w >= screen.width():
            x = screen.width() - w
            self.vx = -self.vx * self.bounce_damping
            bounced = True
        if x <= 0:
            x = 0
            self.vx = -self.vx * self.bounce_damping
            bounced = True

        # Friction
        self.vx *= self.friction
        self.vy *= 0.99

        # Blub based on velocity
        if bounced and self.sound_ready:
            speed = sqrt(self.vx**2 + self.vy**2)
            volume = min(speed / self.terminal_velocity, 1.0)
            threading.Thread(target=lambda: playsound("blub.mp3"), daemon=True).start()

        self.move(int(x + self.vx), int(y + self.vy))


class PanicWindow(QMainWindow):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.setWindowTitle("FISH PANIC!!!")
        self.setGeometry(400, 100, 200, 100)

        self.button = QPushButton("Kill fish", self)
        self.button.setGeometry(20, 20, 160, 60)
        self.button.clicked.connect(self.kill_fish)

        self.show()

    def closeEvent(self, event):
        self.kill_fish()
        event.accept()

    def kill_fish(self):
        playsound("gunshot.mp3")
        time.sleep(1)
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    panic = PanicWindow(pet)
    sys.exit(app.exec_())
