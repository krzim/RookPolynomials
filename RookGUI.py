import sys
from PyQt5 import QtGui as qg
from PyQt5 import QtWidgets as qw
from PyQt5 import QtCore as qc
import ctypes
import RookPolynomials as rp
import LaTex2GUI as l2g


class RPSolver(qw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        # Window Data
        self.setFixedSize(1000, 550)
        self.center()
        self.setWindowTitle("Rook Polynomial Solver")
        self.setWindowIcon(qg.QIcon("images/rook_icon.png"))
        self.show()

    def initUI(self):
        # Board
        self.board = Board(parent=self)

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
        solveBtn = qw.QPushButton("Solve", self)
        solveBtn.clicked.connect(self.board.solve)
        resetBtn = qw.QPushButton("Reset", self)
        resetBtn.clicked.connect(self.reset)


        # Comboboxes
        self.xCombo = qw.QComboBox(self)
        self.xCombo.label = "xCombo"
        self.xCombo.addItems(str(n) for n in range(1, 11))
        self.xCombo.setCurrentIndex(7)  # Default to 8 for 8x8 board
        self.yCombo = qw.QComboBox(self)
        self.yCombo.label = "yCombo"
        self.yCombo.addItems(str(n) for n in range(1, 11))
        self.yCombo.setCurrentIndex(7)  # Default to 8 for 8x8 board

        self.xCombo.activated[str].connect(self.comboActivated)
        self.yCombo.activated[str].connect(self.comboActivated)

        # Grid Layout
        widget = qw.QWidget()
        grid = qw.QGridLayout()
        grid.setSpacing(10)
        # Because I can't get my LaTex label to play nice
        grid.setContentsMargins(40, 10, 10, 10)

        widget.setLayout(grid)
        grid.addWidget(rowLabel, 1, 0)
        grid.addWidget(colLabel, 2, 0)
        grid.addWidget(self.yCombo, 1, 1)
        grid.addWidget(self.xCombo, 2, 1)
        grid.addWidget(solveBtn, 4, 0)
        grid.addWidget(resetBtn, 3, 0)
        grid.addWidget(self.board, 1, 2, 9, 8)
        grid.addWidget(self.board.polyLabel, 9, 0, 1, 9)
        grid.setAlignment(self.board.polyLabel, qc.Qt.AlignCenter)
        grid.setAlignment(self.board, qc.Qt.AlignTop | qc.Qt.AlignLeft)


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
        self.xCombo.setCurrentIndex(7)  # Default to 8 for 8x8 board
        self.yCombo.setCurrentIndex(7)  # Default to 8 for 8x8 board
        polylabel = self.board.polyLabel  # Main UI points to this polylabel
        self.board.initUI(parent=self)
        self.board.polyLabel = polylabel  # Update board polylabel to main UI's
        self.board.solve()

    def reset(self):
        polylabel = self.board.polyLabel  # Main UI points to this polylabel
        self.board.initUI(self.board.x, self.board.y, self)  # new board same size
        self.board.polyLabel = polylabel  # Update board polylabel to main UI's
        self.board.solve()

    def center(self):
        qr = self.frameGeometry()  # find size of window
        cp = qw.QDesktopWidget().availableGeometry().center()  # cntr of desktop
        qr.moveCenter(cp)  # move center of qr rectangle to center of desktop
        self.move(qr.topLeft())  # move center of window to center of qr

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
        elif e.key() == qc.Qt.Key_Return:
            self.board.solve()

    def comboActivated(self, val):
        sender = self.sender()
        if sender.label == "xCombo":
            self.board.x = int(val)
        else:
            self.board.y = int(val)
        self.board.drawBoard()  # Repaint the board


class Board(qw.QGraphicsView):
    def __init__(self, x=8, y=8, parent=None):
        super().__init__()
        self.initUI(x, y, parent)

    def initUI(self, x=8, y=8, parent=None):
        # Default to 8x8 board
        self.x = x
        self.y = y
        self.parent = parent
        self.badCells = set()
        self.polyLabel = l2g.MathTextLabel("Select bad cells and click Solve"
                                           + " or hit Enter")
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
                square = Square(i * 40, j * 40, self)
                if (j, i) in self.badCells:
                    square.bad = True
                square.setFlag(qw.QGraphicsItem.ItemIsSelectable, True)
                square.setAcceptHoverEvents(True)
                self.scene.addItem(square)

    def solve(self):
        rpBoard = rp.Board(self.y, self.x, self.badCells)
        latex = rpBoard.solve().latexFormat()
        self.polyLabel.updateText(latex)
        centralWidget = self.parent.centralWidget()
        centralWidget.update()
        centralWidget.layout().setAlignment(self.polyLabel, qc.Qt.AlignCenter)
        print(latex)




class Square(qw.QGraphicsItem):
    def __init__(self, x, y, board):
        super(Square, self).__init__()
        self.parent = board
        self.pen = qg.QPen()
        self.pen.setColor(qg.QColor(0x000000))

        self.brush = qg.QBrush()

        self.x = x
        self.y = y
        self.bad = False

        self.rect = qc.QRectF(self.x, self.y, 40, 40)

        self.setFlag(qw.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

    # def hoverEnterEvent(self, event):
    #     print(self.parent)
    #     qw.QGraphicsItem.hoverEnterEvent(self, event)
    #
    # def hoverLeaveEvent(self, event):
    #     print("goodbye")
    #     qw.QGraphicsItem.hoverLeaveEvent(self, event)

    def mousePressEvent(self, event):
        # select object
        self.bad = self.bad ^ True  # toggle bad cell on click
        if self.bad:
            self.parent.badCells.add((self.y//40, self.x//40))
        else:
            self.parent.badCells.remove((self.y//40, self.x//40))
        qw.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        qw.QGraphicsItem.mousePressEvent(self, event)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setPen(qc.Qt.NoPen)
        if option.state & qw.QStyle.State_MouseOver:
            pen = qg.QPen(qc.Qt.red, 2, qc.Qt.DashLine, qc.Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(qg.QBrush(qc.Qt.gray, qc.Qt.DiagCrossPattern))

            painter.drawRect(self.x, self.y, 39, 39)
            painter.drawLine(self.x, self.y, self.x + 40, self.y + 40)
            painter.drawLine(self.x + 40, self.y, self.x, self.y + 40)
            return

        if self.bad:
            badBrush = qg.QBrush(qc.Qt.gray, qc.Qt.DiagCrossPattern)
            painter.setBrush(badBrush)
            painter.drawRect(self.x, self.y, 40, 40)
            return

        if (self.x//40 + self.y//40) & 1:  # Creates alternating white/black
            painter.setBrush(qg.QColor(0x000000))
            painter.drawRect(self.x, self.y, 40, 40)
        else:
            painter.setBrush(qg.QColor(0xffffff))
            painter.drawRect(self.x, self.y, 40, 40)


if __name__ == "__main__":
    if sys.platform == "win32" or sys.platform == "win64":
        # Code to set the Windows taskbar icon to match the window icon
        app_id = "RookPolynomials"  # application name
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = qw.QApplication(sys.argv)
    rpsolve = RPSolver()

    sys.exit(app.exec_())
