#!/usr/bin/env python3

from aws_cdk import core

from cdk_infra.cdk_infra_stack import CdkInfraStack

app = core.App()
infra_stack = CdkInfraStack(app, "cdk-infra")

app.synth()
