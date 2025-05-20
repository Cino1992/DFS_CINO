from google.cloud import storage
from app.config import settings
import uuid
import os
import logging

logger = logging.getLogger(__name__)


class GCStorage:
    client = None
    bucket = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            cls.client = storage.Client()
        return cls.client

    @classmethod
    def get_bucket(cls):
        if cls.bucket is None:
            client = cls.get_client()
            cls.bucket = client.bucket(settings.GCS_BUCKET)
        return cls.bucket

    @classmethod
    def upload_file(cls, file_path, destination_folder="uploads"):
        """Upload a file to GCS bucket"""
        try:
            bucket = cls.get_bucket()
            file_name = os.path.basename(file_path)
            unique_filename = f"{destination_folder}/{uuid.uuid4().hex}_{file_name}"

            blob = bucket.blob(unique_filename)
            blob.upload_from_filename(file_path)

            # Make the blob publicly viewable
            blob.make_public()

            logger.info(f"File uploaded to GCS: {unique_filename}")
            return {
                "url": blob.public_url,
                "path": unique_filename
            }
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {e}")
            raise

    @classmethod
    def upload_from_memory(cls, file_bytes, original_filename, destination_folder="uploads", content_type=None):
        """Upload bytes to GCS bucket"""
        try:
            bucket = cls.get_bucket()
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{destination_folder}/{uuid.uuid4().hex}{file_extension}"

            blob = bucket.blob(unique_filename)
            blob.upload_from_string(file_bytes, content_type=content_type)

            # Make the blob publicly viewable
            blob.make_public()

            logger.info(f"File uploaded to GCS from memory: {unique_filename}")
            return {
                "url": blob.public_url,
                "path": unique_filename
            }
        except Exception as e:
            logger.error(f"Error uploading bytes to GCS: {e}")
            raise

    @classmethod
    def download_file(cls, gcs_path, local_destination):
        """Download a file from GCS bucket"""
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(gcs_path)
            blob.download_to_filename(local_destination)
            logger.info(f"File downloaded from GCS: {gcs_path} to {local_destination}")
            return local_destination
        except Exception as e:
            logger.error(f"Error downloading file from GCS: {e}")
            raise

    @classmethod
    def get_signed_url(cls, gcs_path, expiration=3600):
        """Generate a signed URL for a file that expires after a specified time"""
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(gcs_path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            return url
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            raise