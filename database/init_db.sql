-- Create tables for Smart Helmet DB

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_uid VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    owner_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS violations (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    violation_type VARCHAR(50) NOT NULL, -- e.g., 'NO_HELMET', 'TRIPLE_RIDING'
    confidence_score FLOAT,
    location_lat FLOAT,
    location_lon FLOAT,
    violation_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    violation_id INTEGER REFERENCES violations(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- e.g., 'IMAGE', 'VIDEO'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    violation_id INTEGER REFERENCES violations(id),
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, SENT, FAILED
    email_sent_to VARCHAR(100),
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert dummy device for testing
INSERT INTO devices (device_uid, description) VALUES ('TEST-HELMET-001', 'Test Edge Node') ON CONFLICT DO NOTHING;
