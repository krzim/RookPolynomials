import sys
from PyQt5 import QtGui as qg
from PyQt5 import QtWidgets as qw
from PyQt5 import QtCore as qc
import ctypes


class RPSolver(qw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        # Window Data
        self.setFixedSize(700, 600)
        self.center()
        self.setWindowTitle("Rook Polynomial Solver")
        self.setWindowIcon(qg.QIcon("images/rook_icon.png"))
        self.show()

    def initUI(self):
        self.board = Board()

        # Tool Tips
        qw.QToolTip.setFont(qg.QFont("SansSerif", 10))

        # Actions
        exitAct = qw.QAction(qg.QIcon(), "&Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.setStatusTip("Exit application")
        exitAct.triggered.connect(self.close)

        newAct = qw.QAction(qg.QIcon(), "&New", self)
        newAct.setShortcut("Ctrl+N")
        newAct.setStatusTip("Creates a new board")
        newAct.triggered.connect(self.new)

        # Labels
        rowLabel = qw.QLabel("Number of rows:", self)
        colLabel = qw.QLabel("Number of columns:", self)

        # Buttons

        # Comboboxes
        xCombo = qw.QComboBox(self)
        xCombo.label = "xCombo"
        xCombo.addItems(str(n) for n in range(1, 11))
        yCombo = qw.QComboBox(self)
        yCombo.label = "yCombo"
        yCombo.addItems(str(n) for n in range(1, 11))

        xCombo.activated[str].connect(self.onActivated)
        yCombo.activated[str].connect(self.onActivated)

        # Grid Layout
        widget = qw.QWidget()
        grid = qw.QGridLayout()
        grid.setSpacing(10)

        widget.setLayout(grid)
        grid.addWidget(rowLabel, 1, 0)
        grid.addWidget(colLabel, 2, 0)
        grid.addWidget(yCombo, 1, 1)
        grid.addWidget(xCombo, 2, 1)
        grid.addWidget(self.board, 1, 2, 10, 10)

        self.setCentralWidget(widget)

        # Status Bar
        self.statusBar().showMessage("Ready")

        # Menu Bar
        menubar = self.menuBar()
        menubar.clear()  # Clears menu bar when new window opened
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(newAct)
        fileMenu.addAction(exitAct)

    def new(self):
        self.initUI()

    def center(self):
        qr = self.frameGeometry()  # find size of window
        cp = qw.QDesktopWidget().availableGeometry().center()  #find center of desktop
        qr.moveCenter(cp)  # move center of qr rectangle to center of desktop
        self.move(qr.topLeft())  # move center of window to center of qr rectangle

    def closeEvent(self, e):  # handles close action and prompts user
        # message box syntax: titlebar, message, buttons, default button
        reply = qw.QMessageBox.question(self, "Quit",
                                               "Are you sure you want to quit?",
                                               qw.QMessageBox.Yes |
                                               qw.QMessageBox.No,
                                               qw.QMessageBox.No)
        if reply == qw.QMessageBox.Yes:
            e.accept()
        else:
            e.ignore()

    def keyPressEvent(self, e):
        if e.key() == qc.Qt.Key_Escape:
            self.close()

    def onActivated(self, val):
        sender = self.sender()
        if sender.label == "xCombo":
            self.board.x = int(val)
        else:
            self.board.y = int(val)
        self.board.drawBoard()  # Repaint the board


class Board(qw.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.x = 1
        self.y = 1

        sqrDim = 40
        color = self.palette().color(qg.QPalette.Background)

        # Set scene to same size as view and color as window
        self.setMaximumSize(400, 400)

        self.setFixedSize(self.x * sqrDim, self.y * sqrDim)
        rcontent = self.contentsRect()
        self.scene = qw.QGraphicsScene()
        self.scene.setBackgroundBrush(qg.QBrush(color))
        self.setSceneRect(0, 0, rcontent.width(), rcontent.height())
        self.setScene(self.scene)

        # set QGraphicsView attributes
        self.setRenderHints(qg.QPainter.Antialiasing |
            qg.QPainter.HighQualityAntialiasing)
        self.setViewportUpdateMode(qw.QGraphicsView.FullViewportUpdate)

        self.drawBoard()

    def drawBoard(self):
        self.scene.clear()
        sqrDim = 40

        self.setFixedSize(self.x * sqrDim, self.y * sqrDim)

        rcontent = self.contentsRect()
        self.setSceneRect(0, 0, rcontent.width(), rcontent.height())
        self.setScene(self.scene)

        for i in range(self.x):
            for j in range(self.y):
                square = Square(j, i)
                self.scene.addItem(square)


class Square(qw.QGraphicsItem):
    def __init__(self, row, col):
        super(Square, self).__init__()
        self.row = row
        self.col = col
        self.rect = qc.QRectF(0, 0, 40, 40)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setPen(qc.Qt.NoPen)
        if (self.row + self.col) & 1:
            painter.setBrush(qg.QColor(0x000000))
            painter.drawRect(self.col * 40, self.row * 40, 40, 40)
        else:
            painter.setBrush(qg.QColor(0xffffff))
            painter.drawRect(self.col * 40, self.row * 40, 40, 40)


if __name__ == "__main__":
    # Code to set the taskbar icon to match the window icon
    app_id = "RookPolynomials"  # application name
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = qw.QApplication(sys.argv)
    rpsolve = RPSolver()

    sys.exit(app.exec_())
