import requests
import json, base64

filename = 'test.jpg'

url = 'http://5.9.107.99:5000/api/v1/'
f = open(filename,'rb')
img_base64 = str(base64.b64encode(f.read()))
print img_base64
f.close()
headers = {'content-type': 'application/json'}

data = json.dumps({'img':img_base64}) 
r = requests.post(url, data, headers=headers)
print r.text # check if everuthing is fine

url += 'proc/' + r.json()['p_name']
r = requests.get(url)
img_base64 = r.json()['img']
pts = r.json()['pts']
print pts
f = open("'proc" + filename, "wb")
f.write(base64.b64decode(img_base64))
f.close()
