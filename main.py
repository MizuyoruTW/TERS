from Earthquake_Server import Earthquake_Server, EQtoString
from Earthquake_Server_v8 import Earthquake_Server_v8
from PyQt5 import QtWidgets, QtCore, QtGui
import mainwindow
import logging
import setting
import time
import sys
import webbrowser
import configparser
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s : %(message)s', filename="TERS.log")
thisVersion = "2.1"
path = ""

# A timer for interval
class littleTimer(QtCore.QThread):
	remain_sec = QtCore.pyqtSignal(int)
	success = QtCore.pyqtSignal(bool)
	stop = False # For manual refresh

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

# The setting window
class SettingWindow(QtWidgets.QDialog, setting.Ui_Dialog):
	config = configparser.ConfigParser()
	origin_version = ""
	changed = False
	def __init__(self):
		super(SettingWindow, self).__init__()
		self.config.optionxform = str
		self.config.read(path + "/TERS.config")

		self.setupUi(self)

		self.setWindowTitle("設定")

		self.comboBox.addItems(["v7", "v8"])

		self.origin_version = self.config.get("TERS", "Module_Version")

		self.comboBox.setCurrentText(self.origin_version)

		self.buttonBox.clicked.connect(self.OK_selected)


	def OK_selected(self):
		self.config.set("TERS", "Module_Version", str(self.comboBox.currentText()))
		self.config.write(open(path + "/TERS.config","w"))
		if self.origin_version != str(self.comboBox.currentText()): # Module version changed
			logging.info("Module version changed from " + self.origin_version + " to " + str(self.comboBox.currentText()))
			QtWidgets.QMessageBox.information(self, "警告", "模組版本已更新，資料將清除，並重新起動", QtWidgets.QMessageBox.Ok)
			os.remove(path + "/Earthquakes.json") # Remove the previous file because different module version makes website different
			os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) # Restart to apply settings


# The main window
class Main(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
	new_index = 1 # the number of old earthquake
	module_version = ""

	def __init__(self):
		super(Main, self).__init__()
		self.setupUi(self)

		self.readConfig()

		self.about.clicked.connect(self.About_clicked)

		self.setting.clicked.connect(self.setting_clicked)

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
		# About window
		msgBox = QtWidgets.QMessageBox()
		msgBox.setWindowTitle("關於")
		msgBox.setText("版本 V" + thisversion + "\n本程式由水夜工作坊製作\n資訊由中央氣象局提供\n使用中央氣象局地震模組 V7, V8\n\n使用 GPLv3 標準授權")
		msg_layout = msgBox.layout()

		SiteLink = QtWidgets.QLabel()
		SiteLink.setText("<a href='https://github.com/MizuyoruTW'>https://github.com/MizuyoruTW</a>")
		SiteLink.setOpenExternalLinks(True)

		msg_layout.addWidget(SiteLink, 1, 0, 1, msg_layout.columnCount())
		msgBox.show()
		msgBox.exec()

	def Time_changed(self,data):
		self.progressBar.setValue(data)# Showing the interval

	def Thread_complete(self,data):
		if data:
			self.progressBar.setFormat("更新中")
			self.EQ.update()
			self.display_result()
			self.update_Table()
			self.progressBar.setFormat("剩餘%v秒")
			self.TimeThread.start()

	# Manual refresh
	def imm_refresh(self):
		self.TimeThread.stop = True

	def display_result(self):
		EQsize = len(self.EQ.EQs) + 1
		if self.new_index != EQsize: # New earthquake
			EQdetails = ""
			# New earthquake window
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

	# Update the list of earthquakes
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
			logging.error(type(e).__name__ + " " + str(e))

	# Double click on list to open the website
	def TableDoubleClicked(self, mi):
		webbrowser.open(self.EQ.getEQwebsite(self.EQ.EQs[str(mi.row() + 1)]))
    
	# Read configurations
	def readConfig(self):
		try:
			config = configparser.ConfigParser()
			config.read(path + "/TERS.config")
			self.module_version = config.get("TERS", "Module_Version")
			if(self.module_version == "v7"):
				logging.info("Using module version v7")
				self.EQ = Earthquake_Server(path)
			else:
				logging.info("Using module version v8")
				self.EQ = Earthquake_Server_v8(path)
		except Exception as e: # if having any errors, overwrite to default setting
			logging.error(type(e).__name__ + " " + str(e))
			self.EQ = Earthquake_Server_v8(path)
			config = configparser.ConfigParser()
			config.optionxform = str
			config.read(path + "/TERS.config")
			config.add_section("TERS")
			config.set("TERS", "Module_Version", "v8")
			with open(path + "/TERS.config","w") as f:
				config.write(f)

	def setting_clicked(self):
		settings = SettingWindow()
		settings.show()
		settings.exec()
			

if __name__ == "__main__":
	logging.info("Program start--------------------------------------------------")
	path = os.getcwd()
	logging.info("Path set to " + path)
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = Main()
	MainWindow.show()
	sys.exit(app.exec_())