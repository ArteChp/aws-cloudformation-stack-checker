import boto3
import json
import sys
import logging
import time 
from typing import Tuple, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_stack_status(cfn_client, stack_name: str) -> Dict[str, Any]:
    """Retrieve stack status from CloudFormation."""
    return cfn_client.describe_stacks(StackName=stack_name)['Stacks'][0]

def is_in_progress(stack_status: str) -> bool:
    """Check if stack status is in a progress state."""
    return stack_status in ["CREATE_IN_PROGRESS", "UPDATE_IN_PROGRESS", "DELETE_IN_PROGRESS", "ROLLBACK_IN_PROGRESS"]

def get_rollback_details(cfn_client, stack_name: str) -> Dict[str, Any]:
    """Retrieve rollback details if stack is in rollback state."""
    result = {
        "RollbackTriggeredBy": None,
        "ErrorMessage": None,
        "NestedStackError": None
    }
    
    events = cfn_client.describe_stack_events(StackName=stack_name)['StackEvents']
    for event in events:
        if "FAILED" in event['ResourceStatus']:
            result["RollbackTriggeredBy"] = event['LogicalResourceId']
            result["ErrorMessage"] = event['ResourceStatusReason']
            if event['ResourceType'] == 'AWS::CloudFormation::Stack':
                nested_stack_name = event['PhysicalResourceId']
                logger.info(f"Nested stack {nested_stack_name} error details being fetched.")
                nested_events = cfn_client.describe_stack_events(StackName=nested_stack_name)['StackEvents']
                for nested_event in nested_events:
                    if "FAILED" in nested_event['ResourceStatus']:
                        result["NestedStackError"] = {
                            "NestedStack": nested_stack_name,
                            "FailedResource": nested_event['LogicalResourceId'],
                            "ErrorMessage": nested_event['ResourceStatusReason']
                        }
                        break
            break
    
    return result

def check_stack(stack_name: str) -> Dict[str, Any]:
    """Monitor stack status and retrieve rollback details if necessary."""
    cfn_client = boto3.client('cloudformation', region_name='us-west-1')

    try:
        while True:
            cfn_stack = get_stack_status(cfn_client, stack_name)
            stack_status = cfn_stack['StackStatus']

            if not is_in_progress(stack_status):
                break  

            time.sleep(5)

        result = {
            "StackName": cfn_stack['StackName'],
            "StackStatus": stack_status,
        }

        if "ROLLBACK" in stack_status:
            logger.info(f"Stack {stack_name} is in rollback state; fetching details.")
            rollback_details = get_rollback_details(cfn_client, stack_name)
            result.update(rollback_details)

        return result

    except cfn_client.exceptions.ClientError as e:
        return {"Error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"Error": "Please specify the CloudFormation stack name as an argument."}))
        sys.exit(1)

    stack_name = sys.argv[1]
    result = check_stack(stack_name)
    logger.info(json.dumps(result, indent=4))
