import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLineEdit, QMainWindow, QLabel

import pyqtgraph as pg

from .rpacquire import RpInstrument

class DecayWindow(QMainWindow):

    def __init__(self, rpi):
        super().__init__()
        self.title = 'Lifetime Measurement'
        self.left = 30
        self.top = 30
        self.width = 700
        self.height = 700
        self.rpi = rpi
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        # Main window dimensions
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.window = QWidget() #defino nueva ventana para aplicar layout
        self.setCentralWidget(self.window) #pongo la ventana como central

        pg.setConfigOption('background', 'w')
        self.graphicsView = pg.PlotWidget(self.window)
        self.graphicsView.addLegend()

        self.acquire_btn = QPushButton("Acquire")
        self.plot_btn = QPushButton("Calibrate")
        self.clearplot_btn = QPushButton("Clear")

        self.acquire_btn.clicked.connect(self.acquire) #conecto botones a su función
        self.plot_btn.clicked.connect(self.calibrate)
        self.clearplot_btn.clicked.connect(self.clearplot_clk)

        # Textboxes with options
        # Frequency information
        self.freq_label = QLabel('Frequency')
        self.freq_ledit = QLineEdit(self)
        # Server Ip
        self.host_label = QLabel('IP')
        self.host_ledit= QLineEdit(self)
        self.host_ledit.setText(self.rpi.host)
        # Channel
        self.channel_label = QLabel('Channel')
        self.channel_ledit = QLineEdit(self)
        self.channel_ledit.setText(str(self.rpi.channel))
        # Wavelength
        self.wlen_label = QLabel('Wavelength')
        self.wlen_ledit = QLineEdit(self)
        self.wlen_ledit.setText('490')


        grid = QGridLayout() #defino layout grilla
        grid.setSpacing(10)
        grid.addWidget(self.host_label, 1,0,1,1)
        grid.addWidget(self.host_ledit,2,0,1,1)
        grid.addWidget(self.channel_label, 1,1,1,1)
        grid.addWidget(self.channel_ledit,2,1,1,1)
        grid.addWidget(self.freq_label, 1,2,1,1)
        grid.addWidget(self.freq_ledit,2,2,1,1)
        grid.addWidget(self.plot_btn,3,1)
        grid.addWidget(self.acquire_btn,3,0) #agrego botones a la grilla
        grid.addWidget(self.clearplot_btn,3,2)
        grid.addWidget(self.graphicsView,4,0,1,4) # agrego gráfico
        self.window.setLayout(grid)

        self.show()

    def acquire(self):
        t, v1 = self.rpi.acquire_channel()
        name = 'Lifetime decay'
        self.graphicsView.clear()
        handler = self.graphicsView.plot(t, v1,pen ='r')

    def calibrate(self):
        t, v1 = self.rpi.calibration_run()
        name = 'Lifetime decay'
        self.graphicsView.clear()
        handler = self.graphicsView.plot(t, v1,pen ='r')

    def plot_clk(self):
        x = np.arange(0,100,1)
        y = np.arange(0,100,1)
        name = 'curva random'
        self.p1 = self.graphicsView.plot(x,y,pen ='r')
        self.l = self.graphicsView.plotItem.legend
        self.l.addItem(self.p1, name)

    def clearplot_clk(self):
        self.graphicsView.clear()
        self.l.scene().removeItem(self.l)
        self.graphicsView.plotItem.addLegend()
