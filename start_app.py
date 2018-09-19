import sys
from PyQt5.QtWidgets import QApplication
from rpserver.rpgui import DecayWindow

if not QApplication.instance():
    app= QApplication(sys.argv)
else:
    app = QApplication.instance()
ex = DecayWindow()
sys.exit(app.exec_())
