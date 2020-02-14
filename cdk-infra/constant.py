import os
"""
需要修改的变量

"""


class Constant:

    # 消息接收邮箱
    EMAIL_ADDRESS = 'you@email.com'

    PROJECT_NAME = 'cdk-demo'

    # ES 集群的名称
    ES_CLUSTER_NAME = "cdk-demo-es"

    # ES index 名称
    ES_INDEX_NAME = 'log_index'

    # filebeat 监控的日志路径
    ES_LOG_PATH = '/home/ec2-user/web-app/target/logs/*.log'

    #ec2 秘钥名称， 需要提前创建好，登录ec2需要
    EC2_KEY_NAME = "id_rsa"

    #不同区域的共享AMI ID

    ZHY_EC2_AMI_ID = 'ami-08469f09ea12dce3a'
    BJ_EC2_AMI_ID = 'ami-085fcc092e0269581'

    #安装的region 名称
    REGION_NAME = 'cn-northwest-1'

    # 防止资源重复
    RANDOM_STR = '123'