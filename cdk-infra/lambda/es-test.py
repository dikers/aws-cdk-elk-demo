import urllib.request
import json


ES_URL = 'https://search-es-demo-rrmy6y3s7fx3svo3m532poauoy.cn-northwest-1.es.amazonaws.com.cn/subway/_count'


formData = {
    "query": {
        "bool": {
            "must": [
                {"match": {"error_code": 1111}},
                {"range": {"create_time": {"gt": "now-10h", "lte": "now"}}}
            ]
        }
    }
}

formData = json.dumps(formData).encode()
print(type(formData))
print(formData)

headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}

req = urllib.request.Request(url=ES_URL,
                             data=formData, headers=headers)

response = urllib.request.urlopen(req)
tmp_str = response.read().decode('utf-8')
results = json.loads(tmp_str)

error_count = int(results['count'])
print("最近5分钟错误次数: {}".format(error_count))