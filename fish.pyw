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
                self.vx = 0
                self.vy = 0
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
            self.vx = (dx / duration) * 0.8
            self.vy = (dy / duration) * 0.8

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