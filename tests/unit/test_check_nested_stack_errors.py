import json
import unittest
import time
import os
import boto3

from check_stack import check_stack

class TestNestedStackErrors(unittest.TestCase):

    session = boto3.Session()
    region = os.environ.get("AWS_DEFAULT_REGION") or session.region_name


    stack_name = "TestNestedStack"
    bucket_name = "test-nested-stack-s3-bucket"
    nested_stack_key = "nested_stack_template.json"
    change_set_name = "AddNestedStackChangeSet"
    failing_resource_name = "FailingResource"

    initial_template = {
        "Resources": {
            "TestBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": bucket_name,
                    "OwnershipControls": {
                        "Rules": 
                        [
                          {
                            "ObjectOwnership": "BucketOwnerEnforced"
                          }
                        ]
                     },
                    "PublicAccessBlockConfiguration": {
                      "IgnorePublicAcls": "true",
                      "BlockPublicAcls": "true",
                      "BlockPublicPolicy": "false",
                      "RestrictPublicBuckets": "false"
                    }
                }
            },
            "TestBucketPolicy": {
            "Type": "AWS::S3::BucketPolicy",
            "Properties": {
                "Bucket": {"Ref": "TestBucket"},
                "PolicyDocument": {
                    "Statement": 
                        [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "cloudformation.amazonaws.com"},
                                "Action": ["s3:GetObject"],
                                "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "TestBucket"}, "/*"]]}
                            }
                        ]
                    }
                }
            }
        }
    }

    nested_stack_template = {
        "Resources": {
            f"{failing_resource_name}": {
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
    }

    updated_template = {
        "Resources": {
            "TestBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": bucket_name,
                    "OwnershipControls": {
                        "Rules": 
                        [
                          {
                            "ObjectOwnership": "BucketOwnerEnforced"
                          }
                        ]
                     },
                    "PublicAccessBlockConfiguration": {
                      "IgnorePublicAcls": "true",
                      "BlockPublicAcls": "true",
                      "BlockPublicPolicy": "false",
                      "RestrictPublicBuckets": "false"
                    }
                }
            },
            "TestBucketPolicy": {
            "Type": "AWS::S3::BucketPolicy",
            "Properties": {
                "Bucket": {"Ref": "TestBucket"},
                "PolicyDocument": {
                    "Statement": 
                        [
                            {
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": ["s3:GetObject"],
                                "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "TestBucket"}, "/*"]]}
                            }
                        ]
                    }
                }
            },
            "NestedStack": {
                "Type": "AWS::CloudFormation::Stack",
                "Properties": {
                    "TemplateURL": f"https://{bucket_name}.s3.us-west-1.amazonaws.com/{nested_stack_key}"
                }
            }
        }
    }

    def setUp(self):


        cfn_client = boto3.client('cloudformation', region_name=self.region)
        s3_client = boto3.client('s3', region_name=self.region)

        cfn_client.create_stack(
            StackName=self.stack_name,
            TemplateBody=json.dumps(self.initial_template)
        )

        waiter = cfn_client.get_waiter('stack_create_complete')
        waiter.wait(StackName=self.stack_name)

        s3_client.put_object(
            Bucket=self.bucket_name,
            Key=self.nested_stack_key,
            Body=json.dumps(self.nested_stack_template)
        )

        cfn_client.create_change_set(
            StackName=self.stack_name,
            TemplateBody=json.dumps(self.updated_template),
            ChangeSetName=self.change_set_name,
            ChangeSetType="UPDATE"
        )

        waiter = cfn_client.get_waiter('change_set_create_complete')
        waiter.wait(StackName=self.stack_name, ChangeSetName=self.change_set_name)

        cfn_client.execute_change_set(ChangeSetName=self.change_set_name, StackName=self.stack_name)



    def tearDown(self):
        s3_client = boto3.client('s3', region_name=self.region)

        objects = s3_client.list_objects_v2(Bucket=self.bucket_name)

        if 'Contents' in objects:
            s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': [{'Key': obj['Key']} for obj in objects['Contents']]
                }
            )


        cfn_client = boto3.client('cloudformation', region_name=self.region)

        while True:
            response = cfn_client.describe_stacks(StackName=self.stack_name)
            stack_status = response['Stacks'][0]['StackStatus']

            if stack_status not in ["UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS", "UPDATE_ROLLBACK_IN_PROGRESS"]:
                break

            time.sleep(10)

        cfn_client.delete_stack(StackName=self.stack_name)

        waiter = cfn_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=self.stack_name)



    def test_nested_stack_errors(self):

        result = check_stack(self.stack_name)


        self.assertEqual(result['StackName'], self.stack_name)
        if result['NestedStackError']:
            self.assertIn(self.stack_name, result['NestedStackError']['NestedStack'])
            self.assertIn(self.stack_name, result['NestedStackError']['FailedResource'])
            self.assertIn(self.failing_resource_name, result['NestedStackError']['ErrorMessage'])
        else:
            self.fail("Expected 'NestedStackError' in result but found None")

if __name__ == "__main__":
    unittest.main()
