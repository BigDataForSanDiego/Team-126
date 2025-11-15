-- Initialize pgvector and PostGIS extensions
-- This script runs automatically when the Docker container is first created

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable PostGIS extension for geospatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify extensions are loaded
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'postgis');
