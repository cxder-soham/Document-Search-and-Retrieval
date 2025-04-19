import boto3
import uuid
from botocore.exceptions import ClientError

class Storage:
    def __init__(self, bucket_name):
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

    def upload_file(self, file):
        try:
            doc_id = str(uuid.uuid4())
            self.s3.upload_fileobj(file, self.bucket_name, doc_id)
            return doc_id
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {e}")