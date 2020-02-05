import os
"""
需要修改的变量

"""


class Constant:

    # Lambda 需要部署的vpc
    # VPC_ID =  os.env["VPC_ID"]
    VPC_ID = "vpc-0beaf2b26ba8eb173"

    # 部署ES 集群的私有子网id， 设置多个
    SUBNET_1_ID = 'subnet-01c7603aa410242c1'

    SUBNET_2_ID = 'subnet-0550a192dd93fbdd4'

    # 消息接收邮箱
    EMAIL_ADDRESS = 'liangzhang@nwcdcloud.cn'

    # 账户ID
    AWS_ACCOUNT = "690704700794"

    # region 名称
    REGION_NAME = "cn-northwest-1"

    # ES 集群的名称
    ES_CLUSTER_NAME = "cdk-es-demo"

    # 全球用'aws' 国内用 'aws-cn'
    AWS_GLOBAL_PREFIX = 'aws-cn'

