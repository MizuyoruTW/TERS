from PyQt5.QtWidgets import QMainWindow
import mainwindow

class MainUi(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)