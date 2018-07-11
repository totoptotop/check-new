# -*- coding: utf-8 -*-
#baocao_custom.py
from docxtpl import DocxTemplate, RichText
from locin import getWork
import timetime,time,json, datetime
import FRT_parser as fParser
import requests,lxml
from urlparse import urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning

df = dt = mf = mt = yf = yt = 1

class bcolours:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def assign_date(dateString):
	#dateString format = '2018-12-30'

	global df, dt, mf, mt, yf, yt

	future = datetime.datetime.strptime(dateString, '%Y-%m-%d').date()
	past = future + datetime.timedelta(days=-7)
	past = str(past)
	future = str(future)
	df = past.split('-')[2]
	dt = future.split('-')[2]
	mf = past.split('-')[1]
	mt = future.split('-')[1]
	yf = past.split('-')[0]
	yt = future.split('-')[0]
	return future

def query_firewall(token,cookies):
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

def query_change_url(token,cookies):
	command_url = 'https://10.1.253.90/afa/php/commands.php'
	data = {
		"cmd": 'GET_MONITORING_CHANGES',
		"TOKEN": token,
		"REQ_TIME": str(int(time.time()*1000)),
		"sDevice": 'DC_FW_CLUSTER',
		"filter_fw":'',
		"dateFrom": ('%s/%s/%s'%(mf,df,yf)).replace('/','%2F'),
		"dateTo": ('%s/%s/%s'%(mt,dt,yt)).replace('/','%2F'),
		"ChangedBy":'',
		"_search": 'false',
		"nd": str(int(time.time()*1000)),
		"row": '10',
		"page": '1',
		"sidx":'invdate',
		"sord":'asc'
	}
	cur_page = 1
	rules = {
		'add':[],
		'mod':[],
		'del':[]
	}
	defs = {
		'service': [],
		'hostgroup': []
	}
	while True:
		data['page'] = str(cur_page)
		#print data
		r = requests.post(command_url, data=data, cookies=cookies, allow_redirects = True, verify=False)
		obj_changes = json.loads(r.content)
		total_pages = int(obj_changes['total_pages'])
		changes = obj_changes['invdata']
		for change in changes:
			### parse link, rule
			change_link = fParser.link(str(change))
			change_time = fParser.time(str(change))
			change_by = change['cell'][2]
			rules = fParser.rules_(urljoin(command_url,change_link),cookies,change_time,change_by,rules)
			defs  = fParser.defs_(urljoin(command_url,change_link),cookies,defs)
		cur_page += 1
		if (cur_page > total_pages): 
			return rules, defs

def write_docx(rules,defs):
	doc = DocxTemplate("application/FW/BCFW_template.docx")
	datefrom = '%s/%s/%s'%(df,mf,yf)
	dateto = '%s/%s/%s'%(dt,mt,yt)
	context = {
		'datefrom': datefrom,
		'dateto': dateto,
		'rule_add': rules['add'],
		'rule_mod': rules['mod'],
		'rule_del': rules['del'],
		'def_ser' : defs['service'],
		'def_host': defs['hostgroup']
	}
	doc.render(context)
	docxname_ = 'application/static/Changes/BCFW '+str(dateto.replace('/','-'))+'.docx'
	doc.save(docxname_)

def main(dateStr):
	#dateStr = '2018-05-28'
	cookies, ssID, token = getWork()
	print bcolours.OKGREEN + "Logged In & Querying ..." + bcolours.ENDC
	query_firewall(token,cookies)
	#========================== GET DATE ========================
	today = datetime.date.today()
	after = assign_date(dateStr)
	print after
	print bcolours.WARNING + "Querying Change ..." + bcolours.ENDC
	rules,defs = query_change_url(token,cookies)
	print bcolours.WARNING + "Writing ..." + bcolours.ENDC
	write_docx(rules,defs)
	print bcolours.OKGREEN + "Done!" + bcolours.ENDC

if __name__ == "__main__":
	main()