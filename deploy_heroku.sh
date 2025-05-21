#!/bin/bash

# Deploy to Heroku
# Prerequisites: Heroku CLI installed and logged in

# Configuration
HEROKU_APP_NAME="your-heroku-app-name"
GCS_BUCKET="your-gcs-bucket"
MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/deepfake_speech"
ML_SERVICE_URL="https://your-ml-service-url"
ML_SERVICE_API_KEY="your-ml-service-api-key"
SECRET_KEY="your-secret-key"

# Create Heroku app if it doesn't exist
heroku apps:info $HEROKU_APP_NAME > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Creating Heroku app $HEROKU_APP_NAME..."
  heroku create $HEROKU_APP_NAME
else
  echo "Heroku app $HEROKU_APP_NAME already exists."
fi

# Set environment variables
echo "Setting environment variables..."
heroku config:set \
  DEBUG=False \
  GCS_BUCKET=$GCS_BUCKET \
  MONGO_URI=$MONGO_URI \
  MONGO_DB_NAME=deepfake_speech \
  ML_SERVICE_URL=$ML_SERVICE_URL \
  ML_SERVICE_API_KEY=$ML_SERVICE_API_KEY \
  SECRET_KEY=$SECRET_KEY \
  --app $HEROKU_APP_NAME

# Deploy to Heroku
echo "Deploying to Heroku..."
git push heroku main

echo "Deployment complete!"