import sys
from PyQt5.QtWidgets import QApplication
from rpserver.rpgui import DecayWindow
from rpserver.rpacquire import RpInstrument, Options
import rpserver.data as dt

cfg = dt.load_data('cfg.yaml')
opts = Options(nsamples=cfg.nsamples,
               maxwindows = 1E5,
               timeout=100)
rpi = RpInstrument(cfg.rphost, cfg.decimation, cfg.channel, cfg.trigger_channel, opts,
                   cfg.size, sim=False)

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()
ex = DecayWindow(rpi)
sys.exit(app.exec_())
