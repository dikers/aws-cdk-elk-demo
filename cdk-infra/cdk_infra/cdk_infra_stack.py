from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_events_targets as targets,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
    aws_elasticsearch as elasticsearch,
    aws_elasticloadbalancingv2 as elb,
    aws_autoscaling as autoscaling,
    core,
)

from aws_cdk.aws_iam import (
    Role,
    Policy,
    ServicePrincipal,
    CfnInstanceProfile,
    Effect,
    PolicyStatement,
)
from constant import Constant


# 中国两个区域会用到不同的ami_id
ami_map = {
    'cn-northwest-1': Constant.ZHY_EC2_AMI_ID,
    'cn-north-1': Constant.BJ_EC2_AMI_ID,
}

my_ami = ec2.GenericLinuxImage(ami_map)

with open("./user_data/user_data.sh") as f:
    user_data_content = f.read()


class CdkInfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # step 1. VPC
        # 如果在已有的Vpc 中建立环境， 可以用下面这句， 需要传入 vpc_id
        # vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id='')
        vpc = ec2.Vpc(self, "VPC",
                max_azs=2,  # 两个分区， 每个分区建一个子网
                cidr="10.10.0.0/16",
                # configuration will create 3 groups in 2 AZs = 6 subnets.
                subnet_configuration=[ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name="Private",
                    cidr_mask=24
                ),
                # ec2.SubnetConfiguration(
                #     subnet_type=ec2.SubnetType.ISOLATED,
                #     name="DB",
                #     cidr_mask=24
                # )
                ],
                # nat_gateway_provider=ec2.NatProvider.gateway(),
                # nat_gateways=2,
                )

        # ES 需要部署到私有子网中
        selection = vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE
        )

        # step 2. 访问ES 集群需要的 iam_instance_profile
        #  action -> statement -> policy -> role -> instance profile ->  attach ec2

        actions = ["ec2:CreateNetworkInterface",
                   "ec2:DeleteNetworkInterface",
                   "ec2:DescribeNetworkInterfaces",
                   "ec2:ModifyNetworkInterfaceAttribute",
                   "ec2:DescribeSecurityGroups",
                   "ec2:DescribeSubnets",
                   "ec2:DescribeVpcs"]

        policyStatement = PolicyStatement(actions=actions, effect=Effect.ALLOW)
        policyStatement.add_all_resources()
        policyStatement.sid = "Stmt1480452973134"

        policy = Policy(self, "CDK_EC2AccessElasticSearchPolicy", policy_name="CDK_EC2AccessElasticSearchPolicy")

        policy.add_statements(policyStatement)

        access_es_role = Role(
            self, 'CDK_EC2AccessElasticSearchRole',
            role_name='CDK_EC2AccessElasticSearchRole',
            assumed_by=ServicePrincipal('ec2.amazonaws.com.cn')
        )
        policy.attach_to_role(access_es_role)
        instance_profile = CfnInstanceProfile(self, "CDK_EC2AccessElasticSearchInstanceProfile",
                instance_profile_name="CDK_EC2AccessElasticSearchInstanceProfile",
                roles=[access_es_role.role_name])

        # step 4. ES
        es_arn = self.format_arn(
            service="es",
            resource="domain",
            sep="/",
            resource_name=Constant.ES_CLUSTER_NAME
        )

        # 生产环境建议设置安全组， 只接收VPC内443端口请求
        sg_es_cluster = ec2.SecurityGroup(self,id="sg_es_cluster",vpc=vpc,
            security_group_name="sg_es_cluster")

        sg_es_cluster.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443))

        es = elasticsearch.CfnDomain(
            self, Constant.ES_CLUSTER_NAME,
            elasticsearch_version='7.1',
            domain_name=Constant.ES_CLUSTER_NAME,
            node_to_node_encryption_options={"enabled": False},
            vpc_options={
                "securityGroupIds": [sg_es_cluster.security_group_id],  # 生产环境建议设置安全组， 只接收VPC内443端口请求
                # 如果开启多个节点， 需要配置多个子网， 目前测试只有一个ES 节点， 就只用到一个子网
                "subnetIds": selection.subnet_ids[:1]
            },
            ebs_options={"ebsEnabled": True, "volumeSize": 10, "volumeType": "gp2"},
            elasticsearch_cluster_config={
                                          # 生成环境需要开启三个
                                          # "dedicatedMasterCount": 3,
                                          # "dedicatedMasterEnabled": True,
                                          # "dedicatedMasterType": 'm4.large.elasticsearch',
                                          "instanceCount": 1,
                                          "instanceType": 'm4.large.elasticsearch',
                                          "zoneAwarenessEnabled": False}
        )
        es.access_policies = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": "es:*",
                    "Resource": "{}/*".format(es_arn)
                }
            ]
        }

        # step 5.  SNS
        topic = sns.Topic(self, "topic")
        topic.add_subscription(subs.EmailSubscription(Constant.EMAIL_ADDRESS))

        # 设置SNS endpoint, 让lambda 可以从vpc 内部访问
        vpc.add_interface_endpoint("SNSEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SNS)

        # step 6. Lambda
        lambdaFn = lambda_.Function(
            self, "Singleton",
            code=lambda_.Code.asset('lambda'),
            handler='hello.handler',
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE),
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
            environment={
                'SNS_TOPIC_ARN': topic.topic_arn,
                'ES_ENDPOINT': es.attr_domain_endpoint,
                'ES_INDEX_NAME': Constant.ES_INDEX_NAME
            }
        )

        # step 7. Cloud watch event
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='0/5',
                hour='*',
                month='*',
                week_day='*',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        #给Lambda 添加发布SNS的权限
        topic.grant_publish(lambdaFn)




        # Create ALB
        alb = elb.ApplicationLoadBalancer(self, "myALB",
                                          vpc=vpc,
                                          internet_facing=True,
                                          load_balancer_name="myALB")
        alb.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Internet access ALB 80")
        listener = alb.add_listener("my80", port=80, open=True)

        # Create Autoscaling Group with fixed 2*EC2 hosts

        user_data = user_data_content.format(es.attr_domain_endpoint, Constant.REGION_NAME,
                                                                  Constant.ES_LOG_PATH, Constant.ES_INDEX_NAME)

        # step 3. 创建堡垒机
        bastion = ec2.BastionHostLinux(self, "myBastion",
                                       vpc=vpc,
                                       subnet_selection=ec2.SubnetSelection(
                                           subnet_type=ec2.SubnetType.PUBLIC),
                                       instance_name="BastionHost",
                                       instance_type=ec2.InstanceType(instance_type_identifier="m4.large"))
        bastion.instance.instance.add_property_override("KeyName", Constant.EC2_KEY_NAME)
        bastion.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Internet access SSH") # 生成环境可以限定IP allow_from
        bastion.connections.allow_from_any_ipv4(ec2.Port.tcp(8080), "Internet access HTTP")  # 测试需要
        bastion.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Internet access HTTPS")  # 测试需要

        bastion.instance.instance.iam_instance_profile = instance_profile.instance_profile_name   # 给EC2设置 profile , 相当于Role
        bastion.instance.instance.image_id = ami_map.get(Constant.REGION_NAME)  # 指定AMI ID

        #堡垒机的user_data 只能执行一次， 如果要执行多次， 请参考 https://amazonaws-china.com/premiumsupport/knowledge-center/execute-user-data-ec2/?nc1=h_ls
        bastion_user_data = "/home/ec2-user/start.sh {}  {} '{}' {}".format(es.attr_domain_endpoint,
                                                                            Constant.REGION_NAME,
                                                                            Constant.ES_LOG_PATH,
                                                                            Constant.ES_INDEX_NAME)
        bastion.instance.add_user_data("date >> /home/ec2-user/root.txt")  # 查看启动脚本是否执行
        bastion.instance.add_user_data(bastion_user_data)

        asg = autoscaling.AutoScalingGroup(self, "myASG",
                                                vpc=vpc,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC), # PUBLIC for debug
                                                instance_type=ec2.InstanceType(instance_type_identifier="m4.large"),
                                                machine_image=my_ami,
                                                key_name=Constant.EC2_KEY_NAME,
                                                user_data=ec2.UserData.custom(user_data),
                                                desired_capacity=1,
                                                min_capacity=1,
                                                max_capacity=1,
                                                role=access_es_role )

        asg.connections.allow_from(alb, ec2.Port.tcp(8080), "ALB access 80 port of EC2 in Autoscaling Group")
        # asg.connections.allow_from_any_ipv4(ec2.Port.tcp(8080), "Internet access HTTP for test") # 测试用
        asg.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Internet access SSH")  # for debug
        listener.add_targets("addTargetGroup", port=8080, targets=[asg])


        # Elastic Search 统计log 数量， 可以在堡垒机上执行， 快速查看日志数量。
        core.CfnOutput(self, "CmdGetCountIndex", value='curl https://{}/{}/_count'.format(es.attr_domain_endpoint, Constant.ES_INDEX_NAME))

        # 堡垒机的登录命令， 可以直接复制使用
        core.CfnOutput(self, "CmdSshToBastion", value='ssh -i ~/{}.pem ec2-user@{}'.format(Constant.EC2_KEY_NAME, bastion.instance_public_dns_name))

        # 在堡垒机上启动服务的命令， 堡垒机重启以后， 需要执行下面的命令， 可以启动web服务 发送日志到ES
        core.CfnOutput(self, "CmdSshBastionStartWeb", value='sudo {}'.format(bastion_user_data))

        # ALB 的访问地址， 第一次访问的时候， 要等待一段时间， 需要和AutoScaling建立关联。
        core.CfnOutput(self, "UrlLoad_Balancer", value='http://{}'.format(alb.load_balancer_dns_name))

        # 堡垒机的web访问地址， 为了调试方便， 在堡垒机上也使用相同的AMI。
        core.CfnOutput(self, "UrlBastion", value='http://{}:8080'.format(bastion.instance_public_dns_name))

        # 下面这条输出的命令 是通过堡垒机和Elasticsearch 建立隧道， 在本地访问kibana。
        core.CfnOutput(self, "CmdSshProxyToKinana", value='ssh -i ~/{}.pem ec2-user@{}  -N -L 9200:{}:443'.format(Constant.EC2_KEY_NAME, bastion.instance_public_dns_name,es.attr_domain_endpoint ))
        # 执行完上面的命令后， 在浏览器中打开下面的连接
        core.CfnOutput(self, "UrlKibana", value='https://localhost:9200/_plugin/kibana/')


