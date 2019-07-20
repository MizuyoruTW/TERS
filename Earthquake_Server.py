import logging
import requests
import json
import os.path
from bs4 import BeautifulSoup


class Earthquake_Server:
	path = "" # The path of Earthquakes.json

	def __init__(self, path = ""):
		self.EQs = {}
		self.path = path
		self.Readjson()
	
	# Get data from website
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
					Area=td[6].get_text().replace('/r','')
					self.add_new_value(code,td[1].string,td[4].string,td[5].string,Area,td[7].string)
		except Exception as e:
			logging.error(type(e).__name__ + " " + str(e))
				
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
			if self.cmp(newEQ,self.EQs[str(key)]): # Checking if there exists the same earthquake
				found = True
				break
		if not found:
			logging.info("New earthquake detected")
			self.EQs[str(len(self.EQs) + 1)] = newEQ
			self.Savejson()
	
	def Savejson(self):
		if not os.path.exists(self.path + "/Earthquakes.json"): # Checking if there does not exist the json file
			open(self.path + "/Earthquakes.json", 'x')
		with open(self.path + "/Earthquakes.json", 'w') as outfile:  
			json.dump(self.EQs, outfile)
	
	def Readjson(self):
		try:
			if os.path.exists(self.path + "/Earthquakes.json"): # Checking if there does not exist the json file
				with open(self.path + "/Earthquakes.json") as json_file:
					self.EQs=json.load(json_file)
					logging.info("Read " + str(len(self.EQs)) + " earthquakes from file")
			else:
				open(self.path + "/Earthquakes.json", 'x')
		except Exception as e:
			logging.warning(type(e).__name__ + " " + e.args[0])

	# Comparing earthquake informations
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

	# Get real earthquake information website
	def getEQwebsite(self, eq):
		if eq["code"] == "Area":
			return "https://www.cwb.gov.tw/V7/earthquake/Data/local/" + eq["site"]
		else:
			return "https://www.cwb.gov.tw/V7/earthquake/Data/quake/" + eq["site"]
#End of Class

def EQtoString(eq):
	EQstr="\n[" + eq["code"] + "] 於" + eq["time"] + " 在 " + eq["location"] + "發生規模 " + eq["size"] + "，深度 " + eq["depth"] + "KM 的地震\n"
	return EQstr
