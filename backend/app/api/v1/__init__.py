from fastapi import APIRouter
from app.api.v1.endpoints import auth, diagnose, balance, outbreaks, history

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(diagnose.router)
api_router.include_router(balance.router)
api_router.include_router(outbreaks.router)
api_router.include_router(history.router)
