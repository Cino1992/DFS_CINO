from pymongo import MongoClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client = None
    db = None

    @classmethod
    def connect(cls):
        try:
            cls.client = MongoClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB_NAME]
            logger.info("Connected to MongoDB")
            return cls.db
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    @classmethod
    def get_db(cls):
        if cls.db is None:
            return cls.connect()
        return cls.db


# Collections
def get_users_collection():
    db = MongoDB.get_db()
    return db.users


def get_audio_files_collection():
    db = MongoDB.get_db()
    return db.audio_files


def get_detections_collection():
    db = MongoDB.get_db()
    return db.detections