from aws_cdk import (
    aws_s3 as s3,
    Stack,
    RemovalPolicy,
    App,
    CfnParameter,
    CfnResource,
)
from constructs import Construct

class FailingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        sample_bucket = s3.Bucket(self, "SampleBucket",
            removal_policy=RemovalPolicy.DESTROY
        )

        CfnResource(self, "InvalidResourceProperty",
            type="AWS::S3::Bucket",
            properties={
                "BucketName": sample_bucket.bucket_name,
                "NonExistentProperty": "InvalidValue"  # Invalid property that will cause a CloudFormation error
            }
        )


