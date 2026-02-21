# S3 storage service - handles all file uploads and downloads to AWS S3
# Copy and paste everything into backend/services/s3_storage.py

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    # Upload a local file to S3 and return its public URL
    s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
    url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
    return url


def download_file_from_s3(s3_key: str, local_path: str):
    # Download a file from S3 to local disk
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    s3_client.download_file(BUCKET_NAME, s3_key, local_path)


def upload_fileobj_to_s3(file_obj, s3_key: str) -> str:
    # Upload a file object directly to S3
    s3_client.upload_fileobj(file_obj, BUCKET_NAME, s3_key)
    url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
    return url


def get_presigned_url(s3_key: str, expiry: int = 3600) -> str:
    # Generate a temporary URL for downloading a file
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": s3_key},
        ExpiresIn=expiry
    )
    return url