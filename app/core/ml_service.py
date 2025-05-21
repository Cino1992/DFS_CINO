import requests
import logging
import json
import os
import tempfile
import time
from typing import Dict, Any, Optional
from app.config import settings
from app.storage.google_buckets_gcs import GCStorage

logger = logging.getLogger(__name__)


class MLServiceClient:
    """Client for interacting with the ML service (Flask app) from the ML engineer"""

    @staticmethod
    def process_audio(gcs_path: str, audio_type: str) -> Dict[str, Any]:
        """
        Send an audio file to the ML service for processing

        Args:
            gcs_path: Path to the audio file in Google Cloud Storage
            audio_type: MIME type of the audio file

        Returns:
            Dictionary with prediction results
        """
        start_time = time.time()

        try:
            # Generate a signed URL for the ML service to access the file
            signed_url = GCStorage.get_signed_url(gcs_path)

            # Prepare the request to the ML service
            url = f"{settings.ML_SERVICE_URL}/api/predict"
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": settings.ML_SERVICE_API_KEY
            }
            payload = {
                "audio_url": signed_url,
                "audio_type": audio_type
            }

            # Send the request to the ML service
            logger.info(f"Sending request to ML service: {url}")
            response = requests.post(url, headers=headers, json=payload)

            # Check if the request was successful
            if response.status_code != 200:
                logger.error(f"ML service returned error: {response.status_code} - {response.text}")
                raise Exception(f"ML service returned error: {response.status_code}")

            # Parse the response
            result = response.json()

            # Calculate processing time
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time

            logger.info(f"ML service processed audio in {processing_time:.2f} seconds")
            return result

        except Exception as e:
            logger.error(f"Error processing audio with ML service: {str(e)}")
            # Return a fallback result in case of error
            return {
                "is_deepfake": False,
                "confidence_score": 0.0,
                "features": {},
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    @staticmethod
    def health_check() -> bool:
        """Check if the ML service is up and running"""
        try:
            url = f"{settings.ML_SERVICE_URL}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"ML service health check failed: {str(e)}")
            return False