from decouple import config

STATICFILES_STORAGE = 'pfitz_api.storage_classes.StaticRootS3Boto3Storage'
DEFAULT_FILE_STORAGE = 'pfitz_api.storage_classes.MediaRootS3Boto3Storage'

AWS_S3_ACCESS_KEY_ID=config("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY=config("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME=config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME=config("AWS_S3_REGION_NAME")
# cloudfront url
AWS_S3_CUSTOM_DOMAIN=config("AWS_S3_CUSTOM_DOMAIN")