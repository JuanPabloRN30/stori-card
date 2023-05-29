import logging
import os
import urllib.parse

import boto3

from emails import Email
from handlers import InMemoryReportHandler
from models import GenerateReportCommand
from notifications import EmailReportNotification
from process import process_transaction_file

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client("s3")
ssm = boto3.client("ssm")

EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def _get_ssm_parameter(name: str) -> str:
    """Get a parameter from AWS SSM."""
    return ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


EMAIL_PASSWORD = _get_ssm_parameter(os.getenv("EMAIL_PASSWORD"))
EMAIL_SENDER = _get_ssm_parameter(os.getenv("EMAIL_SENDER"))


def lambda_handler(event, context):
    """Lambda handler react to S3 events.

    Download the file from S3, process it and send the report by email.
    """

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    local_path = "/tmp/file.csv"
    try:
        s3.download_file(bucket, key, local_path)

        command = GenerateReportCommand(
            filepath=local_path, receiver_email=EMAIL_RECEIVER
        )
        process_transaction_file(
            InMemoryReportHandler(),
            EmailReportNotification(Email(EMAIL_SENDER, EMAIL_PASSWORD)),
            command,
        )

    except Exception as e:
        logger.error(e)
        logger.error(
            f"Error getting object {key} from bucket {bucket}. Make sure they "
            "exist and your bucket is in the same region as this function."
        )
        raise e

    return {"message": "Report sent!"}
