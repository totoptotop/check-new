from multiprocessing import Process
from threading import Thread


name = 'hello'

def aName(newName):
    global name
    name = newName

print name
aName('Toanpho')
print name

a = Process(target=aName, args=('ToanPVN',))
a.start()

print name

t = Thread(target=aName, args=('ToanPVN',))
t.start()
print name