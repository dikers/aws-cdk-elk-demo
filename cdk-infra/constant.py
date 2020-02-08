import os
"""
需要修改的变量

"""


class Constant:

    # 消息接收邮箱
    EMAIL_ADDRESS = 'you@email.com'

    # ES 集群的名称
    ES_CLUSTER_NAME = "cdk-es-demo"

    # ES index 名称
    ES_INDEX_NAME = 'log_index'

    # filebeat 监控的日志路径
    ES_LOG_PATH = '/home/ec2-user/web-app/target/logs/*'

    #ec2 秘钥名称， 需要提前创建好，登录ec2需要
    EC2_KEY_NAME = "id_rsa"

    #不同区域的共享AMI ID
    ZHY_EC2_AMI_ID = 'ami-0823eb3d6e4a54e1f'
    BJ_EC2_AMI_ID = 'ami-0ffd35f1ea4a72d0d'

    #安装的region 名称
    REGION_NAME = 'cn-north-1'
