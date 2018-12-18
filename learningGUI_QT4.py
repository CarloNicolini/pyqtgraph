import sys
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
#from matplotlib.pylab import *
from matplotlib.figure import Figure
import numpy as np  # mathematics library


class WorkThread(QtCore.QThread):
    """ This class will run underground in the main widget, and emits signals
    with some temporization parameter """
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.n_points = 200
        # This thread will simulate data collection every 100 milliseconds,
        # by generating a vector of 20 random values in [0,1000] units
        self.timer = QtCore.QTimer(self)
        self.collection_interval_milliseconds = 100
        self.timer.timeout.connect(self.collect_data)

    def __del__(self):
        self.wait()

    def collect_data(self):
        # Emit 200 random points from [0,1000] 
        self.emit(QtCore.SIGNAL("data_emitted"),
                  1000 * np.random.random(self.n_points))


class MyCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Units")
        self.axes.grid(True)
        #timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        # timer.start(1000)

    def update_figure(self, data):
        self.axes.plot(data, 'r')
        self.axes.grid(True)
        self.draw()


class PlottingWidget(QtGui.QWidget):

    def __init__(self):
        super(PlottingWidget, self).__init__()
        # Initialize the variables in the class PlottingWidget
        self.initUI()

    def initUI(self):
        # Create the start button
        self.startButton = QtGui.QPushButton('Start!')
        self.startButton.setToolTip('Simulate starting data collection')

        # Create the stop button
        self.stopButton = QtGui.QPushButton('STOP')
        self.stopButton.setToolTip('Simulate data collection interruption')

        # Put the two buttons in a horizontal layout
        # 1. Create the horizontal box layout
        hbox = QtGui.QHBoxLayout()
        # hbox.addStretch(0)
        # Add startButton and stopButton
        hbox.addWidget(self.startButton)
        hbox.addWidget(self.stopButton)

        # Then create a vertical layout, that will fit the entire widget,
        # with the horizontal layout as first row and the canvas as second row
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)

        # Let's create our canvas to draw emitted data on
        self.myMplCanvas = MyCanvas(self)
        # Connect the canvas plotting function to every emission of signals
        # from the worker thread
        vbox.addWidget(self.myMplCanvas)

        # Set the main layout of the widget as the vertical layout we've just
        self.setLayout(vbox)

        # Finally let's set the properties of the window
        # Set the size of the widget
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('MyPlottingWidget')
        self.show()

        # Connect the press of the button with the creation of a thread that
        # emits data every x seconds
        self.startButton.clicked.connect(self.startButton_clicked)
        self.stopButton.clicked.connect(self.stopButton_clicked)

        # Create the workthread that lives in the main widget
        self.workThread = WorkThread()
        # and connect the emission of signals from the thread to 
        # update of the figure canvas
        self.connect(self.workThread, QtCore.SIGNAL(
            "data_emitted"), self.myMplCanvas.update_figure)

    def startButton_clicked(self):
        # when the start button will emit the pressed signal, this will connect
        # to the workThread method that emits the data every 100 milliseconds
        # simulating a running microscope scan
        self.workThread.timer.start(self.workThread.collection_interval_milliseconds)
        
    def stopButton_clicked(self):
        self.workThread.timer.stop()


def main():

    app = QtGui.QApplication(sys.argv)
    ex = PlottingWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
