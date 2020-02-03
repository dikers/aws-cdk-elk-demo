from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_events_targets as targets,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
    core,
)

from constant import Constant


class CdkInfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=Constant.VPC_ID)

        # SNS
        topic = sns.Topic(
            self, "topic"
        )
        topic.add_subscription(subs.EmailSubscription(Constant.EMAIL_ADDRESS))

        # 设置SNS endpoint, 让lambda 可以从vpc 内部访问
        vpc.add_interface_endpoint("SNSEndpoint", service=ec2.InterfaceVpcEndpointAwsService.SNS)

        # The code that defines your stack goes here
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

        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
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




