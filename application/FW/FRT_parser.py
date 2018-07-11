import requests,lxml
from bs4 import BeautifulSoup
from docxtpl import RichText

def link(txt):
	pos = txt.find('../session')
	for i in range(pos,100000):
		if (txt[i] == '"'):
			return txt[pos:i]

def time(txt):
	ioc = '</span>'
	pos = txt.find(ioc)
	for i in range(pos,100000):
		if (txt[i] == "'"):
			return txt[pos+len(ioc):i]

newLine = '<w:br/>'

def replace_right(source, target, replacement, replacements=None):
    return replacement.join(source.rsplit(target, replacements))

def r_strip_once(source):
	return replace_right(source, newLine, '', 1)

def pretty_rule(rule):
	rule['source'].xml = r_strip_once(rule['source'].xml)
	rule['dest'].xml = r_strip_once(rule['dest'].xml)
	rule['ser'].xml = r_strip_once(rule['ser'].xml)
	rule['act'].xml = r_strip_once(rule['act'].xml)
	rule['enable'].xml = r_strip_once(rule['enable'].xml)
	rule['exp'].xml = r_strip_once(rule['exp'].xml)
	return rule

def row_0(obj):
	rule = {}
	cells = obj.find_all('td')
	rule['no'] = cells[1].get_text()

	rule['name'] = RichText('')
	if (cells[4].font != None):
		rule['name'].add(cells[4].get_text(), style='Style1')
	else:
		rule['name'].add(cells[4].get_text())

	if 'Any' in cells[5].get_text():
		rule['source'] = RichText('Any')
	else:
		rule['source'] = RichText('')
		for el in cells[5].find_all('font', {'color': "#111111"}):
			if (el.font != None):
				rule['source'].add(el.get_text(), style='Style1')
			else:
				rule['source'].add(el.get_text())
			rule['source'].add('\n')


	if 'Any' in cells[6].get_text():
		rule['dest'] = RichText('Any')
	else:
		rule['dest'] = RichText()
		if cells[6].font:
			for el in cells[6].find_all('font', {'color': "#111111"}):
				if (el.font != None):
					rule['dest'].add(el.get_text(), style='Style1')
				else:
					rule['dest'].add(el.get_text())
				rule['dest'].add('\n')
		else:
			rule['dest'].add(cells[6].get_text())
			rule['dest'].add('\n')



	if 'Any' in cells[7].get_text():
		rule['ser'] = RichText('Any')
	else:
		rule['ser'] = RichText('')
		for el in cells[7].find_all('font', recursive=False):
			if (el.font != None):
				rule['ser'].add(el.get_text(), style='Style1')
			else:
				rule['ser'].add(el.get_text())
			rule['ser'].add('\n')


	rule['act'] = RichText('')
	if (cells[8].font != None):
		rule['act'].add(cells[8].get_text().strip(), style='Style1')
	else:
		rule['act'].add(cells[8].get_text().strip())
	rule['act'].add('\n')


	rule['enable'] = RichText('')
	if (cells[11].font != None):
		rule['enable'].add(cells[11].get_text(), style='Style1')
	else:
		rule['enable'].add(cells[11].get_text())
	rule['enable'].add('\n')


	rule['exp'] = RichText('')
	if (cells[13].font != None):
		rule['exp'].add(cells[13].get_text(), style='Style1')
	else:
		rule['exp'].add(cells[13].get_text())
	rule['exp'].add('\n')
	
	m = 0
	if ('insert' in str(cells[0].img['src'])):
		tt = 0
		rule['no'] = RichText(rule['no'])
	elif ('delete' in str(cells[0].img['src'])):
		tt = 1
		rule['no'] = RichText(rule['no'])
	else: 
		tt = 2
		m = 1

	return rule, tt, m

def row_1(rule, obj):
	cells = obj.find_all('td')
	no = cells[0].get_text()
	if (rule['no'] != no):
		rule['no'] = RichText(rule['no'])
		rule['no'].add('\n')
		rule['no'].add(no, style='Style2')
	else:
		rule['no'] = RichText(rule['no'])

	for el in cells[3].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['name'].add(el.get_text(), style='Style2')
		rule['name'].add('\n')

	for el in cells[4].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['source'].add(el.get_text(), style='Style2')
		rule['source'].add('\n')

	for el in cells[5].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['dest'].add(el.get_text(), style='Style2')
		rule['dest'].add('\n')

	for el in cells[6].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['ser'].add(el.get_text(), style='Style2')
		rule['ser'].add('\n')

	for el in cells[7].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['act'].add(el.get_text(), style='Style2')
		rule['act'].add('\n')

	for el in cells[10].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['enable'].add(el.get_text(), style='Style2')
		rule['enable'].add('\n')

	for el in cells[12].find_all('font', {'style': "BACKGROUND-COLOR: pink"}):
		rule['exp'].add(el.get_text(), style='Style2')
		rule['exp'].add('\n')

	return rule

def rules_(link,cookies,time,by,rules):
	r = requests.post(link, cookies=cookies, allow_redirects = True, verify=False)
	soup = BeautifulSoup(r.text, 'lxml')
	rule_table = soup.find_all('table', {"width" : "99%"})
	if len(rule_table) == 0: return rules
	rule_table = rule_table[0]
	row_list = rule_table.find_all('tr')
	del row_list[0]
	mod = 0
	rType = 0
	for row in row_list:
		if (mod == 0):
			rule, rType, mod = row_0(row)
			rule['time'] = time
			rule['by'] = by
			if (rType == 0):
				rule = pretty_rule(rule)
				rules['add'].append(rule)
			elif (rType == 1):
				rule = pretty_rule(rule)
				rules['del'].append(rule)
		else:
			rule = row_1(rule, row)
			rule['time'] = time
			rule['by'] = by
			rule = pretty_rule(rule)
			rules['mod'].append(rule)
			mod = 0
	return rules

def defs_(link,cookies,defs):
	r = requests.post(link, cookies=cookies, allow_redirects = True, verify=False)
	soup = BeautifulSoup(r.text, 'lxml')
	def_tables = soup.find_all('table', {"width" : "50%"})
	for tbl in def_tables:
		row_list = tbl.find_all('tr', {'bgcolor': "white"},recursive=False)
		dect = row_list[0]
		del row_list[0]
		if ('ADDRESSES' in dect.find_all('th')[1].get_text()): #Hostgroup definitions
			hg = {
			}
			for row in row_list:
				cells = row.find_all('td')
				hg['name'] = cells[2].get_text()
				hg['ip'] = cells[3].get_text()
				hg['time'] = cells[4].get_text()
				hg['by'] = cells[5].get_text()
				defs['hostgroup'].append(hg)
			return defs
		elif ('PROTOCOL' in dect.find_all('th')[1].get_text()):
			sv = {
				'name': 'a'
			}
			for row in row_list:
				cells = row.find_all('td',recursive=False)
				# for i in cells:
				# 	print '---', i , '\n', i.get_text()
				sv['name'] = cells[0].get_text().strip()
				sv['pro'] = cells[1].get_text()
				sv['dest'] = cells[2].get_text()
				sv['source'] = cells[3].get_text()
				sv['time'] = cells[4].get_text()
				sv['by'] = cells[5].get_text()
				defs['service'].append(sv)
	return defs

