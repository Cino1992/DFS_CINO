from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List
import io
import time
import logging

from app.api.models import (
    User, UserCreate, AudioFile, AudioFileInDB, Detection,
    DetectionInDB, Token
)
from app.api.auth import (
    authenticate_user, get_password_hash, create_access_token,
    get_current_active_user
)
from app.api.validators import validate_audio_file, validate_email, validate_password
from app.database.mongo_client import (
    get_users_collection, get_audio_files_collection,
    get_detections_collection
)
from app.storage.google_buckets_gcs import GCStorage
from app.core.ml_service import MLServiceClient
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Authentication routes
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User logged in: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    validate_email(user.email)
    validate_password(user.password)

    users_collection = get_users_collection()

    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if users_collection.find_one({"username": user.username}):
        logger.warning(f"Registration attempt with existing username: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user in DB
    hashed_password = get_password_hash(user.password)
    user_in_db = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }

    result = users_collection.insert_one(user_in_db)
    user_id = str(result.inserted_id)
    logger.info(f"New user registered: {user.username} (ID: {user_id})")

    # Return user object (without password)
    return {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "created_at": user_in_db["created_at"]
    }


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# Audio file routes
@router.post("/audio-files", response_model=AudioFile)
async def upload_audio_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_active_user)
):
    # Validate file
    validate_audio_file(file.content_type, file.size)

    # Read file content
    file_content = await file.read()

    # Upload to GCS
    try:
        gcs_result = GCStorage.upload_from_memory(
            file_bytes=file_content,
            original_filename=file.filename,
            destination_folder=f"users/{current_user.id}/audio",
            content_type=file.content_type
        )

        # Store file metadata in MongoDB
        audio_file = AudioFileInDB(
            filename=file.filename,
            file_type=file.content_type,
            user_id=current_user.id,
            gcs_path=gcs_result["path"],
            public_url=gcs_result["url"]
        )

        audio_files_collection = get_audio_files_collection()
        result = audio_files_collection.insert_one(audio_file.dict())
        file_id = str(result.inserted_id)

        logger.info(f"Audio file uploaded: {file.filename} (ID: {file_id}) by user: {current_user.username}")

        # Add background task to process the audio file
        background_tasks.add_task(
            process_audio_file,
            file_id=file_id,
            user_id=current_user.id,
            gcs_path=gcs_result["path"],
            file_type=file.content_type
        )

        return {
            "id": file_id,
            "filename": audio_file.filename,
            "file_type": audio_file.file_type,
            "user_id": audio_file.user_id,
            "public_url": str(audio_file.public_url),
            "created_at": audio_file.created_at
        }
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/audio-files", response_model=List[AudioFile])
async def list_user_audio_files(current_user: User = Depends(get_current_active_user)):
    audio_files_collection = get_audio_files_collection()
    files = audio_files_collection.find({"user_id": current_user.id})

    return [{
        "id": str(file["_id"]),
        "filename": file["filename"],
        "file_type": file["file_type"],
        "user_id": file["user_id"],
        "public_url": file["public_url"],
        "created_at": file["created_at"]
    } for file in files]


@router.get("/audio-files/{file_id}", response_model=AudioFile)
async def get_audio_file(
        file_id: str,
        current_user: User = Depends(get_current_active_user)
):
    audio_files_collection = get_audio_files_collection()
    file = audio_files_collection.find_one({"_id": file_id, "user_id": current_user.id})

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )

    return {
        "id": str(file["_id"]),
        "filename": file["filename"],
        "file_type": file["file_type"],
        "user_id": file["user_id"],
        "public_url": file["public_url"],
        "created_at": file["created_at"]
    }


# Detection routes
@router.get("/detections", response_model=List[Detection])
async def list_user_detections(current_user: User = Depends(get_current_active_user)):
    detections_collection = get_detections_collection()
    detections = detections_collection.find({"user_id": current_user.id})

    return [{
        "id": str(detection["_id"]),
        "audio_file_id": detection["audio_file_id"],
        "user_id": detection["user_id"],
        "is_deepfake": detection["is_deepfake"],
        "confidence_score": detection["confidence_score"],
        "created_at": detection["created_at"],
        "processing_time": detection.get("processing_time", 0.0)
    } for detection in detections]


@router.get("/detections/{detection_id}", response_model=Detection)
async def get_detection(
        detection_id: str,
        current_user: User = Depends(get_current_active_user)
):
    detections_collection = get_detections_collection()
    detection = detections_collection.find_one({"_id": detection_id, "user_id": current_user.id})

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )

    return {
        "id": str(detection["_id"]),
        "audio_file_id": detection["audio_file_id"],
        "user_id": detection["user_id"],
        "is_deepfake": detection["is_deepfake"],
        "confidence_score": detection["confidence_score"],
        "created_at": detection["created_at"],
        "processing_time": detection.get("processing_time", 0.0)
    }


# ML service health check endpoint
@router.get("/ml-service-health")
async def check_ml_service_health(current_user: User = Depends(get_current_active_user)):
    is_healthy = MLServiceClient.health_check()
    return {"status": "ok" if is_healthy else "error"}


# Background task for processing audio files
def process_audio_file(file_id: str, user_id: str, gcs_path: str, file_type: str):
    """Process audio file in the background by sending it to the ML service"""
    logger.info(f"Processing audio file: {file_id}")
    try:
        # Call the ML service
        prediction = MLServiceClient.process_audio(gcs_path, file_type)

        # Store detection results
        detection = DetectionInDB(
            audio_file_id=file_id,
            user_id=user_id,
            is_deepfake=prediction["is_deepfake"],
            confidence_score=prediction["confidence_score"],
            features=prediction["features"],
            processing_time=prediction.get("processing_time", 0.0)
        )

        # Save to MongoDB
        detections_collection = get_detections_collection()
        result = detections_collection.insert_one(detection.dict())
        detection_id = str(result.inserted_id)

        logger.info(f"Detection completed: {detection_id} for file: {file_id}")

    except Exception as e:
        logger.error(f"Error processing audio file {file_id}: {str(e)}")
        # Log the error but don't raise it since this is a background task