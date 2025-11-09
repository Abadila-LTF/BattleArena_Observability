-- BattleArena Database Initialization
-- This script runs when PostgreSQL container starts for the first time

-- Create database if it doesn't exist (though docker-compose already does this)
-- The actual table creation is handled by SQLAlchemy in the application

-- Optional: Set timezone for consistent timestamps
SET timezone = 'UTC';

-- Optional: Create any initial configuration if needed
-- (Currently handled by the application)
