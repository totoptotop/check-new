import requests,sys,re
from bs4 import BeautifulSoup
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# Login & make cookie acceptable
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getWork():
	r = requests.get("https://10.1.253.90/AFA/php/Login.php", allow_redirects = False, verify=False)
	# Extract session information
	sessionID = re.match("PHPSESSID=(.*?);", r.headers["set-cookie"])
	sessionID = sessionID.group(1)
	data = {
		"user_name": '',
		"password": '',
		"screenWidth": "",
		"screenHeight":"",
		"pixelDepth":"",
		"colorDepth":"",
		"ScreenDPI":"",
		"last_url":"",
		"forceLocalAuth":"0"
	}
	#uName = str(raw_input('Input username: '))
	#pWord = str(getpass.getpass('Input password: '))
	uName = 'Toanpvn'
	pWord = '7061737340616c67313233'.decode('hex')
	data['user_name'] = uName
	data['password'] = pWord
	cookies = {
		"PHPSESSID": sessionID
	}
	r = requests.post("https://10.1.253.90/AFA/php/Login.php", data=data, cookies=cookies, allow_redirects = True, verify=False)
	r = requests.get("https://10.1.253.90/afa/php/home.php", cookies=cookies, allow_redirects = True, verify=False)
	pos = r.text.find('g_sessID')
	for i in range(pos, pos + 500):
		if r.text[i]=="'":
			ssID = r.text[i+1:i+33]
			break
	pos = r.text.find('g_sSessionToken')
	for i in range(pos, pos + 500):
		if r.text[i]=="'":
			token = r.text[i+1:i+33]
			break
	return cookies,ssID,token

#print getWork()