from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..db.database import get_db
from ..services.auth_service import AuthService
from ..services.cache_service import CacheService
from ..schemas.schemas import DashboardStats, ThreatIntelResponse

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> DashboardStats:
    """Get dashboard statistics."""
    cache_service = CacheService(db)
    
    # Get all stats concurrently
    stats = await cache_service.get_dashboard_stats()
    recent_threats = await cache_service.get_recent_threats()
    severity_distribution = await cache_service.get_severity_stats()
    threat_types_distribution = await cache_service.get_threat_type_stats()
    
    return DashboardStats(
        total_cves=stats["total_cves"],
        total_ip_threats=stats["total_ip_threats"],
        total_otx_threats=stats["total_otx_threats"],
        recent_threats=recent_threats,
        severity_distribution=severity_distribution,
        threat_types_distribution=threat_types_distribution
    )

@router.get("/recent-threats", response_model=List[ThreatIntelResponse])
async def get_recent_threats(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> List[ThreatIntelResponse]:
    """Get recent threats."""
    cache_service = CacheService(db)
    return await cache_service.get_recent_threats()

@router.get("/severity-distribution")
async def get_severity_distribution(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> Dict[str, int]:
    """Get severity distribution stats."""
    cache_service = CacheService(db)
    return await cache_service.get_severity_stats()

@router.get("/threat-types-distribution")
async def get_threat_types_distribution(
    db: Session = Depends(get_db),
    current_user: Any = Depends(AuthService.get_current_user)
) -> Dict[str, int]:
    """Get threat type distribution stats."""
    cache_service = CacheService(db)
    return await cache_service.get_threat_type_stats()
