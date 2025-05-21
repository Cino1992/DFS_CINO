from flask import Flask, request, jsonify
import random
import time
import requests
import logging

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})


@app.route('/api/predict', methods=['POST'])
def predict():
    # Log the request
    app.logger.info("Received prediction request")

    # Get request data
    data = request.json
    if not data or 'audio_url' not in data:
        return jsonify({"error": "Missing audio_url parameter"}), 400

    # Simulate processing delay (1-3 seconds)
    processing_time = random.uniform(1, 3)
    time.sleep(processing_time)

    # Simulate downloading the audio from the signed URL
    audio_url = data.get('audio_url')
    try:
        # Just check if the URL is accessible, don't actually download the file
        # In a real scenario, this would download and process the file
        response = requests.head(audio_url, timeout=5)
        if response.status_code != 200:
            return jsonify({"error": f"Could not access audio file: {response.status_code}"}), 400
    except Exception as e:
        app.logger.error(f"Error accessing audio URL: {str(e)}")
        # Continue anyway for testing purposes

    # Generate mock prediction results
    is_deepfake = random.choice([True, False])
    confidence = random.uniform(0.6, 0.98)

    # Create mock features
    features = {
        "spectral_features": {
            "centroid": random.uniform(1000, 5000),
            "bandwidth": random.uniform(1000, 3000),
            "rolloff": random.uniform(0.6, 0.95)
        },
        "temporal_features": {
            "zero_crossing_rate": random.uniform(0.01, 0.2),
            "rms_energy": random.uniform(0.1, 0.9)
        },
        "voice_features": {
            "pitch_mean": random.uniform(80, 400),
            "pitch_variance": random.uniform(10, 100),
            "harmonics_to_noise": random.uniform(5, 20)
        }
    }

    # Return prediction results
    result = {
        "is_deepfake": is_deepfake,
        "confidence_score": confidence,
        "features": features,
        "processing_time": processing_time
    }

    app.logger.info(f"Prediction result: deepfake={is_deepfake}, confidence={confidence:.2f}")
    return jsonify(result)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host='0.0.0.0', port=5000)