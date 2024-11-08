#!/usr/bin/env python3

import os
import sys 
import aws_cdk as cdk
from cfn_stack.failing_nested_stack import FailingNestedStack
from cfn_stack.failing_stack import FailingStack

env_us_west_1 = cdk.Environment(region="us-west-1")

app = cdk.App()

stack_name = None
nested_stack_name = None

for arg in sys.argv[1:]:
    if arg.startswith("--stack_name="):
        stack_name = arg.split("=")[1]
    elif arg.startswith("--nested_stack_name="):
        nested_stack_name = arg.split("=")[1]

if stack_name:
    failing_stack = FailingStack(app, stack_name, env=env_us_west_1)

if nested_stack_name:
    failing_nested_stack = FailingNestedStack(app, nested_stack_name, env=env_us_west_1)

app.synth()

