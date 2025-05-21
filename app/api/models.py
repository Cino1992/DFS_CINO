from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase):
    id: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AudioFileBase(BaseModel):
    filename: str
    file_type: str


class AudioFileCreate(AudioFileBase):
    pass


class AudioFileInDB(AudioFileBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    gcs_path: str
    public_url: HttpUrl
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AudioFile(AudioFileBase):
    id: str
    user_id: str
    public_url: HttpUrl
    created_at: datetime


class DetectionBase(BaseModel):
    audio_file_id: str


class DetectionCreate(DetectionBase):
    pass


class DetectionInDB(DetectionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    is_deepfake: bool
    confidence_score: float
    features: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float  # Time taken to process in seconds


class Detection(DetectionBase):
    id: str
    user_id: str
    is_deepfake: bool
    confidence_score: float
    created_at: datetime
    processing_time: float


class DetectionResult(BaseModel):
    is_deepfake: bool
    confidence_score: float
    features: Dict[str, Any]
    processing_time: float