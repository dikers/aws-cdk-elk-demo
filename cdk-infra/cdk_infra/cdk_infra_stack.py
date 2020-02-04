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
        # es_cluster_arn = '"arn:aws-cn:es:{}:{}:domain/{}/*"'.format(Constant.REGION_NAME, Constant.AWS_ACCOUNT, Constant.ES_CLUSTER_NAME)
        # print(es_cluster_arn)
        # elasticsearch.CfnDomain(
        #     self, Constant.ES_CLUSTER_NAME,
        #     elasticsearch_version='7.1',
        #     access_policies={
        #         "Version": "2012-10-17",
        #         "Statement": [
        #             {
        #                 "Effect": "Allow",
        #                 "Principal": {
        #                     "AWS": "*"
        #                 },
        #                 "Action": "es:*",
        #                 "Resource": es_cluster_arn
        #             }
        #         ]
        #     },
        #     vpc_options={
        #         "SubnetIds": [Constant.SUBNET_1_ID]
        #     },
        #     ebs_options={'EBSEnabled': True,  'VolumeSize': 100, 'VolumeType': 'gp2', 'Iops': 3000},
        #     elasticsearch_cluster_config={"DedicatedMasterCount": 1,
        #                                   "DedicatedMasterEnabled": False,
        #                                   "DedicatedMasterType": 'm4.large.elasticsearch',
        #                                   "InstanceCount": 1,
        #                                   "InstanceType": 'm3.medium.elasticsearch',
        #                                   "ZoneAwarenessEnabled": False}
        # )

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
                'SNS_TOPIC_ARN': topic.topic_arn
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




