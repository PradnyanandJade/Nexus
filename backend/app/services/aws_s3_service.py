import boto3
from app.config import settings
from fastapi.concurrency import run_in_threadpool

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

async def upload_file_to_s3(file_obj,s3_key: str,content_type: str):
    await run_in_threadpool(
        s3_client.upload_fileobj,
        file_obj,
        settings.AWS_S3_BUCKET,
        s3_key,
        ExtraArgs={
            "ContentType": content_type,
        },
    )
def generate_presigned_url(s3_key: str, expires_in: int = 18000):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_S3_BUCKET,
            "Key": s3_key,
        },
        ExpiresIn=expires_in,
    )

async def delete_file_from_s3(s3_key: str):
    await run_in_threadpool(
        s3_client.delete_object,
        Bucket=settings.AWS_S3_BUCKET,
        Key=s3_key,
    )

