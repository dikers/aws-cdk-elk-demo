from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_events_targets as targets,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
    aws_elasticsearch as elasticsearch,
    core,
)

from constant import Constant


class CdkInfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # step 1. VPC
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=Constant.VPC_ID)

        # step 2. ES
        es_cluster_arn = 'arn:{}:es:{}:{}:domain/{}/*'.format(Constant.AWS_GLOBAL_PREFIX, Constant.REGION_NAME,
                                                Constant.AWS_ACCOUNT, Constant.ES_CLUSTER_NAME)

        sg_es_cluster = ec2.SecurityGroup(
            self,
            id="sg_es_cluster",
            vpc=vpc,
            security_group_name="sg_es_cluster"
        )

        sg_es_cluster.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443)
        )

        es = elasticsearch.CfnDomain(
            self, Constant.ES_CLUSTER_NAME,
            elasticsearch_version='7.1',
            domain_name=Constant.ES_CLUSTER_NAME,
            node_to_node_encryption_options={"enabled": False},
            vpc_options={
                "securityGroupIds": [sg_es_cluster.security_group_id],
                "subnetIds": [Constant.SUBNET_1_ID]
            },
            ebs_options={"ebsEnabled": True, "volumeSize": 30, "volumeType": "gp2"},
            elasticsearch_cluster_config={
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
                    "Resource": es_cluster_arn
                }
            ]
        }

        # step 3.  SNS
        topic = sns.Topic(
            self, "topic"
        )
        topic.add_subscription(subs.EmailSubscription(Constant.EMAIL_ADDRESS))

        # 设置SNS endpoint, 让lambda 可以从vpc 内部访问
        vpc.add_interface_endpoint("SNSEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SNS)

        # step 4. Lambda
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
            }
        )

        # step 5. Cloud watch event
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                minute='0/5',
                hour='10',
                month='*',
                week_day='*',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))

        #给Lambda 添加发布SNS的权限
        topic.grant_publish(lambdaFn)




