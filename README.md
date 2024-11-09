# AWS CloudFormation Stack Checker 

The purpose of this repository is to create a Python script to:

1. Output the current status of a CloudFormation Stack.
2. If the stack is in a rollback state, output the name of the resource that triggered the rollback and the error message.
3. If the resource in #2 is a nested stack, output the name of the resource in the nested stack that triggered the rollback and the error message.

Additionally:
- AWS credentials and region are supplied to the script as environment variables (or with AWS configure).
- The script's output is JSON formatted.


## Prerequisites

1. NodeJS (v. 22+) NodeJS is required for running and installing AWS CDK. You can download it [here](https://nodejs.org/en/download/).
2. AWS CDK (v. 2.166.0): Please install its [prerequisites](https://cdkworkshop.com/15-prerequisites.html) and follow the  [Python workshop](https://cdkworkshop.com/30-python.html) first.
3. Python (v. 3.9.2) 

## Structure 

├── app.py
├── cdk.json
├── cfn_stack
│   ├── failing_nested_stack.py
│   ├── failing_stack.py
│   ├── __init__.py
│   ├── nested_stack_template
│   │   └── nested_stack_template.json
├── check_stack.py
├── __init__.py
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── tests
    ├── __init__.py
    └── unit
        ├── __init__.py
        ├── test_check_nested_stack_errors.py
        ├── test_check_stack_errors.py
        └── test_check_stack_status.py


## Components 

The main components of this repository are:

1. `check_stack.py` will check status, errors of a stack (or nested stacks) 
2. `app.py`will deploy necessary stacks with AWS CDK for testing the main script #1
3. `cfn_stack/failing_stack.py` will deploy a CloudFormation failing stack.
4. `cfn_stack/failing_nested_stack.py` will deploy a CloudFormation failing nested stack and a healthy main stack.
5. `tests/unit/test_check_stack_status.py` will unit test the status output of the main stack running script #1 using the `moto` library (mock_aws)
6. `tests/unit/test_check_stack_errors.py` will unit test the error output of the main stack running script #1 using the `boto3` library 
7. `tests/unit/test_check_nested_stack_errors.py` will unit test the error output of the nested stacks running script #1 using the `boto3` library 

## Testing 

There are 2 ways to test the main script `check_stack.py`:

1. Running unit tests (simple)
2. Deploying failing sample stacks with AWS CDK and executing the script

## Deployment steps

Position yourself in the `aws-cloudformation-stack-checker` folder if you aren't already there:

```
$ cd aws-cloudformation-stack-checker
```

Create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

Activate your virtualenv:

```
$ source .venv/bin/activate
```

Install the required dependencies:

```
$ pip3 install -r requirements.txt
```

Install the devevelopment dependencies for unit testing:

```
$ pip3 install -r requirements-dev.txt
```

### Configure AWS credentials and region

1. Configure AWS CLI (recommended):

```
$ aws configure
```

2. Using environment variables: 

```
$ export AWS_ACCESS_KEY_ID=AKIA******XAMPLE
$ export AWS_SECRET_ACCESS_KEY=wJalr******AMPLEKEY
$ export AWS_DEFAULT_REGION=us-west-1
```

### I. Running Unit Tests with Pytest 

```
$ python3 -m pytest tests/unit
```

### II. Init Failing Sample Stacks with CDK

Bootstrap the CDK stack:

```
$ cdk bootstrap 
```

Synthesize the CloudFormation template of the main stack:

```
$ cdk synth --app "python3 app.py --stack_name=FailedStackName"
```

Synthesize the CloudFormation template of the stack with the nested stack:

```
$ cdk synth --app "python3 app.py --nested_stack_name=FailedNestedStackName"
```

### Deploy Failing Sample Stacks


Deploy the main stack:

```
$ cdk deploy --app "python3 app.py --stack_name=FailedStackName"
```

Deploy the stack with the nested stack:

```
$ cdk synth --app "python3 app.py --nested_stack_name=FailedNestedStackName"
```

**Both stacks are expected to fail as part of the testing setup.**


### Deploy Failing Sample Stacks

Getting the JSON output of the main stack:

```
$ python3 check_stack.py FailedStackName
```

Getting the JSON output of the stack with the nested stack:

```
$ python3 check_stack.py FailedNestedStackName
```


### Parameters 

```
1. `FailedStackName` : Name of the main CloudFormation stack (Mandatory)
2. `FailedNestedStackName` : Name of the CloudFormation stack with nested stack (Mandatory)
```


### Destroy the Stack

```
cdk destroy --all
```

Enjoy!



