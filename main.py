from Earthquake_Server import Earthquake_Server, EQtoString, getEQwebsite
from PyQt5 import QtWidgets, QtCore, QtGui
import mainwindow
import time
import sys
import webbrowser

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

class Main(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
	EQ=Earthquake_Server(True)
	new_index = 1
	def __init__(self):
		super(Main, self).__init__()
		self.setupUi(self)

		self.about.clicked.connect(self.About_clicked)

		self.TimeThread = littleTimer()
		self.TimeThread.remain_sec.connect(self.Time_changed)
		self.TimeThread.success.connect(self.Thread_complete)

		self.refresh.clicked.connect(self.imm_refresh)
		self.new_index = len(self.EQ.EQs) + 1

		self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		self.tableView.horizontalHeader().setStretchLastSection(True)
		self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.tableView.doubleClicked.connect(self.TableDoubleClicked)

		self.Thread_complete(True)


	def About_clicked(self):
		msgBox = QtWidgets.QMessageBox()
		msgBox.setWindowTitle("關於")
		msgBox.setText("版本 V1.1\n本程式由水夜工作坊製作\n資訊由中央氣象局提供\n使用中央氣象局地震模組 V7\n\n使用 GPLv3 標準授權")
		msg_layout = msgBox.layout()

		SiteLink = QtWidgets.QLabel()
		SiteLink.setText("<a href='https://github.com/MizuyoruTW'>https://github.com/MizuyoruTW</a>")
		SiteLink.setOpenExternalLinks(True)

		msg_layout.addWidget(SiteLink, 1, 0, 1, msg_layout.columnCount())
		msgBox.show()
		msgBox.exec()

	def Time_changed(self,data):
		self.progressBar.setValue(data)

	def Thread_complete(self,data):
		if data:
			self.progressBar.setFormat("更新中")
			self.EQ.update()
			self.display_result()
			self.update_Table()
			self.progressBar.setFormat("剩餘%v秒")
			self.TimeThread.start()

	def imm_refresh(self):
		self.TimeThread.stop = True

	def display_result(self):
		EQsize = len(self.EQ.EQs) + 1
		if self.new_index != EQsize:
			EQdetails = ""
			msgBox = QtWidgets.QMessageBox()
			for index in range(self.new_index,EQsize):
				EQdetails += EQtoString(self.EQ.EQs[str(index)]) + '\n'
			msgBox.setWindowTitle("新地震訊息")
			msgBox.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
			msgBox.setIcon(QtWidgets.QMessageBox.Warning)
			msgBox.setText("從中央氣象局接收" + str(EQsize - self.new_index) + "條新地震訊息")
			msgBox.setDetailedText(EQdetails)
			self.new_index = EQsize
			msgBox.show()
			msgBox.exec()

	def update_Table(self):
		try:
			self.model=QtGui.QStandardItemModel(len(self.EQ.EQs), 6)
			self.model.setHorizontalHeaderLabels(["編號","時間","規模","深度","位置","網頁"])
			for row in range(len(self.EQ.EQs)):
				self.model.setItem(row, 0, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["code"]))
				self.model.setItem(row, 1, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["time"]))
				self.model.setItem(row, 2, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["size"]))
				self.model.setItem(row, 3, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["depth"]))
				self.model.setItem(row, 4, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["location"]))
				self.model.setItem(row, 5, QtGui.QStandardItem(self.EQ.EQs[str(row + 1)]["site"]))
			self.tableView.setModel(self.model)
		except Exception as e:
			print("[ERROR] " + type(e).__name__ + " " + str(e))

	def TableDoubleClicked(self, mi):
		webbrowser.open(getEQwebsite(self.EQ.EQs[str(mi.row() + 1)]))
    




if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = Main()
	MainWindow.show()
	sys.exit(app.exec_())