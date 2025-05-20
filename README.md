# Deepfake Speech Detection Backend

This is the backend API service for the Deepfake Speech Detection application, built with FastAPI, MongoDB, and Google Cloud Storage.

## Architecture

The application follows a microservices architecture:

1. **FastAPI Backend (this service)** - Handles user authentication, file uploads, and orchestrates the detection process
2. **ML Service** - Flask application built by the ML engineer for running deepfake detection algorithms
3. **MongoDB** - Database for storing user data, audio files metadata, and detection results
4. **Google Cloud Storage** - For storing the audio files

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- MongoDB
- Google Cloud SDK (for GCS access)

### Local Development

1. Clone the repository: