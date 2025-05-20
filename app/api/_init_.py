from fastapi import APIRouter
from app.api.routes import router as api_router

router = APIRouter()
router.include_router(api_router, prefix="/api/v1")

__all__ = ['router']