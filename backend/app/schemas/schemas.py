from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# CVE schemas
class CVEBase(BaseModel):
    cve_id: str
    description: str
    severity: str
    cvss_score: str
    published_date: datetime
    last_modified_date: datetime
    references: List[str]

class CVECreate(CVEBase):
    pass

class CVEResponse(CVEBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# IP Threat schemas
class IPThreatBase(BaseModel):
    ip_address: str
    confidence_score: int
    is_public: bool
    abuse_types: List[str]
    total_reports: int
    last_reported_at: Optional[datetime]
    country_code: str

class IPThreatCreate(IPThreatBase):
    pass

class IPThreatResponse(IPThreatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# OTX Threat schemas
class OTXThreatBase(BaseModel):
    pulse_id: str
    name: str
    description: str
    author_name: str
    tlp: str
    tags: List[str]
    indicators: List[Dict[str, Any]]
    references: List[str]

class OTXThreatCreate(OTXThreatBase):
    pass

class OTXThreatResponse(OTXThreatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Generic Threat Intel schemas
class ThreatIntelBase(BaseModel):
    source: str
    source_id: str
    threat_type: str
    severity: str
    confidence: int
    raw_data: Dict[str, Any]

class ThreatIntelCreate(ThreatIntelBase):
    pass

class ThreatIntelResponse(ThreatIntelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_cves: int
    total_ip_threats: int
    total_otx_threats: int
    recent_threats: List[ThreatIntelResponse]
    severity_distribution: Dict[str, int]
    threat_types_distribution: Dict[str, int]

# Cache Management schemas
class CacheInfo(BaseModel):
    key: str
    ttl: int
    size: int
    last_updated: datetime

class CacheStatus(BaseModel):
    total_keys: int
    memory_usage: float
    cache_hits: int
    cache_misses: int
