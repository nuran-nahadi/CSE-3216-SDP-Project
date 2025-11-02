-- Enable UUID generation (pgcrypto is available by default on Supabase)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enum types
CREATE TYPE user_roles AS ENUM ('admin', 'user');
CREATE TYPE task_priorities AS ENUM ('low', 'medium', 'high');
CREATE TYPE themes AS ENUM ('light', 'dark', 'auto');
CREATE TYPE time_formats AS ENUM ('12h', '24h');
CREATE TYPE week_start_days AS ENUM ('monday', 'sunday');
CREATE TYPE expense_categories AS ENUM (
  'food', 'transport', 'entertainment', 'bills',
  'shopping', 'health', 'education', 'travel', 'other'
);
CREATE TYPE payment_methods AS ENUM (
  'cash', 'credit_card', 'debit_card', 'bank_transfer',
  'digital_wallet', 'other'
);

-- users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  hashed_password TEXT NOT NULL,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  profile_picture_url TEXT,
  timezone TEXT NOT NULL DEFAULT 'UTC',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  role user_roles NOT NULL DEFAULT 'user',
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- user_preferences table
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  default_task_priority task_priorities NOT NULL DEFAULT 'medium',
  default_expense_currency TEXT NOT NULL DEFAULT 'USD',
  notification_settings JSONB,
  theme themes NOT NULL DEFAULT 'auto',
  language TEXT NOT NULL DEFAULT 'en',
  date_format TEXT NOT NULL DEFAULT 'YYYY-MM-DD',
  time_format time_formats NOT NULL DEFAULT '12h',
  week_start_day week_start_days NOT NULL DEFAULT 'monday',
  ai_insights_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- expenses table
CREATE TABLE expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DOUBLE PRECISION NOT NULL,
  currency TEXT NOT NULL DEFAULT 'Taka',
  category expense_categories NOT NULL,
  subcategory TEXT,
  merchant TEXT,
  description TEXT,
  date TIMESTAMPTZ NOT NULL,
  payment_method payment_methods,
  receipt_url TEXT,
  is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
  recurrence_rule TEXT,
  tags JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- events table
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  location TEXT,
  tags JSONB,
  is_all_day BOOLEAN NOT NULL DEFAULT FALSE,
  reminder_minutes INTEGER,
  recurrence_rule TEXT,
  color TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT check_end_time_after_start CHECK (end_time > start_time),
  CONSTRAINT check_reminder_minutes_positive CHECK (reminder_minutes IS NULL OR reminder_minutes >= 0),
  CONSTRAINT check_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Task status enum
CREATE TYPE task_statuses AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');

-- tasks table
CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  due_date TIMESTAMPTZ,
  priority task_priorities NOT NULL DEFAULT 'medium',
  status task_statuses NOT NULL DEFAULT 'pending',
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completion_date TIMESTAMPTZ,
  estimated_duration INTEGER,  -- in minutes
  actual_duration INTEGER,    -- in minutes
  tags JSONB,
  parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT check_estimated_duration_positive CHECK (estimated_duration IS NULL OR estimated_duration > 0),
  CONSTRAINT check_actual_duration_positive CHECK (actual_duration IS NULL OR actual_duration > 0),
  CONSTRAINT check_completion_date_with_status CHECK (
    (status = 'completed' AND completion_date IS NOT NULL AND is_completed = TRUE) OR
    (status != 'completed' AND completion_date IS NULL AND is_completed = FALSE)
  )
);





-- 1) Create the enum type
CREATE TYPE journal_moods AS ENUM (
  'very_happy', 'happy', 'neutral', 'sad', 'very_sad', 
  'angry', 'excited', 'anxious', 'grateful'
);

-- 2) Create the table
CREATE TABLE journal_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,
  content TEXT NOT NULL,
  mood journal_moods,
  sentiment_score DOUBLE PRECISION,
  keywords TEXT,         -- JSON stored as string; if you prefer JSONB, change to JSONB
  summary TEXT,
  weather TEXT,
  location TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



