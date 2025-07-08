-- Initialize database with required extensions and configurations
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (add your specific indexes here)
-- Example: CREATE INDEX IF NOT EXISTS idx_academic_program_code ON academic_program(code);

-- Set timezone
SET timezone = 'UTC';
