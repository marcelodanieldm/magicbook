-- MagicBook workflow schema (PostgreSQL)
-- Matches the 3-table structure requested for 16-step orchestration.

-- Enable UUID generation if needed.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main container: projects
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  niche TEXT,
  target_country TEXT,
  target_audience TEXT,
  status TEXT DEFAULT 'draft', -- draft, completed, active
  progress_percentage INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step outputs: 1..16 modules
CREATE TABLE IF NOT EXISTS project_steps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  step_number INTEGER NOT NULL,
  step_name TEXT NOT NULL,
  content JSONB,
  is_completed BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT project_steps_step_number_range CHECK (step_number BETWEEN 1 AND 16),
  CONSTRAINT uniq_project_step_number UNIQUE (project_id, step_number)
);

-- Long-form book content for step 12
CREATE TABLE IF NOT EXISTS book_chapters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  chapter_number INTEGER,
  title TEXT,
  body_text TEXT,
  status TEXT DEFAULT 'draft'
);
