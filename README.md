This ia an AI mobile application to detect Deepfake Speech from audios. 

This is the backend API service for the Deepfake Speech Detection application, built with FastAPI, MongoDB, and Google Cloud Storage.

## Architecture model 
deepfake_speech_app/
├── app/
│   ├── __init__.py              # Main application entry point
│   ├── config.py                # Configuration settings
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py            # API route definitions
│   │   ├── validators.py        # Request validation
│   │   ├── models.py            # Pydantic models
│   │   └── auth.py              # Authentication logic
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   └── ml_service.py        # ML service client
│   ├── db/                      # Database connections
│   │   ├── __init__.py
│   │   └── mongo_client.py      # MongoDB client setup
│   └── storage/                 # Cloud storage integrations
│       ├── __init__.py
│       └── gcs.py               # Google Cloud Storage client
├── ml-service-mock/             # Mock ML service for development
│   └── app.py                   # Flask app for mock ML service
├── tests/                       # Test suite
│   ├── conftest.py              # Test configuration
│   ├── test_users.py            # User API tests
│   └── test_ml_service.py       # ML service client tests
├── .github/                     # CI/CD configurations
│   └── workflows/
│       └── ci.yml               # GitHub Actions workflow
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Python runtime for Heroku
├── Procfile                     # Heroku deployment configuration
├── deploy-cloud-run.sh          # Google Cloud Run deployment script
├── deploy-heroku.sh             # Heroku deployment script
├── .env.example                 # Example environment variables
└── README.md                    # Project documentation


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
git clone <repository-url>
cd deepfake_speech_app

2. Create a local environment file:
cp .env.example .env

3. Update the environment variables in `.env` as needed.

4. Start the development environment (includes a mock ML service):
docker-compose up --build

5. The API will be available at [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## ML Service Integration

The backend communicates with the ML Service (Flask application built by the ML engineer) through a RESTful API:

1. **Audio File Processing Flow**:
- User uploads audio file to the backend
- Backend stores the file in GCS
- Backend sends a request to the ML Service with a signed URL to access the file
- ML Service processes the audio and returns the detection results
- Backend stores the results in MongoDB

2. **ML Service API**:
- Endpoint: `POST /api/predict`
- Request Format:
  ```json
  {
    "audio_url": "https://storage.googleapis.com/signed-url-to-access-file",
    "audio_type": "audio/wav"
  }
  ```
- Response Format:
  ```json
  {
    "is_deepfake": true,
    "confidence_score": 0.92,
    "features": {
      "spectral_features": { ... },
      "temporal_features": { ... },
      "voice_features": { ... }
    },
    "processing_time": 2.5
  }
  ```

## API Endpoints

### Authentication
- `POST /api/v1/token` - Get access token
- `POST /api/v1/users` - Register new user

### Audio Files
- `POST /api/v1/audio-files` - Upload audio file
- `GET /api/v1/audio-files` - List user's audio files
- `GET /api/v1/audio-files/{file_id}` - Get audio file details

### Detections
- `GET /api/v1/detections` - List user's detection results
- `GET /api/v1/detections/{detection_id}` - Get detection details

### ML Service
- `GET /api/v1/ml-service-health` - Check ML service health

## Deployment

### Google Cloud Run

To deploy to Google Cloud Run:

1. Update the configuration variables in `deploy-cloud-run.sh`
2. Run the script:
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh

### Heroku

To deploy to Heroku:

1. Update the configuration variables in `deploy-heroku.sh`
2. Run the script:
chmod +x deploy-heroku.sh
./deploy-heroku.sh

## Frontend Integration

The frontend application should integrate with this backend through the provided API endpoints. For authentication, use the JWT token flow:

1. Register a user: `POST /api/v1/users`
2. Get access token: `POST /api/v1/token`
3. Include the token in all authenticated requests:
Authorization: Bearer <access_token>

## License

[Specify your license here]
