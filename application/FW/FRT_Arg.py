import requests,lxml
from bs4 import BeautifulSoup
from urlparse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime, json
from locin import getWork
import timetime
import time
import sys,os
sys.stdout.flush()
reload(sys)
sys.setdefaultencoding('utf8')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#----------------------define_variables_urls----------
dictionary = {}
totalPages = 0
rulesPage = ''

class bcolours:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def getHeaders():

	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0'
	}

	headersFileName = 'headers_FRT.txt'
	headersString = open(headersFileName).readlines()
	for line in headersString:
		zxc = line.split(':')
		headers[zxc[0]]=zxc[1].strip('\n').strip(' ')
	return headers

def get_IP(href, grep, cookies):
	try:
		return dictionary[grep]
	except:
		ipURL = urljoin(rulesPage,href)
		content = requests.get(ipURL,cookies=cookies,allow_redirects = False, verify=False)
		strin = content.text
		#parse to ip
		pos = strin.find('\"' + grep + '\"')
		for i in range(pos+len(grep),pos+400):
			if ('|! ' in strin[i:i+3]): 
				#if (grep == 'Mgmt_VCenter'): print strin[i:i+3]
				for j in range(i,i-400,-1):
					if strin[j] == "\"":
						try:
							dictionary[strin[j+1:i]]
							temp = dictionary[grep] = '<span>'+strin[j+1:i]+'</span>'
							dictionary[temp] = grep
						except:
							temp = dictionary[grep] = strin[j+1:i]
							dictionary[temp] = grep
						return strin[j+1:i]
						break
				break

def get_port(href, grep, cookies):
	try:
		return dictionary[grep]
	except:
		ipURL = urljoin(rulesPage,href)
		content = requests.get(ipURL,cookies=cookies,allow_redirects = False, verify=False)
		#print ipURL
		strin = content.text
		#parse to port
		pos = strin.find('\"' + grep + '\"')
		i = strin.find(',","*',pos)
		#print strin
		#sys.exit()
		for j in range(i,i-50,-1):
			if strin[j] == '"':
				try:
					dictionary[strin[j+1:i]]
					temp = dictionary[grep] = '<span>'+strin[j+1:i]+'</span>'
					dictionary[temp] = grep
				except:
					temp = dictionary[grep] = strin[j+1:i]
					dictionary[temp] = grep
				#print grep, strin[j+1:i]
				return strin[j+1:i]

def getRules(pageURL, cookies):
	#print pageURL
	eachHTML = ""
	content = requests.get(pageURL,cookies=cookies, verify=False)
	### Get timetable
	contentHTML = content.text
	posTime = contentHTML.find('<br><h3>Time objects</h3>')
	posAfter = contentHTML.find('<br><h3>Advanced security options</h3>')
	timeHTML = contentHTML[posTime:posAfter].replace('bgcolor="#2969A6" ','',1)
	soup = BeautifulSoup(content.text, 'lxml')
	for elem in soup.find_all("tr", id=True):
		td = ['']*10
		#### Get all td
		tds = elem.find_all("td")
		#### Get Rule ID
		#tds[2].get_text()
		td[0] = tds[1].get_text()
		td[1] = tds[2].get_text()
		tmp = str(td[0]).translate(None,'Disabled Inactive (time)\n')
		print '%4s'%(tmp),
		#print td[0], 's : %i, d : %i, se : %i' %(len(tds[4].find_all("a")),len(tds[5].find_all("a")), len(tds[7].find_all("a")))
		#### Get Source
		if "Any" in tds[3].get_text():
			td[2] = "Any"
		else:
			for aa in tds[3].find_all("a"):
				td[2] += aa.get_text() + '\n'
				td[2] += '(%s) <br> \n' %get_IP(aa['href'],aa.get_text(), cookies)
		#print td[2]
		#print '==============================='
		#### Get Destination
		if "Any" in tds[4].get_text():
			td[3] =  "Any"
		else:
			for aa in tds[4].find_all("a"):
				td[3] += aa.get_text() + '\n'
				td[3] += '(%s) <br> \n' %get_IP(aa['href'],aa.get_text(), cookies)
		#print td[3]
		#print '==============================='
		#### get port
		if "Any" in tds[6].get_text():
			td[4] = "Any"
		else:
			for aa in tds[6].find_all("a"):
				td[4] += aa.get_text() + '\n'
				td[4] += '(%s) <br> \n' %get_port(aa['href'],aa.get_text(), cookies)
		#print td[4]
		#### get action
		td[5] = tds[7].get_text().strip()
		#print td[5]
		#### get time
		td[6] = tds[9].get_text().strip()
		eachHTML += """		<tr>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		</tr>\n"""% (td[0],td[1],td[2],td[3],td[4],td[5],td[6])
		#print ',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'

	print
	return eachHTML,timeHTML

