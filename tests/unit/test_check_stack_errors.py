import boto3
import json
import unittest

from check_stack import check_stack

class TestStackErrors(unittest.TestCase):

    stack_name = "TestStack"

    def setUp(self):


        cfn = boto3.client('cloudformation', region_name='us-west-1')

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
        cfn = boto3.client('cloudformation', region_name='us-west-1')
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


