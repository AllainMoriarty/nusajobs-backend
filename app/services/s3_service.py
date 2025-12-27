import boto3
from botocore.exceptions import ClientError
from typing import Optional
from app.core.config import settings

class S3Service:
    def __init__(self):
        # Setup S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Upload file to S3
        Returns: URL of uploaded file or None if failed
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_data,
                ContentType=content_type
            )
            # Return the file URL
            file_url = f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{filename}"
            return file_url
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from S3
        Returns: True if success, False if failed
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists in S3
        Returns: True if exists, False if not
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            # Other error
            print(f"Error checking file existence: {e}")
            return False

    def get_file_url(self, filename: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for file access
        expires_in: URL expiration time in seconds (default: 1 hour)
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=expires_in
            )
            return presigned_url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

s3_service = S3Service()