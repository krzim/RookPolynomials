import sys
from PyQt5 import QtGui, QtWidgets
import ctypes

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Test(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setGeometry(800, 400, 600, 600)
        self.setWindowTitle("Rook Polynomial Solver")
        self.setWindowIcon(QtGui.QIcon("images/rook_icon.png"))

        self.show()

if __name__ == "__main__":
    # Code to set the taskbar icon to match the window icon
    app_id = "RookPolynomials"  # application name
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QtWidgets.QApplication(sys.argv)
    test = Test()




    sys.exit(app.exec_())
