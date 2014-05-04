import requests
import json, base64

filename = '/home/almaz/Desktop/3.jpg'

url = 'http://5.9.107.99:5000/api/v1/'
f = open(filename,'rb')
img_base64 = str(base64.b64encode(f.read()))
f.close()
headers = {'content-type': 'application/json'}
data = json.dumps({'img':img_base64})
r = requests.post(url, data, headers=headers)
if r.status_code >= 400:
    print r.status_code