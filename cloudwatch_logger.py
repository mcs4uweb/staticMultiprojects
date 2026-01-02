import argparse
import sys
import time

import boto3
from botocore.exceptions import ClientError


def create_logs_client(region_name, profile):
    if profile:
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3.Session()
    return session.client("logs", region_name=region_name)


def ensure_log_group(logs_client, log_group):
    try:
        logs_client.create_log_group(logGroupName=log_group)
        print(f"Created log group '{log_group}'.")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ResourceAlreadyExistsException":
            print(f"Log group '{log_group}' already exists.")
        else:
            raise


def ensure_log_stream(logs_client, log_group, log_stream):
    try:
        logs_client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        print(f"Created log stream '{log_stream}'.")
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ResourceAlreadyExistsException":
            print(f"Log stream '{log_stream}' already exists.")
        else:
            raise


def put_log_message(logs_client, log_group, log_stream, message):
    describe_resp = logs_client.describe_log_streams(
        logGroupName=log_group,
        logStreamNamePrefix=log_stream,
        limit=1,
    )
    sequence_token = None
    log_streams = describe_resp.get("logStreams", [])
    if log_streams:
        sequence_token = log_streams[0].get("uploadSequenceToken")

    event = {"timestamp": int(time.time() * 1000), "message": message}
    request = {
        "logGroupName": log_group,
        "logStreamName": log_stream,
        "logEvents": [event],
    }
    if sequence_token:
        request["sequenceToken"] = sequence_token

    response = logs_client.put_log_events(**request)
    next_token = response.get("nextSequenceToken")
    if next_token:
        print(f"Log event accepted. Next sequence token: {next_token}")
    else:
        print("Log event accepted.")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Send a single log message to AWS CloudWatch Logs."
    )
    parser.add_argument("log_group", help="CloudWatch Logs log group name.")
    parser.add_argument("log_stream", help="CloudWatch Logs log stream name.")
    parser.add_argument("message", help="Message body for the log event.")
    parser.add_argument(
        "--region",
        default="us-gov-west-1",
        help="AWS region for CloudWatch Logs (default: us-gov-west-1).",
    )
    parser.add_argument(
        "--profile",
        help="Name of the AWS profile to use (defaults to the current environment).",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    logs_client = create_logs_client(args.region, args.profile)
    ensure_log_group(logs_client, args.log_group)
    ensure_log_stream(logs_client, args.log_group, args.log_stream)
    put_log_message(logs_client, args.log_group, args.log_stream, args.message)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