-- -- Create indexes for better performance
-- CREATE INDEX idx_tasks_user_id ON tasks(user_id);
-- CREATE INDEX idx_tasks_due_date ON tasks(due_date);
-- CREATE INDEX idx_tasks_status ON tasks(status);
-- CREATE INDEX idx_tasks_priority ON tasks(priority);
-- CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
-- CREATE INDEX idx_tasks_created_at ON tasks(created_at);





------------------------------------ Data inserted for testing ------------------------------------
-- 1) Insert a sample user
INSERT INTO users (
  id,
  username,
  email,
  first_name,
  last_name,
  hashed_password,
  is_verified,
  profile_picture_url,
  timezone,
  role,
  is_active
) VALUES (
  '11111111-1111-1111-1111-111111111111',  -- fixed UUID
  'jdoe',
  'jdoe@example.com',
  'John',
  'Doe',
  '$2b$12$KIX/RSampleHashForDemoOnly1234567890ab',  -- bcrypt placeholder
  TRUE,
  'https://example.com/profiles/jdoe.png',
  'Asia/Dhaka',
  'user',
  TRUE
);

-- 2) Insert a sample expense for that user
INSERT INTO expenses (
  id,
  user_id,
  amount,
  currency,
  category,
  subcategory,
  merchant,
  description,
  date,
  payment_method,
  receipt_url,
  is_recurring,
  recurrence_rule,
  tags
) VALUES (
  '22222222-2222-2222-2222-222222222222',  -- fixed UUID
  '11111111-1111-1111-1111-111111111111',  -- matches the user above
  350.75,
  'Taka',
  'food',
  'lunch',
  'Dhaka Café',
  'Team lunch on project kickoff',
  '2025-06-24T13:45:00+06:00',
  'credit_card',
  'https://example.com/receipts/receipt-20250624.png',
  FALSE,
  NULL,
  '{"tags": ["team","project"]}'::jsonb
);

-- 3) Insert sample events for that user
INSERT INTO events (
  id,
  user_id,
  title,
  description,
  start_time,
  end_time,
  location,
  tags,
  is_all_day,
  reminder_minutes,
  recurrence_rule,
  color
) VALUES 
(
  '33333333-3333-3333-3333-333333333333',
  '11111111-1111-1111-1111-111111111111',
  'Team Standup',
  'Daily team standup meeting',
  '2025-06-25T09:00:00+06:00',
  '2025-06-25T09:30:00+06:00',
  'Conference Room A',
  '{"tags": ["work","meeting","daily"]}'::jsonb,
  FALSE,
  15,
  'FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR',
  '#4CAF50'
),
(
  '44444444-4444-4444-4444-444444444444',
  '11111111-1111-1111-1111-111111111111',
  'Doctor Appointment',
  'Annual health checkup',
  '2025-06-26T14:00:00+06:00',
  '2025-06-26T15:00:00+06:00',
  'City Hospital',
  '{"tags": ["health","appointment"]}'::jsonb,
  FALSE,
  60,
  NULL,
  '#F44336'
),
(
  '55555555-5555-5555-5555-555555555555',
  '11111111-1111-1111-1111-111111111111',
  'Weekend Trip',
  'Weekend getaway to Coxs Bazar',
  '2025-06-28T00:00:00+06:00',
  '2025-06-29T23:59:59+06:00',
  'Coxs Bazar',
  '{"tags": ["travel","vacation","weekend"]}'::jsonb,
  TRUE,
  1440,
  NULL,
  '#2196F3'
);


-- Insert a parent task
INSERT INTO tasks (
  id,
  user_id,
  title,
  description,
  due_date,
  priority,
  status,
  is_completed,
  completion_date,
  estimated_duration,
  actual_duration,
  tags,
  parent_task_id,
  created_at,
  updated_at
) VALUES (
  '66666666-6666-6666-6666-666666666666',  -- fixed UUID for parent task
  '11111111-1111-1111-1111-111111111111',  -- matches the test user
  'Q2 Project Planning',
  'Complete Q2 project planning and documentation',
  '2025-06-30T17:00:00+06:00',
  'high',
  'in_progress',
  FALSE,
  NULL,
  480,  -- 8 hours estimated
  NULL,
  '{"tags": ["project","planning","q2"]}'::jsonb,
  NULL,  -- no parent task
  '2025-06-24T09:00:00+06:00',
  '2025-06-24T09:00:00+06:00'
);

