import boto3
from botocore.exceptions import NoCredentialsError

import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_s3(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True


def upload_organization_file(file_name, org_id):
    bucket = 'your-s3-bucket-name'
    object_name = f'{org_id}/{file_name}'
    return upload_to_s3(file_name, bucket, object_name)

def list_org_files(bucket, org_id):
    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # List objects within the specified prefix
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=f'{org_id}/')
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
    except NoCredentialsError:
        print("Credentials not available")
        return []
