import sys
from PyQt5.QtWidgets import QApplication
from rpserver.rpgui import DecayWindow
from rpserver.rpacquire import RpInstrument
import rpserver.data as dt

cfg = dt.load_data('cfg.yaml')
rpi = RpInstrument(cfg.rphost, cfg.decimation, cfg.channel, cfg.trigger,
                   cfg.size)


if not QApplication.instance():
    app= QApplication(sys.argv)
else:
    app = QApplication.instance()
ex = DecayWindow(rpi)
sys.exit(app.exec_())
