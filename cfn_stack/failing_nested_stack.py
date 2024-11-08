from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudformation as cfn,
    aws_iam as iam,
    Stack,
    RemovalPolicy,
    App,
    CfnParameter,
)
from constructs import Construct

class FailingNestedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = "sample-bucket-failed-nested-stack"
        nested_stack_key = "nested_stack_template.json"

        sample_bucket = s3.Bucket(self, "SampleBucket",
            bucket_name=bucket_name,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        nested_template_deployment = s3_deployment.BucketDeployment(self, "NestedTemplateDeployment",
            sources=[s3_deployment.Source.asset(f"cfn_stack/nested_stack_template")],
            destination_bucket=sample_bucket,
            destination_key_prefix=""
        )

        nested_stack = cfn.CfnStack(self, "NestedStack",
            template_url=f"https://{bucket_name}.s3.us-west-1.amazonaws.com/{nested_stack_key}"
        )

        nested_stack.node.add_dependency(sample_bucket)
        nested_stack.node.add_dependency(nested_template_deployment)


