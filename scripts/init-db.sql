-- Initialize SOPA database with required extensions and configurations

-- Create the database if it doesn't exist (PostgreSQL will handle this via POSTGRES_DB env var)
-- This script runs after the database is created

-- Create required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create basic configuration
DO $$ 
BEGIN
    RAISE NOTICE 'SOPA Database initialized successfully!';
END $$;
