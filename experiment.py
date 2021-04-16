import jellyfish
import requests

a = "inkom waz nine millen compard to the prior year of two millen. This is an exampl ov a corekshun from phonetik speling. thes mashin iz tha best mashin."
b = a.split(' ')
url = 'http://localhost:8081/v2/check'
payload = {'text' : a,
			'language': 'en-US',
			'enabledOnly':'false'}
headers = {}
res = requests.post(url,data=payload,headers=headers)
j = res.json()

uk = {}

for unk in j['matches']:
	options = []
	start = int(unk['offset'])
	length = int(unk['length'])
	key = a[start:start+length]
	for match in unk['replacements']:
		options.append(match['value'])
	uk[key] = options

for (x, candidates) in uk.items():
	min = None
	top = ''
	for candidate in candidates:
		c = jellyfish.jaro_distance(x, candidate)
		d = jellyfish.jaro_similarity(x, candidate)
		e = jellyfish.match_rating_comparison(x,candidate)
		f = jellyfish.damerau_levenshtein_distance(x,candidate)
		g = jellyfish.levenshtein_distance(x,candidate)
		h = jellyfish.jaro_winkler_similarity(x,candidate)
		k = jellyfish.hamming_distance(x,candidate)
		if min == None:
			min = e
			top = candidate
		elif e > min:
			min = e 
			top = candidate
	print(f'{candidate}, {x}')
		#print(candidate,x,c,d,e,f,g,h,k)
