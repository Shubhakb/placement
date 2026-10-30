-- ====================================================================
-- College Placement Management System - Supabase Schema Extension
-- Run this script in the Supabase SQL Editor to add missing columns
-- ====================================================================

-- 1. Extend public.students table
ALTER TABLE public.students 
ADD COLUMN IF NOT EXISTS password text DEFAULT 'student123',
ADD COLUMN IF NOT EXISTS skills text,
ADD COLUMN IF NOT EXISTS certifications text,
ADD COLUMN IF NOT EXISTS projects text,
ADD COLUMN IF NOT EXISTS github_url text,
ADD COLUMN IF NOT EXISTS portfolio_url text,
ADD COLUMN IF NOT EXISTS preferred_location text,
ADD COLUMN IF NOT EXISTS preferred_work_mode text,
ADD COLUMN IF NOT EXISTS backlogs integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS profile_photo text,
ADD COLUMN IF NOT EXISTS graduation_year integer;

-- 2. Extend public.companies table
ALTER TABLE public.companies 
ADD COLUMN IF NOT EXISTS password text DEFAULT 'company123',
ADD COLUMN IF NOT EXISTS recruiter_name text,
ADD COLUMN IF NOT EXISTS industry text,
ADD COLUMN IF NOT EXISTS logo_url text;

-- 3. Extend public.job_postings table
ALTER TABLE public.job_postings 
ADD COLUMN IF NOT EXISTS required_skills text,
ADD COLUMN IF NOT EXISTS qualification text,
ADD COLUMN IF NOT EXISTS graduation_year integer,
ADD COLUMN IF NOT EXISTS backlog_requirement integer DEFAULT 0,
ADD COLUMN IF NOT EXISTS work_mode text DEFAULT 'Onsite',
ADD COLUMN IF NOT EXISTS openings integer DEFAULT 1;

-- 4. Extend public.interviews table
ALTER TABLE public.interviews 
ADD COLUMN IF NOT EXISTS interview_time text,
ADD COLUMN IF NOT EXISTS interview_round text,
ADD COLUMN IF NOT EXISTS meeting_info text,
ADD COLUMN IF NOT EXISTS instructions text;

-- 5. Add unique constraint on applications (student_id + job_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_student_job'
    ) THEN
        ALTER TABLE public.applications ADD CONSTRAINT unique_student_job UNIQUE (student_id, job_id);
    END IF;
END $$;
