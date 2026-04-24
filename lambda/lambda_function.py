import json
import boto3

def handler(event, context):
    ec2 = boto3.client(
        "ec2",
        endpoint_url="http://localhost.localstack.cloud:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

    body = event.get("body")

    if body:
        body = json.loads(body)
    else:
        body = event

    action = body.get("action", "describe")
    instance_id = body.get("instance_id")

    if action == "describe":
        result = ec2.describe_instances()
        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str)
        }

    if action == "start":
        result = ec2.start_instances(InstanceIds=[instance_id])
        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str)
        }

    if action == "stop":
        result = ec2.stop_instances(InstanceIds=[instance_id])
        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str)
        }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "action invalide"})
    }

