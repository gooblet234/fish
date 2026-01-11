import sys
import time
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QMainWindow, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie
from playsound import playsound

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FiSH")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setGeometry(100, 100, 200, 200)

        self.label = QLabel(self)
        self.movie = QMovie("pet.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setScaledContents(True)
        self.label.setGeometry(0, 0, self.width(), self.height())

        self.velx = 0
        self.vely = 0
        self.grav = 0.7
        self.bounce_dampening = 0.7
        self.fric = 0.99
        self.termv = 12

        self.dragging = False
        self.drag_stime = 0
        self.drag_spos = (0, 0)
        self.offx = 0
        self.offy = 0

        self.physp = False
        self.boom = False
        self.sr = False
        self.splatq = []
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pos)
        self.timer.start(30)

        threading.Thread(target=self.preload_audio, daemon=True).start()
        self.show()

    def preload_audio(self):

        threading.Thread(target=lambda: None, daemon=True).start()
        time.sleep(4)
        self.sr = True
    
    def resizeEvent(self, event):
        self.label.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.dragging:
                self.dragging = True
                self.drag_stime = time.time()
                self.drag_spos = (self.x(), self.y())
                self.offx = event.x()
                self.offy = event.y()
                self.velx = 0
                self.vely = 0
        elif event.button() == Qt.RightButton:
            self.physp = not self.physp
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalX() - self.offx, event,globalY() - self.offy)
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggin:
            self.dragging = False
            end_pos = (self.x(), self.y())
            duration = max(time.time() - self.drag_stime, 0.01)
            dx = end_pos[0] - self.drag_spos[0]
            dy = end_pos[1] - self.drag_spos[1]
            self.velx = (dx / duration) * 0.8
            self.vely = (dy / duration) * 0.8

    def closeEvent(self, event):
        if self.physp:
            event.accept()
        elif not self.boom:
            event.ignore()
            threading.Thread(target=self.cry_and_explode, daemon=True).start()
        else:
            event.accept()

    def cry_and_explode(self):
        if self.boom:
            return
        self.boom = True
        self.physp = True
        self.dragging = False
        playsound("explosion.mp3")
        time.sleep(2)
        QApplication.quit()

    def update_position(self):
        if self.dragging or self.physics_paused or self.exploding:
            return
        
        screen = QApplication.primaryScreen().availableGeometry()
        x, y, w, h = self.x(), self.y(), self.width(), self.height()

        self.vely += self.grav
        if self.vely > self.termv
            self.vely = self.termv

        bounced = False
        if y + h >= screen.height():
            y = screen.height() - h
            self.vely = -self.vely * self.bounce_dampening
            bounced = True
        if y <= 0:
            y = 0
            self.vely = -self.vely * self.bounce_dampening
            bounced = True
        if x + w >= screen.width():
            x = screen.width() - w
            self.velx = -self.velx * self.bounce_dampening
            bounced = True
        if x <= 0:
            x = 0
            self.velx = -self.velx * self.bounce_dampening
            bounced = True
        
        self.velx *= self.fric
        self.vy *= 0.99