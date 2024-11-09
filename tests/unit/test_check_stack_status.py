import boto3
import json
import unittest
import os
from moto import mock_aws

from check_stack import check_stack

class TestStackStatus(unittest.TestCase):

    session = boto3.Session()
    region = os.environ.get("AWS_DEFAULT_REGION") or session.region_name  

    stack_name = "TestStack"

    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()


        cfn = boto3.client('cloudformation', region_name=self.region)

        cfn.create_stack(
            StackName=self.stack_name,
            TemplateBody=json.dumps({
                "Resources": {
                    "SampleBucket": {
                        "Type": "AWS::S3::Bucket"
                    }
                }
            })
        )

    def tearDown(self):
        self.mock_aws.stop()


    def test_stack_status(self):

        result = check_stack(self.stack_name)

        self.assertEqual(result['StackName'], self.stack_name)
        self.assertEqual(result['StackStatus'], "CREATE_COMPLETE")


if __name__ == "__main__":
    unittest.main()


