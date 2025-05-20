# app/main.py
from flask import Flask
from flask_cors import CORS
import os
from app.api.routes import api_bp
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Enable CORS for frontend integration
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Simple root route
    @app.route('/')
    def home():
        return {
            'name': 'Deepfake Speech Detection API',
            'version': '1.0.0',
            'status': 'running'
        }

    return app


app = create_app()

if __name__ == '__main__':
    # Get port from environment (for Heroku compatibility)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    