def buildHTML(rules_html, time_html, timeCreated):
	html_code = """<!DOCTYPE html>
	<html>
	<head>
		<link href='https://fonts.googleapis.com/css?family=Squada+One' rel='stylesheet' type='text/css'>
		<link href='https://rawgit.com/IAt0ny/python/master/frs.css' rel='stylesheet' type='text/css'>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
	</head>
	<body>
		<link href='https://fonts.googleapis.com/css?family=Libre+Baskerville:400,400italic,700' rel='stylesheet' type='text/css'>
		<h1>Firewall Rule Table v1.0</h1>
		<p><em>
			Source : Firewall Checkpoint <br> 
			Created by : <a href='mailto:toanpvn@ncb-bank.vn'>ToanPVN@ncb-bank.vn</a> <br> 
			Created date : %s</em>
		</p>
		<table>
			<tr>
			<th width=5%%>Rule ID</th>
			<th width=5%%>Name</th>
			<th width=30%%>Source</th>
			<th width=30%%>Destination</th>
			<th width=20%%>Service(Port)</th>
			<th width=5%%>Action</th>
			<th width=5%%>Time</th>
			</tr>\n
			%s
		</table>
		<br>
		<br>
		%s
	</body>
	</html>"""%(timeCreated, rules_html, time_html)
	filename_ = 'application/static/FRT/FRT %s.html'%timeCreated.split(' ')[0]
	f = open(filename_,'w')
	f.write(html_code)
	f.close()
	print bcolours.OKGREEN + "Successfull !!!" + bcolours.ENDC

def queryPolicy(token,cookies):
	command_url = 'https://10.1.253.90/afa/php/commands.php'
	data = {
		"cmd": 'GET_REPORTS',
		"ActionType": 'GET_REPORTS',
		"TOKEN": token,
		"REQ_TIME": str(int(time.time()*1000)),
		"sDevice": 'DC-FW-CLUSTER',
		"sDeviceName": "DC_FW_CLUSTER",
		"dev_type": 'firewall',
		"rep_type": 'firewall',
		"show_all_fws": '',
		"selectedReps": '',
		"_search": 'false',
		"nd": str(int(time.time()*1000)),
		"row": '10',
		"page": '1',
		"sidx":'date',
		"sord":'desc'
	}
	r = requests.post(command_url, data=data, cookies=cookies, allow_redirects = True, verify=False)
	content = r.content
	pos = content.find("javascript:window.open('")
	for i in range(pos, pos+100):
		if content[i]=='.':
			for j in range(i,i+1000):
				if content[j]==')':
					return urljoin(command_url, content[i+7:j-1].replace("\\",''))
					break
			break

def getTimeCreated(pageURL, cookies):
	pageURL = pageURL.replace('orig_rules','menubar')
	content = requests.get(pageURL,cookies=cookies, verify=False)
	contentHTML = content.text
	pos = contentHTML.find('<span>Analyzed on:')
	aft = contentHTML.find('</span>',pos)
	return contentHTML[pos+19:aft]

######### Init To Process #########
def main():
	global rulesPage
	print bcolours.WARNING + "Logging In FRT" + bcolours.ENDC
	cookies, ssID, token = getWork()
	print bcolours.OKGREEN + "Logged In ..." + bcolours.ENDC
	#headers = getHeaders()
	#pageURL = pageURL%(ssID,ssID)
	lastPage = queryPolicy(token,cookies).replace('index','orig_rules')
	rulesPage = lastPage
	print bcolours.OKGREEN + " & Querying " + lastPage + "..." + bcolours.ENDC
	timeCreated = getTimeCreated(lastPage, cookies)
	rules_html, time_html = getRules(lastPage, cookies)
	print bcolours.OKGREEN + "Building FRT.HTML !" + bcolours.ENDC
	buildHTML(rules_html,time_html, timeCreated)
	print bcolours.OKGREEN + "Done FRT !" + bcolours.ENDC
