from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime, timedelta
import requests
import subprocess
import glob
import os

year = ""
month = ""
day = ""
spectrum = ""

target_wavelengths = ["94", "171", "193", "211", "304", "335"]

url = "http://jsoc.stanford.edu/data/aia/images/2018/04/10/335/"
ext = 'jp2'

alist = []
lena = [0, 0, 0, 0, 0, 0]
lenb = [0, 0, 0, 0, 0, 0]



def buildURL():
	time = datetime.now()
	time = str(time).split(" ")[0].split("-")
	year = time[0]
	month = time[1]
	day = time[2]
	urlout = "http://jsoc.stanford.edu/data/aia/images/" + str(year) + "/" + str(month) + "/" + str(day) + "/" 
	return(urlout)

def listFD(url, ext=''):
    page = requests.get(url).text
    # print page
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]


while True:

	time = datetime.now()
	time = str(time).split(" ")[0].split("-")
	year = time[0]
	month = time[1]
	day = time[2]
	urlout = "http://jsoc.stanford.edu/data/aia/images/" + str(year) + "/" + str(month) + "/" + str(day) + "/" 

	for wlen in target_wavelengths:
		for file in glob.glob(str(wlen) + "/*.jp2"):
			file_mod_time = datetime.fromtimestamp(os.stat(file).st_mtime)
			if(str(datetime.now() - file_mod_time).find("1 day") != -1): #if a file is more than 24 hours old
				print("PRUNING: " + str(file))
				os.remove(file)

	for wlen in target_wavelengths:

		url = urlout + str(wlen) + "/"
		windex = target_wavelengths.index(wlen)
		print("CHECKING: " + str(url))
		lena[windex] = lenb[windex]
		alist = []
		for file in listFD(url, ext):
		    alist.append(str(file))

		print("LENGTH: " + str(len(alist)))
		lenb[windex] = len(alist)

		if((lenb[windex] - lena[windex]) < 0):
			lena[windex] = 0

		new = lenb[windex] - lena[windex] #Without the above if statement, When the day changes over, this becomes negative!!
		print("NEW: " + str(new))
		if(new > 0):
			for file in range((lenb[windex] - new), lenb[windex]):
				subprocess.call("wget -P " + str(wlen) + " " + str(alist[file]), shell = True)

	#check every 15 minutes

	sleep(900)


