from Earthquake_Server import *
from PyQt5 import QtWidgets, QtCore
import mainwindow
import time
import sys

class About(QtWidgets.QWidget):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi()
	
	def setupUi(self):
		self.setWindowTitle("關於")
		self.resize(200, 200)
		
		self.label = QtWidgets.QLabel()
		self.label.setText("本程式由水夜工作坊製作\n資訊由中央氣象局提供")
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		
		self.CancelButton = QtWidgets.QPushButton()
		self.CancelButton.setText("關閉")
		self.CancelButton.clicked.connect(self.close)
		
		self.SiteLink = QtWidgets.QLabel()
		self.SiteLink.setText("<a href='https://github.com/MizuyoruTW'>https://github.com/MizuyoruTW</a>")
		self.SiteLink.setOpenExternalLinks(True)
		self.SiteLink.setAlignment(QtCore.Qt.AlignCenter)
		
		h_layout = QtWidgets.QVBoxLayout()
		h_layout.addWidget(self.label)
		h_layout.addWidget(self.SiteLink)
		h_layout.addWidget(self.CancelButton)
		
		self.setLayout(h_layout)

class Main(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
	#EQ=Earthquake_Server()
	new_index = 1
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.about.clicked.connect(self.About_clicked)
		self.AboutWindow = About()
		#self.EQ.update()
	
	def About_clicked(self):
		self.AboutWindow.show()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = Main()
	MainWindow.show()
	sys.exit(app.exec_())