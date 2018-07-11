from datetime import datetime,tzinfo,timedelta

class Zone(tzinfo):
    def __init__(self,offset,isdst,name):
        self.offset = offset
        self.isdst = isdst
        self.name = name
    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)
    def dst(self, dt):
            return timedelta(hours=1) if self.isdst else timedelta(0)
    def tzname(self,dt):
         return self.name

def filename_date():
    VN = Zone(7,False,'Vietnamese')
    return datetime.now(VN).strftime('%d-%m-%Y')

def report_datetime():
    VN = Zone(7,False,'Vietnamese')
    return datetime.now(VN).strftime('%H:%M %d-%m-%Y')

def dateto():
    VN = Zone(7,False,'Vietnamese')
    return datetime.now(VN).strftime('%m-%d-%Y').replace('-','%2F')

def datefrom():
    to = dateto()
    day = to.split('%2F')[1]
    to = to.replace(day,str(int(day)-6))
    return to
