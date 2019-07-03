from Earthquake_Server import Earthquake_Server
from PyQt5 import QtWidgets, QtCore
import mainwindow
import time
import sys

class littleTimer(QtCore.QThread):
	remain_sec = QtCore.pyqtSignal(int)
	success = QtCore.pyqtSignal(bool)
	stop = False

	def __init__(self):
		QtCore.QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		self.stop = False
		self.success.emit(False)
		self.remain_sec.emit(10)
		for index in range(1, 10 + 1):
			if self.stop:
				break
			self.remain_sec.emit(10 - index)
			time.sleep(1)
		self.success.emit(True)

class About(QtWidgets.QDialog):
	def __init__(self):
		super(About, self).__init__()
		self.setupUi()
	
	def setupUi(self):
		self.setWindowTitle("關於")
		self.setFixedSize(200, 200)
		
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
	EQ=Earthquake_Server()
	new_index = 1
	def __init__(self):
		super(Main, self).__init__()
		self.setupUi(self)

		self.about.clicked.connect(self.About_clicked)
		self.AboutWindow = About()

		self.TimeThread = littleTimer()
		self.TimeThread.remain_sec.connect(self.Time_changed)
		self.TimeThread.success.connect(self.Thread_complete)
		self.TimeThread.start()

		self.refresh.clicked.connect(self.imm_refresh)
	
	def About_clicked(self):
		self.AboutWindow.show()

	def Time_changed(self,data):
		self.progressBar.setValue(data)

	def Thread_complete(self,data):
		if data:
			self.progressBar.setFormat("更新中")
			self.EQ.update()
			self.progressBar.setFormat("剩餘%v秒")
			self.TimeThread.start()

	def imm_refresh(self):
		self.TimeThread.stop = True

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = Main()
	MainWindow.show()
	sys.exit(app.exec_())