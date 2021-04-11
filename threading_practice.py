from threading import Thread

from gingerit.gingerit import GingerIt

import time

returns = {}

def parse(inp, parser, thread_n):
	returns[thread_n] =  parser.parse(inp)['result']

parser = GingerIt()

f = open('constitution.txt','r')
text = f.read()
f.close()

text = text.split(' ')
text = [' '.join(text[i:i+10]) for i in range(0, len(text), 10)]

start = time.time()

threads = []

for i in range(0, len(text)):
	threads.append(Thread(target=parse, args=(text[i]+'.',parser, i)))

for thread in threads:
	thread.start()

for thread in threads:
	thread.join()

end = time.time()

out = ""
for i in range (0,len(text)):
	out += returns[i]

f = open('other.txt','w')
f.write(out)
f.close()

print(end-start)
