from storages.backends.s3boto3 import S3Boto3Storage

class CustomStorage(S3Boto3Storage):
    bucket_name = "media"
    custom_domain = f"http://minIo_on_demand:9000/{bucket_name}"
    file_overwrite = False
