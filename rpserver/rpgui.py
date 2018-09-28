import numpy as np
import sys
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QLineEdit, QMainWindow, QLabel,
                           QAction, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QVBoxLayout, QMenu, QMenuBar, QTextEdit, QFileDialog, QApplication, QComboBox,
                           QSpinBox)
from PyQt5.QtCore import QRect
import pyqtgraph as pg
import time
from .rpacquire import RpInstrument


class Dialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, opts, host, channel):
        super(Dialog, self).__init__()
        self.createFormGroupBox(opts, host, channel)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Configuration parameters")
        self.show()

    def createFormGroupBox(self, opts, host, channel):
        self.formGroupBox = QGroupBox("Configuration parameters")
        channel_combobox = QComboBox()
        channel_combobox.addItem('1')
        channel_combobox.addItem('2')
        # Number of samples
        samples_ledit = QLineEdit(str(opts.nsamples))

        layout = QFormLayout()
        layout.addRow(QLabel("Samples:"), samples_ledit)
        layout.addRow(QLabel("Channel:"), channel_combobox)
        layout.addRow(QLabel("IP:"),QLineEdit(host))
        opts.nsamples = int(samples_ledit.text())
        self.formGroupBox.setLayout(layout)


class DecayWindow(QMainWindow):
    def __init__(self, rpi):
        super(DecayWindow, self).__init__()
        self.rpi = rpi
        self.setGeometry(30, 30, 700, 700)
        self.setWindowTitle("Lifetime Measurement with Red Pitaya")
        # Define a new window for the layout
        self.window = QWidget()
        self.setCentralWidget(self.window)
        # Plot window configuration
        # a figure instance to plot on
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # pg.setConfigOption('background', 'w')
        # self.graphicsView = pg.PlotWidget(self.window)
        # self.graphicsView.addLegend()
        # Buttons
        # self.lifetime_button = QPushButton("Lifetime")
        # Button events
        # self.lifetime_button.clicked.connect(self.lifetime)
        # Adding labels and linedits
        self.info_label = QLabel('Ready to calibrate.')
        self.wlen_ledit = QLineEdit(self)
        self.freq_ledit = QLineEdit(self)
        self.duty_ledit = QLineEdit(self)
        self.lpower_ledit = QLineEdit(self)
        self.filter_ledit = QLineEdit(self)

        # Using a Grid layout
        grid = QGridLayout()
        grid.setSpacing(5)
        # Line edits
        self.addLinedit(grid,  QLabel('Wavelength'), self.wlen_ledit, 0, 0)
        self.addLinedit(grid,  QLabel('Frequency'), self.freq_ledit, 1, 0)
        self.addLinedit(grid,  QLabel('Duty Cycle'), self.duty_ledit, 2, 0)
        self.addLinedit(grid,  QLabel('Laser power'), self.lpower_ledit, 0, 2)
        self.addLinedit(grid,  QLabel('Optical filter'), self.filter_ledit, 1, 2)
        # Buttons
        # grid.addWidget(self.lifetime_button,3,2,1,1)
        # Graphics
        # grid.addWidget(self.graphicsView, 3, 0, 2, 4)
        grid.addWidget(self.toolbar, 3, 0, 1, 4)
        grid.addWidget(self.canvas, 4, 0, 2, 4)
        grid.addWidget(self.info_label, 6, 0, 1, 1)
        # To avoid resizing of grid cells
        self.window.setLayout(grid)
        # Munu configuration
        self.menuInit()
        self.show()

    def menuInit(self):
        # File saving
        self.savefile = QAction("&Save File", self)
        self.savefile.setShortcut("Ctrl+S")
        self.savefile.setStatusTip('Save File')
        self.savefile.triggered.connect(self.saveFile)
        # Calibration
        self.calibrate = QAction("&Calibrate", self)
        self.calibrate.setStatusTip('Calibrate')
        self.calibrate.triggered.connect(self.calibrateTrigger)
        # Acquisition
        self.acquire = QAction("&Acquire", self)
        self.acquire.setStatusTip('Acquire')
        self.acquire.triggered.connect(self.acquire_channel)
        # Lifetime meassurement
        self.lifetime = QAction("&Lifetime", self)
        # self.lifetime.setStatusTip('Lifetime')
        self.lifetime.triggered.connect(self.lifetime_meassure)
        # Configurate
        self.configurate = QAction("&Configurate", self)
        # self.lifetime.setStatusTip('Configurate')
        self.configurate.triggered.connect(self.configurateAcquisition)
        # Adding the menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        operationsMenu = mainMenu.addMenu('&Operations')
        fileMenu.addAction(self.savefile)
        operationsMenu.addAction(self.calibrate)
        operationsMenu.addAction(self.acquire)
        operationsMenu.addAction(self.lifetime)
        operationsMenu.addAction(self.configurate)

    def addLinedit(self, grid, label, linedit, row, col):
        grid.addWidget(label, row, col, 1, 1)
        grid.addWidget(linedit, row, col+1, 1, 1)

    def acquire_channel(self):
        t, v1 = self.rpi.acquire_triggered()
        self.graphicsView.clear()
        handler = self.graphicsView.plot(t, v1,pen ='r')
        self.info_label.setText('Signal acquired.')

    def calibrateTrigger(self):
        t, v1, status = self.rpi.calibration_run()
        self.graphicsView.clear()
        handler = self.graphicsView.plot(t, v1,pen ='r')
        self.info_label.setText(status)
        return

    def lifetime_meassure(self):
        try:
            set_wlen = int(self.wlen_ledit.text())
            if set_wlen < 200 or set_wlen > 900:
                self.info_label.setText('Please, enter a wavelength in the valid range (200 - 900 nm).')
                QApplication.processEvents()
                return
        except:
            self.info_label.setText('Please, enter wavelength in nm.')
            QApplication.processEvents()
            return
        ax = self.figure.add_subplot(111)

        for hist, bins, status in self.rpi.acquire_decay():
            # self.graphicsView.clear()
            # handler = self.graphicsView.plot(bins[:-1]*1000, hist, symbol='o', size=1)
            # discards the old graph
            ax.clear()
            # plot data
            ax.plot(bins[:-1]*1000, hist, 'o--')
            # refresh canvas
            self.canvas.draw()
            self.info_label.setText(status)
            QApplication.processEvents()
        self.wlen_ledit.clear()
        return

    def saveFile(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        filename = name[0]
        # text = self.textEdit.toPlainText()
        np.save(filename+'.npy', self.counts)
        return

    def configurateAcquisition(self):
        configDialog = Dialog(self.rpi.opts, self.rpi.host, self.rpi.channel)
        configDialog.exec_()
        return

    def clearplot_clk(self):
        self.graphicsView.clear()
        self.l.scene().removeItem(self.l)
        self.graphicsView.plotItem.addLegend()
