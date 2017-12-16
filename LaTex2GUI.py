from PyQt5 import QtGui, QtWidgets, QtCore

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MathTextLabel(QtWidgets.QWidget):
    def __init__(self, mathText, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent, **kwargs)

        l = QtWidgets.QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        r, g, b, a = self.palette().window().color().getRgbF()
        print(r, g, b, a)

        self._figure = Figure(edgecolor=(r, g, b), facecolor=(r, g, b))
        self._canvas = FigureCanvas(self._figure)
        l.addWidget(self._canvas)

        self._figure.clear()
        text = self._figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            size=QtWidgets.qApp.font().pointSize() * 2)
        self._canvas.draw()

        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self._figure.set_size_inches(w / 80, h / 80)
        self.setFixedSize(w, h)


if __name__ == '__main__':
    from sys import argv, exit


    class Widget(QtWidgets.QWidget):
        def __init__(self, parent=None, **kwargs):
            QtWidgets.QWidget.__init__(self, parent, **kwargs)

            l = QtWidgets.QVBoxLayout(self)
            l.addWidget(QtWidgets.QLabel("<h1>Discrete Fourier Transform</h1>"))

            mathText = r'$X_k = \sum_{n=0}^{N-1} x_n . e^{\frac{-i2\pi kn}{N}}$'
            l.addWidget(MathTextLabel(mathText, self),
                        alignment=QtCore.Qt.AlignHCenter)


    a = QtWidgets.QApplication(argv)
    w = Widget()
    w.show()
    w.raise_()
    exit(a.exec_())

    """
    another solution??
    
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

    # Get window background color
    bg = self.palette().window().color()
    cl = (bg.redF(), bg.greenF(), bg.blueF())

    # Create figure, using window bg color
    self.fig = Figure(edgecolor=cl, facecolor=cl)

    # Add FigureCanvasQTAgg widget to form
    self.canvas = FigureCanvasQTAgg(self.fig)        
    self.tex_label_placeholder.layout().addWidget(self.canvas)

    # Clear figure
    self.fig.clear()

    # Set figure title
    self.fig.suptitle('$TeX$',
                      x=0.0, y=0.5, 
                      horizontalalignment='left',
                      verticalalignment='center')
    self.canvas.draw()
    """