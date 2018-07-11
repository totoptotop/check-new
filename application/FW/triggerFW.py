from FW_Changes_Arg import main as changeMain
from FRT_Arg import main as frtMain
import datetime

def getMondayDate():
	day = datetime.datetime.today()
	while (day.weekday() != 0):
		day = day + datetime.timedelta(days=-1)
	nearestMonday = day
	return nearestMonday.strftime('%Y-%m-%d')

def generate_docx_html():
	mondayDate = getMondayDate()
	frtMain()
	changeMain(mondayDate)

if __name__ == '__main__':
	#print getMondayDate()
	generate_docx_html()