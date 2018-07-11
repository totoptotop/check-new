#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

#read email config
SERVER =    'mail.ncb-bank.vn'
PORT =      587
SENDER =    str(('NCB Sec Team <toanpvn@ncb-bank.vn>'))
USERNAME = 'toanpvn'
PASSWORD =  'cGFzc0BuY2IxMjM='.decode('base64')
list_receiver = [
		{
			'name':'Trung Anh Hói',
			'mail':'anhpt@ncb-bank.vn'
		},
		{
			'name':'Phong Siêu Nhơn',
			'mail':'phongnx@ncb-bank.vn'
		}
]
def send_email_text(content):
	session = smtplib.SMTP(SERVER, PORT)
	session.set_debuglevel(0)
	session.ehlo()
	session.starttls()
	session.ehlo
	session.login(USERNAME, PASSWORD)
	for receiver in list_receiver:
		msg = MIMEText(content.replace('people.name',receiver['name']), 'html', 'utf-8')
		msg['Subject'] = '[NCB-Scan IP Table] Found some new IP'
		msg['From'] = SENDER
		msg['To'] = receiver['mail']
		session.sendmail(SENDER, receiver['mail'], msg.as_string())
		print 'done', receiver['name'] , str(datetime.now())
	session.quit()

def send_mail(list_IP):
	row_html = """      <tr>
                            <td>iter</td>
                            <td>table.ip</td>
                          </tr>"""
	main_html = open('email_template.html').read()
	stt = 0
	manyrow_html = ""
	for ip in list_IP:
		stt += 1
		new_row = row_html.replace('iter',str(stt))
		new_row = new_row.replace('table.ip',ip)
		manyrow_html += new_row + '\n'
	content = main_html.replace('table.tr',manyrow_html)
	send_email_text(content)

def check_new_IP():
	from application.models import *
	ipsTable = IpTable()
	oldQuery = ipsTable.get_by_status('active')
	oldIP = []
	for rec in oldQuery:
		oldIP.append(rec[0].strip())
	scanresult = open('everyday_shuffle.txt').read()
	import re
	m = re.compile(r"(\d+\.\d+\.\d+\.\d+)")
	newIP = m.findall(scanresult)
	unindentifyIP = []
	for ip in newIP:
		if ip not in oldIP:
			unindentifyIP.append(ip)
	return unindentifyIP

print check_new_IP()

# send_mail(check_new_IP())