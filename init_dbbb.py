#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from application.models import *

def load_excel():
    import os 
    import pandas
    import re
    import math
    ipsTable = IpTable()
    reaesc = re.compile(r'\x1b[^m]*m')
    xls = pandas.ExcelFile('IP Table-1.xlsx')
    import numpy as np
    for sh in xls.sheet_names:
        df = xls.parse(sh)
        df = df.drop('Unnamed: 7',1)
        df = df.drop('Note',1)
        df = df.replace(np.nan, '', regex=True)
        vlan = ''
        print list(df)
        for i in range(0,len(df.index)):
            ipAdress = ''
            oper = ''
            own = ''
            hostname = ''
            editor = ''
            status = 'active'
            service = ''

            if (df.at[i,'IP Server'] == ''):
                vlan = df.at[i,'Device']
                continue
            ipAdress = df.at[i,'IP Server']
            oper = df.at[i, 'OS']
            hostname = df.at[i,'Hostname']
            own = df.at[i,'Owner']
            service = df.at[i,'Service']
            print (ipAdress, hostname, own, oper, service, editor, status, vlan)
            print IpTable().add_data(ipAdress, hostname, own, oper, service, editor, status, vlan)



if __name__ == '__main__':
	load_excel()