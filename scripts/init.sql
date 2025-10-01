IF NOT EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = N'threat_intel_db')
BEGIN
  CREATE DATABASE [threat_intel_db];
END;
GO

USE [threat_intel_db];
GO
-- USERS TABLE
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) UNIQUE NOT NULL,
    email NVARCHAR(255) UNIQUE,
    hashed_password NVARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1,
    is_admin BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_users_username ON users(username);

-- CVE DATA TABLE
CREATE TABLE cve_data (
    id NVARCHAR(50) PRIMARY KEY,
    description NVARCHAR(MAX),
    severity NVARCHAR(20),
    cvss_score DECIMAL(3,1),
    published_date DATETIME,
    last_modified DATETIME,
    references NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_cve_severity ON cve_data(severity);
CREATE INDEX idx_cve_cvss_score ON cve_data(cvss_score DESC);

-- IP THREATS TABLE
CREATE TABLE ip_threats (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ip_address NVARCHAR(45) UNIQUE NOT NULL,
    abuse_score INT CHECK (abuse_score BETWEEN 0 AND 100),
    country NVARCHAR(10),
    usage_type NVARCHAR(100),
    isp NVARCHAR(255),
    total_reports INT DEFAULT 0,
    last_reported DATETIME,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_ip_address ON ip_threats(ip_address);
CREATE INDEX idx_ip_abuse_score ON ip_threats(abuse_score DESC);

-- OTX PULSES TABLE
CREATE TABLE otx_pulses (
    id NVARCHAR(100) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX),
    author NVARCHAR(255),
    created DATETIME,
    modified DATETIME,
    tags NVARCHAR(MAX),
    tlp NVARCHAR(20),
    indicator_count INT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_otx_created ON otx_pulses(created DESC);

-- FEED STATUS TABLE
CREATE TABLE feed_status (
    feed_name NVARCHAR(100) PRIMARY KEY,
    last_update DATETIME,
    status NVARCHAR(50),
    record_count INT DEFAULT 0,
    error_message NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- ACTIVE SESSIONS TABLE
CREATE TABLE active_sessions (
    session_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id INT FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE,
    token_hash NVARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    last_accessed DATETIME DEFAULT GETDATE(),
    ip_address NVARCHAR(45),
    user_agent NVARCHAR(MAX)
);

CREATE INDEX idx_sessions_token_hash ON active_sessions(token_hash);
CREATE INDEX idx_sessions_user_id ON active_sessions(user_id);

-- TRIGGERS TO UPDATE updated_at
CREATE TRIGGER trg_update_users_timestamp
ON users
AFTER UPDATE
AS
BEGIN
    UPDATE users SET updated_at = GETDATE()
    FROM inserted WHERE users.id = inserted.id;
END;

CREATE TRIGGER trg_update_cve_data_timestamp
ON cve_data
AFTER UPDATE
AS
BEGIN
    UPDATE cve_data SET updated_at = GETDATE()
    FROM inserted WHERE cve_data.id = inserted.id;
END;

CREATE TRIGGER trg_update_ip_threats_timestamp
ON ip_threats
AFTER UPDATE
AS
BEGIN
    UPDATE ip_threats SET updated_at = GETDATE()
    FROM inserted WHERE ip_threats.id = inserted.id;
END;

CREATE TRIGGER trg_update_otx_pulses_timestamp
ON otx_pulses
AFTER UPDATE
AS
BEGIN
    UPDATE otx_pulses SET updated_at = GETDATE()
    FROM inserted WHERE otx_pulses.id = inserted.id;
END;

-- INSERT DEFAULT ADMIN USER
INSERT INTO users (username, email, hashed_password, is_admin)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$hashedpasswordgoeshere',  -- Replace with bcrypt hash
    1
);
