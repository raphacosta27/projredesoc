from pprint import pprint
d = {}

import json

with open('./topics.txt', 'r') as f:
    l = ([list(map(lambda x: x.lower(), x.strip().split('\t'))) for x in f.readlines()])


for item in l:
    pprint(item)
    if len(item) == 2:
        d[item[0]] = item[1].replace(' (parent topic)','')
    
    
pprint(d)

with open('categories.json', 'w') as fp:
    json.dump(d, fp)

