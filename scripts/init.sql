-- PostgreSQL Database Initialization Script

-- Generate unique UUIDs and secure password hashes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- CVE Data table
CREATE TABLE IF NOT EXISTS cve_data (
    id VARCHAR(50) PRIMARY KEY,
    description TEXT,
    severity VARCHAR(20),
    cvss_score DECIMAL(3,1),
    published_date TIMESTAMP,
    last_modified TIMESTAMP,
    references JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cve_severity ON cve_data(severity);
CREATE INDEX idx_cve_cvss_score ON cve_data(cvss_score DESC);

-- IP Threats table
CREATE TABLE IF NOT EXISTS ip_threats (
    id SERIAL PRIMARY KEY,
    ip_address INET UNIQUE NOT NULL,
    abuse_score INTEGER CHECK (abuse_score >= 0 AND abuse_score <= 100),
    country VARCHAR(10),
    usage_type VARCHAR(100),
    isp VARCHAR(255),
    total_reports INTEGER DEFAULT 0,
    last_reported TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ip_address ON ip_threats(ip_address);
CREATE INDEX idx_ip_abuse_score ON ip_threats(abuse_score DESC);

-- OTX Pulses table
CREATE TABLE IF NOT EXISTS otx_pulses (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    created TIMESTAMP,
    modified TIMESTAMP,
    tags JSONB,
    tlp VARCHAR(20),
    indicator_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otx_created ON otx_pulses(created DESC);

-- Feed Status table
CREATE TABLE IF NOT EXISTS feed_status (
    feed_name VARCHAR(100) PRIMARY KEY,
    last_update TIMESTAMP,
    status VARCHAR(50),
    record_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active Sessions table (for Redis session validation)
CREATE TABLE IF NOT EXISTS active_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_sessions_token_hash ON active_sessions(token_hash);
CREATE INDEX idx_sessions_user_id ON active_sessions(user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cve_data_updated_at BEFORE UPDATE ON cve_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ip_threats_updated_at BEFORE UPDATE ON ip_threats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_otx_pulses_updated_at BEFORE UPDATE ON otx_pulses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
-- Hashed with bcrypt
INSERT INTO users (username, email, hashed_password, is_admin)
VALUES (
    'admin',
    'admin@threatintel.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW7Q3PGrw7YO',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO threat_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO threat_user;
