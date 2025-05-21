# app/core/model_handler.py
import os
import joblib
import logging
import numpy as np
import tempfile
from app.storage.google_buckets_gcs import gcs_client

logger = logging.getLogger(__name__)


class ModelHandler:
    def __init__(self):
        """Initialize the model handler"""
        self.model_path = os.environ.get('MODEL_PATH', 'models/xgboost_model.pkl')
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the XGBoost model"""
        try:
            # Check if model exists locally
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            else:
                # Download from GCS if not local
                logger.info("Model not found locally, downloading from GCS")
                temp_model_path = tempfile.mktemp()
                gcs_client.download_file(self.model_path, temp_model_path)
                self.model = joblib.load(temp_model_path)
                os.remove(temp_model_path)
                logger.info(f"Loaded model from GCS: {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def predict(self, features):
        """
        Make a prediction using the model

        Args:
            features: Extracted acoustic features

        Returns:
            prediction: 'real' or 'fake'
            confidence: Confidence score
        """
        try:
            # Reshape features if needed
            if features.ndim == 1:
                features = features.reshape(1, -1)

            # Make prediction using the XGBoost model
            proba = self.model.predict_proba(features)[0]
            prediction = 'fake' if proba[1] > 0.5 else 'real'
            confidence = proba[1] if prediction == 'fake' else proba[0]

            return prediction, float(confidence)
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise