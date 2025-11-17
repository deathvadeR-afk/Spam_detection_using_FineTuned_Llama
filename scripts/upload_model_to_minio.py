import os
import logging
from minio import Minio
from minio.error import S3Error

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_model_to_minio(model_directory: str = "./model"):
    """Upload the model files to MinIO storage"""
    try:
        # MinIO configuration from environment variables
        minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        minio_bucket = os.getenv('MINIO_BUCKET', 'models')
        
        logger.info(f"Connecting to MinIO at {minio_endpoint}")
        
        # Create MinIO client
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False  # Set to True for HTTPS
        )
        
        # Create bucket if it doesn't exist
        found = client.bucket_exists(minio_bucket)
        if not found:
            client.make_bucket(minio_bucket)
            logger.info(f"Created bucket: {minio_bucket}")
        else:
            logger.info(f"Bucket {minio_bucket} already exists")
        
        # Upload all files in the model directory
        if not os.path.exists(model_directory):
            logger.error(f"Model directory {model_directory} does not exist")
            return False
            
        for root, dirs, files in os.walk(model_directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate the relative path to maintain directory structure
                relative_path = os.path.relpath(file_path, model_directory)
                object_name = relative_path.replace("\\", "/")  # Use forward slashes for MinIO
                
                logger.info(f"Uploading {file_path} as {object_name}")
                client.fput_object(minio_bucket, object_name, file_path)
        
        logger.info("Model files uploaded successfully!")
        return True
        
    except S3Error as e:
        logger.error(f"MinIO S3 error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error uploading model to MinIO: {e}")
        return False

if __name__ == "__main__":
    success = upload_model_to_minio()
    if success:
        print("Model upload completed successfully!")
    else:
        print("Model upload failed!")