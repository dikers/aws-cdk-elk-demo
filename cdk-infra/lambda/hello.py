import urllib.request
import json
import os
import boto3

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
ES_ENDPOINT = os.environ['ES_ENDPOINT']
ES_INDEX_NAME = os.environ['ES_INDEX_NAME']


def handler(event, context):

    print('SNS_TOPIC_ARN : {}  '.format(SNS_TOPIC_ARN))
    print('ES_ENDPOINT   : {}  '.format(ES_ENDPOINT))

    es_url = 'https://{}/{}/_count'.format(ES_ENDPOINT, ES_INDEX_NAME)

    print(es_url)
    formData = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"error_code": 1111}},
                    {"range": {"create_time": {"gt": "now-5m", "lte": "now"}}}
                ]
            }
        }
    }

    formData = json.dumps(formData).encode()
    print('查询条件： {} '.format(formData))

    headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}

    req = urllib.request.Request(url=es_url,
                                 data=formData, headers=headers)

    response = urllib.request.urlopen(req)
    tmp_str = response.read().decode('utf-8')
    results = json.loads(tmp_str)

    error_count = int(results['count'])
    message = "最近5分钟错误次数: {}".format(error_count)
    print(message)

    sns = boto3.client('sns')

    if error_count > 5:
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
