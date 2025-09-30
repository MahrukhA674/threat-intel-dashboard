from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class CVE(Base):
    __tablename__ = "cves"

    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), unique=True, index=True)
    description = Column(Text)
    severity = Column(String(20))
    cvss_score = Column(String(4))
    published_date = Column(DateTime)
    last_modified_date = Column(DateTime)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IPThreat(Base):
    __tablename__ = "ip_threats"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), index=True)  # Support both IPv4 and IPv6
    confidence_score = Column(Integer)
    is_public = Column(Boolean, default=True)
    abuse_types = Column(JSON)  # Array of abuse types
    total_reports = Column(Integer, default=0)
    last_reported_at = Column(DateTime)
    country_code = Column(String(2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OTXThreat(Base):
    __tablename__ = "otx_threats"

    id = Column(Integer, primary_key=True, index=True)
    pulse_id = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    author_name = Column(String(255))
    tlp = Column(String(10))  # Traffic Light Protocol level
    tags = Column(JSON)  # Array of tags
    indicators = Column(JSON)  # Array of indicators
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    references = Column(JSON)  # Array of reference URLs

class ThreatIntel(Base):
    __tablename__ = "threat_intel"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))  # 'cve', 'abuseipdb', 'otx'
    source_id = Column(String(255), index=True)  # ID from the source system
    threat_type = Column(String(50))
    severity = Column(String(20))
    confidence = Column(Integer)
    raw_data = Column(JSON)  # Store complete raw data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
