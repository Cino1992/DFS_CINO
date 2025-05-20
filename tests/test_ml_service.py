import pytest
from unittest.mock import patch, MagicMock
from app.core.ml_service import MLServiceClient


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "is_deepfake": True,
        "confidence_score": 0.85,
        "features": {
            "spectral_features": {
                "centroid": 3000,
                "bandwidth": 2000,
                "rolloff": 0.8
            }
        },
        "processing_time": 1.5
    }
    return mock


def test_process_audio(mock_response):
    with patch('app.core.ml_service.GCStorage.get_signed_url') as mock_get_url:
        with patch('app.core.ml_service.requests.post') as mock_post:
            # Set up mocks
            mock_get_url.return_value = "https://example.com/signed-url"
            mock_post.return_value = mock_response

            # Call the function
            result = MLServiceClient.process_audio("test/path.wav", "audio/wav")

            # Check the result
            assert result["is_deepfake"] is True
            assert result["confidence_score"] == 0.85
            assert "processing_time" in result
            assert "spectral_features" in result["features"]

            # Verify mocks were called correctly
            mock_get_url.assert_called_once_with("test/path.wav")
            mock_post.assert_called_once()


def test_health_check_success():
    with patch('app.core.ml_service.requests.get') as mock_get:
        # Set up mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Call the function
        result = MLServiceClient.health_check()

        # Check the result
        assert result is True

        # Verify mock was called correctly
        mock_get.assert_called_once()


def test_health_check_failure():
    with patch('app.core.ml_service.requests.get') as mock_get:
        # Set up mock to raise exception
        mock_get.side_effect = Exception("Connection error")

        # Call the function
        result = MLServiceClient.health_check()

        # Check the result
        assert result is False

        # Verify mock was called correctly
        mock_get.assert_called_once()