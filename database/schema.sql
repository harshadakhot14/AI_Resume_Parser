-- ============================================================
-- Resume Parser Database Schema
-- ============================================================
-- File: database/schema.sql
-- Purpose: Single source of truth for database structure.
-- Usage: psql -U <username> -d resume_parser_db -f database/schema.sql
-- ============================================================

-- ============================================================
-- 1. EXTENSIONS
-- ============================================================
-- Enable case-insensitive text for better search
CREATE EXTENSION IF NOT EXISTS citext;

-- ============================================================
-- 2. TABLES
-- ============================================================

-- -----------------------------------------------------------
-- Table: resumes
-- Purpose: Stores the main resume record with personal info
--          and the raw extracted text for reference.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS resumes (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255),
    email           VARCHAR(255),
    phone           VARCHAR(50),
    linkedin_url    VARCHAR(500),
    github_url      VARCHAR(500),
    summary         TEXT,
    raw_text        TEXT,
    file_name       VARCHAR(255) NOT NULL,
    file_path       VARCHAR(500) NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- Table: education
-- Purpose: Stores education entries linked to a resume.
--          One resume can have multiple education records.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS education (
    id              SERIAL PRIMARY KEY,
    resume_id       INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    institution     VARCHAR(255),
    degree          VARCHAR(255),
    field_of_study  VARCHAR(255),
    start_date      VARCHAR(50),
    end_date        VARCHAR(50),
    gpa             VARCHAR(20)
);

-- -----------------------------------------------------------
-- Table: experience
-- Purpose: Stores work experience entries linked to a resume.
--          One resume can have multiple experience records.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS experience (
    id              SERIAL PRIMARY KEY,
    resume_id       INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    company         VARCHAR(255),
    job_title       VARCHAR(255),
    start_date      VARCHAR(50),
    end_date        VARCHAR(50),
    description     TEXT
);

-- -----------------------------------------------------------
-- Table: projects
-- Purpose: Stores project entries linked to a resume.
--          One resume can have multiple project records.
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id              SERIAL PRIMARY KEY,
    resume_id       INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    title           VARCHAR(255),
    description     TEXT,
    technologies    VARCHAR(500),
    link            VARCHAR(500)
);

-- -----------------------------------------------------------
-- Table: skills
-- Purpose: Stores individual skills linked to a resume.
--          Skills are categorized (e.g., "Programming Language",
--          "Framework", "Tool", "Soft Skill").
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id              SERIAL PRIMARY KEY,
    resume_id       INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    skill_name      VARCHAR(255) NOT NULL,
    category        VARCHAR(100)
);

-- ============================================================
-- 3. INDEXES
-- ============================================================
-- Speed up lookups by email (common search field)
CREATE INDEX IF NOT EXISTS idx_resumes_email ON resumes(email);

-- Speed up lookups by name
CREATE INDEX IF NOT EXISTS idx_resumes_name ON resumes(name);

-- Speed up JOIN queries on foreign keys
CREATE INDEX IF NOT EXISTS idx_education_resume_id ON education(resume_id);
CREATE INDEX IF NOT EXISTS idx_experience_resume_id ON experience(resume_id);
CREATE INDEX IF NOT EXISTS idx_skills_resume_id ON skills(resume_id);

-- Speed up skill-based searches
CREATE INDEX IF NOT EXISTS idx_skills_skill_name ON skills(skill_name);

-- ============================================================
-- 4. TRIGGER: Auto-update updated_at on row modification
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to resumes table
DROP TRIGGER IF EXISTS trigger_resumes_updated_at ON resumes;
CREATE TRIGGER trigger_resumes_updated_at
    BEFORE UPDATE ON resumes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 5. TABLE COMMENTS
-- ============================================================
COMMENT ON TABLE resumes IS 'Main resume records with personal info and raw extracted text';
COMMENT ON TABLE education IS 'Education entries linked to resumes (one-to-many)';
COMMENT ON TABLE experience IS 'Work experience entries linked to resumes (one-to-many)';
COMMENT ON TABLE skills IS 'Individual skills linked to resumes with category classification';

COMMENT ON COLUMN resumes.raw_text IS 'Full extracted text from the uploaded resume file';
COMMENT ON COLUMN resumes.file_path IS 'Server-side path to the uploaded resume file';
COMMENT ON COLUMN skills.category IS 'Skill category: Programming Language, Framework, Database, Tool, Soft Skill, etc.';
