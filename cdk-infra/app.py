#!/usr/bin/env python3

from aws_cdk import core

from cdk_infra.cdk_infra_stack import CdkInfraStack
from constant import Constant


env_cn = core.Environment(region=Constant.REGION_NAME)
app = core.App()
infra_stack = CdkInfraStack(app, "cdk-infra", env=env_cn)

app.synth()
