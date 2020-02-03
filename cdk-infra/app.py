#!/usr/bin/env python3

from aws_cdk import core

from cdk_infra.cdk_infra_stack import CdkInfraStack
from constant import Constant

# Define your account id to make import vpc work
env_cn = core.Environment(account=Constant.AWS_ACCOUNT, region=Constant.REGION_NAME)

app = core.App()
CdkInfraStack(app, "cdk-infra",  env=env_cn)

app.synth()
