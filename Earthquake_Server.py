import requests
import json
import os.path
from bs4 import BeautifulSoup

class Earthquake_Server:
	print_message = False

	def __init__(self, showMessage = False):
		self.print_message = showMessage
		self.EQs = {}
		self.Readjson()
	
	
	def update(self):
		try:
			res = requests.get('https://www.cwb.gov.tw/V7/modules/MOD_EC_Home.htm')
			res.encoding="utf-8"
			tbody = BeautifulSoup(res.text,"lxml").table.tbody
			for tr in tbody.findAll('tr')[::-1]:
				td = tr.findAll('td')
				if (len(td) == 9):
					code=td[0].string
					if(code == "小區域"):
						code="Area"
					Area=td[6].get_text().replace('\r','')
					self.add_new_value(code,td[1].string,td[4].string,td[5].string,Area,td[7].string)
		except Exception as e:
			if self.print_message:
				print("[ERROR] " + type(e).__name__ + " " + e.args[0])
				
	def add_new_value(self,code,time,size,depth,location,site):
		newEQ={
				"code":code,
				"time":time,
				"size":size,
				"depth":depth,
				"location":location,
				"site":site
			}
		found = False
		for key in range(1,len(self.EQs) + 1):
			if self.cmp(newEQ,self.EQs[str(key)]):
				found = True
		if not found:
			if self.print_message:
					print("[Debug]New earthquake detected")
			self.EQs[str(len(self.EQs) + 1)] = newEQ
			self.Savejson()
	
	def Savejson(self):
		if not os.path.exists('Earthquakes.json'):
			open('Earthquakes.json', 'x')
		with open('Earthquakes.json', 'w') as outfile:  
			json.dump(self.EQs, outfile)
	
	def Readjson(self):
		try:
			if os.path.exists('Earthquakes.json'):
				with open('Earthquakes.json') as json_file:
					self.EQs=json.load(json_file)
				if self.print_message:
					print("[Debug] Read " + str(len(self.EQs)) + " earthquake from file")
			else:
				open('Earthquakes.json', 'x')
		except Exception as e:
			if self.print_message:
				print("[Warn ] " + type(e).__name__ + " " + e.args[0])

	def cmp(self,a,b):
		if a["code"] != b["code"]:
			return False
		if a["time"] != b["time"]:
			return False
		if a["size"] != b["size"]:
			return False
		if a["depth"] != b["depth"]:
			return False
		if a["location"] != b["location"]:
			return False
		if a["site"] != b["site"]:
			return False
		return True
#End of Class

def EQtoString(eq):
	EQstr="\n[" + eq["code"] + "] 於" + eq["time"] + " 在 " + eq["location"] + "發生規模 " + eq["size"] + "，深度 " + eq["depth"] + "KM 的地震\n"
	return EQstr