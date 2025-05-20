from fastapi import HTTPException, status
from typing import List, Optional
import re


def validate_audio_file(content_type: str, file_size: int) -> None:
    """Validate audio file type and size"""
    # Check file type
    allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/x-wav"]
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be one of the following formats: WAV, MP3"
        )

    # Check file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds 10MB limit. Got {file_size / (1024 * 1024):.2f}MB"
        )


def validate_email(email: str) -> None:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )


def validate_password(password: str) -> None:
    """Validate password strength"""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )