#!/bin/bash

# Deploy to Google Cloud Run
# Prerequisites: Google Cloud SDK installed and configured

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="deepfake-speech-backend"
REGION="us-central1"
GCS_BUCKET="your-gcs-bucket"
MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/deepfake_speech"
ML_SERVICE_URL="https://your-ml-service-url"
ML_SERVICE_API_KEY="your-ml-service-api-key"
SECRET_KEY="your-secret-key"

# Build the container
echo "Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="DEBUG=False,GCS_BUCKET=$GCS_BUCKET,MONGO_URI=$MONGO_URI,MONGO_DB_NAME=deepfake_speech,ML_SERVICE_URL=$ML_SERVICE_URL,ML_SERVICE_API_KEY=$ML_SERVICE_API_KEY,SECRET_KEY=$SECRET_KEY"

echo "Deployment complete!"