-- Insert some subtasks
INSERT INTO tasks (
  id,
  user_id,
  title,
  description,
  due_date,
  priority,
  status,
  is_completed,
  completion_date,
  estimated_duration,
  actual_duration,
  tags,
  parent_task_id,
  created_at,
  updated_at
) VALUES 
(
  '77777777-7777-7777-7777-777777777777',
  '11111111-1111-1111-1111-111111111111',
  'Resource Allocation',
  'Determine resource requirements and allocations for Q2 projects',
  '2025-06-25T17:00:00+06:00',
  'high',
  'completed',
  TRUE,
  '2025-06-24T16:30:00+06:00',
  120,  -- 2 hours estimated
  90,   -- 1.5 hours actual
  '{"tags": ["resources","planning"]}'::jsonb,
  '66666666-6666-6666-6666-666666666666',  -- parent task ID
  '2025-06-24T09:00:00+06:00',
  '2025-06-24T16:30:00+06:00'
),
(
  '88888888-8888-8888-8888-888888888888',
  '11111111-1111-1111-1111-111111111111',
  'Budget Planning',
  'Create detailed budget plan for Q2 projects',
  '2025-06-26T17:00:00+06:00',
  'high',
  'pending',
  FALSE,
  NULL,
  180,  -- 3 hours estimated
  NULL,
  '{"tags": ["budget","planning","finance"]}'::jsonb,
  '66666666-6666-6666-6666-666666666666',  -- parent task ID
  '2025-06-24T09:00:00+06:00',
  '2025-06-24T09:00:00+06:00'
),
(
  '99999999-9999-9999-9999-999999999999',
  '11111111-1111-1111-1111-111111111111',
  'Timeline Development',
  'Create project timelines and milestones',
  '2025-06-27T17:00:00+06:00',
  'medium',
  'pending',
  FALSE,
  NULL,
  240,  -- 4 hours estimated
  NULL,
  '{"tags": ["timeline","planning","milestones"]}'::jsonb,
  '66666666-6666-6666-6666-666666666666',  -- parent task ID
  '2025-06-24T09:00:00+06:00',
  '2025-06-24T09:00:00+06:00'
);

-- Insert a standalone task
INSERT INTO tasks (
  id,
  user_id,
  title,
  description,
  due_date,
  priority,
  status,
  is_completed,
  completion_date,
  estimated_duration,
  actual_duration,
  tags,
  parent_task_id,
  created_at,
  updated_at
) VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  '11111111-1111-1111-1111-111111111111',
  'Review Team Performance',
  'Complete Q2 performance reviews for team members',
  '2025-06-28T17:00:00+06:00',
  'medium',
  'pending',
  FALSE,
  NULL,
  300,  -- 5 hours estimated
  NULL,
  '{"tags": ["hr","reviews","q2"]}'::jsonb,
  NULL,  -- no parent task
  '2025-06-24T09:00:00+06:00',
  '2025-06-24T09:00:00+06:00'
);

-- 3) Insert a sample journal entry
INSERT INTO journal_entries (
  id,
  user_id,
  title,
  content,
  mood,
  sentiment_score,
  keywords,
  summary,
  weather,
  location,
  created_at
) VALUES (
  '33333333-3333-3333-3333-333333333333',  -- fixed UUID
  '11111111-1111-1111-1111-111111111111',  -- existing user_id
  'Reflections on Networking',
  'Today I dug into TCP Reno vs Tahoe and finally understand how cwnd adapts. Feeling confident about my simulation code!',
  'happy',
  0.85,
  '["tcp","reno","simulation"]',
  'Understood cwnd behavior in congestion control algorithms.',
  'Sunny, 30°C',
  'Dhaka, Bangladesh',
  '2025-07-02T10:00:00+06:00'
);


