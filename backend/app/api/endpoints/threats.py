from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.services.feed_service import FeedService
from app.services.cache_service import CacheService
#from app.schemas.schemas import (
##    CVEResponse,
#    IPThreatResponse,
#    OTXThreatResponse,
 #   ThreatIntelResponse
#)
#from app.models import ThreatIntel  # Corrected import for the ThreatIntel model

#router = APIRouter()

#@router.get("/cves", response_model=List[CVEResponse])
#async def get_cves(
#    severity: Optional[str] = Query(None),
#    limit: int = Query(10, ge=1, le=100),
#    skip: int = Query(0, ge=0),
#    db: Session = Depends(get_db),
#   # current_user: Any = Depends(AuthService.get_current_user)
#) -> List[CVEResponse]:
#    """Get CVE threats with optional filtering."""
#    query = db.query(CVE)
#    if severity:
#        query = query.filter(CVE.severity == severity.upper())
#    return query.offset(skip).limit(limit).all()

#@router.get("/ip-threats", response_model=List[IPThreatResponse])
#async def get_ip_threats(
#    confidence_min: Optional[int] = Query(None, ge=0, le=100),
#    country_code: Optional[str] = Query(None),
#    limit: int = Query(10, ge=1, le=100),
#    skip: int = Query(0, ge=0),
#    db: Session = Depends(get_db),
  #  current_user: Any = Depends(AuthService.get_current_user)
#) -> List[IPThreatResponse]:
#    """Get IP threats with optional filtering."""
#    query = db.query(IPThreat)
#    if confidence_min is not None:
#        query = query.filter(IPThreat.confidence_score >= confidence_min)
#    if country_code:
#        query = query.filter(IPThreat.country_code == country_code.upper())
#    return query.offset(skip).limit(limit).all()

#@router.get("/otx-threats", response_model=List[OTXThreatResponse])
#async def get_otx_threats(
#    tag: Optional[str] = Query(None),
#    tlp: Optional[str] = Query(None),
#    limit: int = Query(10, ge=1, le=100),
#    skip: int = Query(0, ge=0),
#    db: Session = Depends(get_db),
  #  current_user: Any = Depends(AuthService.get_current_user)
#) -> List[OTXThreatResponse]:
#    """Get OTX threats with optional filtering."""
#    query = db.query(OTXThreat)
#    if tag:
#        query = query.filter(OTXThreat.tags.contains([tag]))
#    if tlp:
#        query = query.filter(OTXThreat.tlp == tlp.lower())
#    return query.offset(skip).limit(limit).all()

#@router.post("/refresh-feeds")
#async def refresh_threat_feeds(
#    db: Session = Depends(get_db),
  #  current_user: Any = Depends(AuthService.get_current_user)
#) -> dict:
#    """Manually trigger feed refresh."""
#    cache_service = CacheService(db)
#    feed_service = FeedService(db, cache_service)
    
 #   try:
#        results = await feed_service.ingest_feeds()
#        return {
#            "message": "Feed refresh completed successfully",
#            "results": results
#        }
#    except Exception as e:
#        raise HTTPException(
#            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#            detail=str(e)
#        )

#@router.get("/search", response_model=List[ThreatIntelResponse])
#async def search_threats(
#    query: str = Query(..., min_length=3),
#    source: Optional[str] = Query(None),
#    limit: int = Query(10, ge=1, le=100),
#    db: Session = Depends(get_db),
  #  current_user: Any = Depends(AuthService.get_current_user)
#) -> List[ThreatIntelResponse]:
#    """Search across all threat types."""
#    search_query = db.query(ThreatIntel)
    
#    if source:
#        search_query = search_query.filter(ThreatIntel.source == source)
    
    # Add full-text search conditions based on the query
#    search_query = search_query.filter(
#        or_(
 #           ThreatIntel.raw_data['description'].astext.ilike(f"%{query}%"),
 #           ThreatIntel.raw_data['name'].astext.ilike(f"%{query}%"),
 #           ThreatIntel.source_id.ilike(f"%{query}%")
 #       )
 #   )
    
 #   return search_query.limit(limit).all()
