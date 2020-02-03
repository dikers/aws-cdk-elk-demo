import urllib.request
import json
import os
import boto3

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def handler(event, context):
    # ES_URL = 'https://search-es-demo-rrmy6y3s7fx3svo3m532poauoy.cn-northwest-1.es.amazonaws.com.cn/subway/_count'

    print('arn : {}  '.format(SNS_TOPIC_ARN))

    ES_URL = 'https://vpc-subwayes-adtjf5sflea4zjq5utwap6t27i.cn-northwest-1.es.amazonaws.com.cn/subway/_count'
    formData = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"error_code": 9999}},
                    {"range": {"create_time": {"gt": "now-10h", "lte": "now"}}}
                ]
            }
        }
    }

    formData = json.dumps(formData).encode()
    print('查询条件： {} '.format(formData))

    headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}

    req = urllib.request.Request(url=ES_URL,
                                 data=formData, headers=headers)

    response = urllib.request.urlopen(req)
    tmp_str = response.read().decode('utf-8')
    results = json.loads(tmp_str)

    error_count = int(results['count'])
    message = "最近5分钟错误次数: {}".format(error_count)
    print(message)

    sns = boto3.client('sns')

    if error_count > 0:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message
        )
        print('sns response : {} '.format(response))


    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': "最近5分钟错误次数: {}".format(error_count)
    }
