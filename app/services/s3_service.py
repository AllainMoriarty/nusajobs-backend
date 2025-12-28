import boto3
from botocore.exceptions import ClientError
from typing import Optional, List
from app.core.config import settings

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.gateway_url = "https://gradual-chocolate-cephalopod.myfilebase.com/ipfs"

    def upload_file(self, file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Upload file ke Filebase dan kembalikan URL IPFS Gateway
        """
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_data,
                ContentType=content_type
            )
            
            # Filebase mengembalikan CID di dalam header metadata
            cid = response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amz-meta-cid')
            
            if cid:
                # Mengembalikan URL dengan format Gateway
                return f"{self.gateway_url}/{cid}"
            
            return None
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

    def get_file_url(self, filename: str) -> Optional[str]:
        """
        Mendapatkan URL Gateway berdasarkan CID file yang sudah ada
        """
        try:
            # Mengambil metadata file untuk mendapatkan CID
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=filename)
            cid = response.get('Metadata', {}).get('cid') or response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amz-meta-cid')
            
            if cid:
                return f"{self.gateway_url}/{cid}"
            return None
        except ClientError as e:
            print(f"Error fetching CID: {e}")
            return None

    def list_files_by_prefix(self, prefix: str) -> List[str]:
        """
        List semua file dengan prefix tertentu
        Returns: List of S3 keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except ClientError as e:
            print(f"Error listing files: {e}")
            return []

    def delete_files_by_prefix(self, prefix: str) -> bool:
        """
        Delete semua file dengan prefix tertentu
        Returns: True if success, False if failed
        """
        try:
            files = self.list_files_by_prefix(prefix)
            
            if not files:
                return True
            
            # Delete objects satu per satu
            for file_key in files:
                self.delete_file(file_key)
            
            return True
        except ClientError as e:
            print(f"Error deleting files by prefix: {e}")
            return False

s3_service = S3Service()