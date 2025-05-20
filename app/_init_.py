import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.db.mongo_client import MongoDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Create FastAPI app
app = FastAPI(
    title="Deepfake Speech Detection API",
    description="Backend API for detecting deepfake speech in audio files",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Connect to MongoDB on startup
@app.on_event("startup")
async def startup_db_client():
    MongoDB.connect()
    logging.info("Application startup: Connected to MongoDB")

# Close MongoDB connection on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    if MongoDB.client:
        MongoDB.client.close()
        logging.info("Application shutdown: Closed MongoDB connection")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}