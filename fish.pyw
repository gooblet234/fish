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
        self.fric = 0.99 # change this if you want to be a fun person. Personally, im not a fun person, so I won't. But.. I bet you are! :D
        self.termv = 12

        self.dragging = False
        self.drag_stime = 0
        self.drag_spos = (0, 0) 
        self.offx = 0 # Short for offsetx
        self.offy = 0 # Short for offsety

        self.physp = False
        self.boom = False # Game breaking var btw, do not touch this. Literally a ticking time bomb. See what I did there? 
        self.sr = False # short for Sound Ready
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
        playsound("crying.mp3")
        self.movie.stop()
        self.movie = QMovie("explosion.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        playsound("explosion.mp3")
        time.sleep(2)
        QApplication.quit()

    def update_pos(self):
        if self.dragging or self.physp or self.boom:
            return
        
        screen = QApplication.primaryScreen().availableGeometry()
        x, y, w, h = self.x(), self.y(), self.width(), self.height()

        self.vely += self.grav
        if self.vely > self.termv:
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
        
        # need to fix i dont think this will work
        self.velx *= self.fric
        self.vely *= 0.99

        if bounced and self.sr:
            speed = sqrt(self.velx**2 + self.vely**2)
            volume = min(speed / self.termv, 1.0)
            # Random sounds cuz the splat pmo
            sound_file = random.choice(["blub.mp3","splat.mp3","splash.mp3","augh.mp3"])
            threading.Thread(target=lambda: playsound(sound_file), daemon=True).start()

        # self moving may only work on windows idek
        self.move(int(x + self.velx), int(y + self.vely))

class PanicWindow(QMainWindow):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.setWindowTitle("FISH PANIC!")
        self.setGeometry(400, 100, 200, 100)
        # button geometry different than main geometry
        self.button = QPushButton("Kill", self)
        self.button.setGeometry(20, 20, 160, 60)
        # UNFOLD THYSELF! - William Shakespeare (Hamlet) [probably]
        self.show()
    
    def closeEvent(self, event):
        self.superkill_fish()
        event.accept()
        # dont question this. you experience what you deserve. ;P

    def superkill_fish(self):
        playsound("gunshot.mp3")
        time.sleep(1)
        playsound("gunshot.mp3")
        time.sleep(0.25)
        playsound("sniper.mp3")
        time.sleep(0.25)
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    panic = PanicWindow(pet)
    sys.exit(app.exec_())