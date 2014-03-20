import requests
import json, base64


url = 'http://localhost:5000/api/v1/'
f = open('test.jpg','rb')
img_base64 = str(base64.b64encode(f.read()))
f.close()
headers = {'content-type': 'application/json'}

data = json.dumps({'img':img_base64}) 
r = requests.post(url, data, headers=headers)
print r.text

url = 'http://localhost:5000/api/v1/source/' + r.json()['s_name']
r1 = requests.get(url)
print r1.text

url = 'http://localhost:5000/api/v1/proc/' + r.json()['p_name']
r = requests.get(url)
print r.text
