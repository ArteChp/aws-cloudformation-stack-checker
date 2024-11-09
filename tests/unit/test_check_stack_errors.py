import json
import unittest
import os
import boto3

from check_stack import check_stack

class TestStackErrors(unittest.TestCase):

    session = boto3.Session()
    region = os.environ.get("AWS_DEFAULT_REGION") or session.region_name

    stack_name = "TestStack"

    def setUp(self):


        cfn = boto3.client('cloudformation', region_name=self.region)

        cfn.create_stack(
            StackName=self.stack_name,
            TemplateBody=json.dumps({
                "Resources": {
                    "SampleBucket": {
                        "Type": "AWS::S3::Bucket",
                        "Properties": {
                             "AccessControl": "PublicRead",
                             "PublicAccessBlockConfiguration": {
                                  "BlockPublicAcls": "false",
                                  "BlockPublicPolicy": "false",
                                  "IgnorePublicAcls": "false",
                                  "RestrictPublicBuckets": "false"
                            }
                        }
                    }
                }
            })
        )

    def tearDown(self):
        cfn = boto3.client('cloudformation', region_name=self.region)
        cfn.delete_stack(
            StackName=self.stack_name
        )


    def test_stack_status(self):

        result = check_stack(self.stack_name)

        self.assertEqual(result['StackName'], self.stack_name)
        self.assertIsNotNone(result['RollbackTriggeredBy'])
        self.assertIsNotNone(result['ErrorMessage'])


if __name__ == "__main__":
    unittest.main()
