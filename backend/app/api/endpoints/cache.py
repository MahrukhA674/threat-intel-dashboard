from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..db.database import get_db
from ..services.auth_service import AuthService
from ..services.cache_service import CacheService
from ..schemas.schemas import CacheInfo, CacheStatus

router = APIRouter()

@router.get("/info", response_model=CacheStatus)
async def get_cache_info(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> CacheStatus:
    """Get cache statistics and information."""
    cache_service = CacheService(db)
    return await cache_service.get_cache_info()

@router.post("/refresh")
async def refresh_cache(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> Dict[str, str]:
    """Manually refresh all cached data."""
    cache_service = CacheService(db)
    await cache_service.refresh_cache()
    return {"message": "Cache refreshed successfully"}

@router.delete("/invalidate")
async def invalidate_cache(
    pattern: str = Query(None, description="Cache key pattern to invalidate"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> Dict[str, str]:
    """Invalidate cache by pattern."""
    cache_service = CacheService(db)
    await cache_service.invalidate_cache(pattern)
    return {"message": f"Cache invalidated successfully for pattern: {pattern if pattern else 'all'}"}
