from decouple import config

STATICFILES_STORAGE = 'pfitz_api.storage_classes.StaticRootS3Boto3Storage'
DEFAULT_FILE_STORAGE = 'pfitz_api.storage_classes.MediaRootS3Boto3Storage'

AWS_S3_ACCESS_KEY_ID=config("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY=config("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME=config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL=config("AWS_S3_ENDPOINT_URL")