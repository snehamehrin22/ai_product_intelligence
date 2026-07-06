-- AI Todo App - Database Schema Setup
-- This script creates the necessary tables in Databricks using Delta Lake format
-- Run this in Databricks SQL Editor: https://your-workspace.databricks.com/sql/editor

-- Use the appropriate catalog and schema
-- NOTE: Update the catalog name if using a different one (currently: signaltogrowth)
USE CATALOG signaltogrowth;
CREATE SCHEMA IF NOT EXISTS todo_app;
USE SCHEMA todo_app;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Stores user information (hardcoded test user for Phase 1)
CREATE TABLE IF NOT EXISTS users (
  user_id STRING NOT NULL COMMENT 'Unique user identifier (UUID)',
  email STRING NOT NULL COMMENT 'User email address',
  full_name STRING COMMENT 'User full name',
  created_at TIMESTAMP NOT NULL COMMENT 'Account creation timestamp',
  updated_at TIMESTAMP NOT NULL COMMENT 'Last update timestamp',
  CONSTRAINT users_pk PRIMARY KEY (user_id)
)
USING DELTA
COMMENT 'User accounts for the todo app'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'  -- Enable CDC for Phase 3 streaming
);

-- ============================================================================
-- TASKS TABLE
-- ============================================================================
-- Stores todo tasks with full metadata
CREATE TABLE IF NOT EXISTS tasks (
  task_id STRING NOT NULL COMMENT 'Unique task identifier (UUID)',
  user_id STRING NOT NULL COMMENT 'Foreign key to users table',
  title STRING NOT NULL COMMENT 'Task title (max 200 chars)',
  description STRING COMMENT 'Detailed task description',
  status STRING NOT NULL COMMENT 'Task status: pending, in_progress, completed, cancelled (validated by Pydantic)',
  priority STRING NOT NULL COMMENT 'Task priority: low, medium, high, urgent (validated by Pydantic)',
  due_date TIMESTAMP COMMENT 'Optional task due date/time',
  created_at TIMESTAMP NOT NULL COMMENT 'Task creation timestamp',
  updated_at TIMESTAMP NOT NULL COMMENT 'Last update timestamp',
  CONSTRAINT tasks_pk PRIMARY KEY (task_id)
)
USING DELTA
COMMENT 'Todo tasks with AI-generated and manual entries'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'  -- Enable CDC for Phase 3 streaming
);

-- ============================================================================
-- TEST DATA
-- ============================================================================
-- Insert test user for Phase 1 development
INSERT INTO users (user_id, email, full_name, created_at, updated_at)
VALUES (
  'test-user-001',
  'test@example.com',
  'Test User',
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
)
-- Only insert if not already exists
EXCEPT
SELECT user_id, email, full_name, created_at, updated_at FROM users WHERE user_id = 'test-user-001';

-- Insert sample tasks for testing
INSERT INTO tasks (task_id, user_id, title, description, status, priority, due_date, created_at, updated_at)
VALUES
  (
    'task-001',
    'test-user-001',
    'Complete backend setup',
    'Set up FastAPI backend with Databricks connection',
    'completed',
    'high',
    NULL,
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP()
  ),
  (
    'task-002',
    'test-user-001',
    'Implement CRUD endpoints',
    'Create REST API endpoints for task management',
    'in_progress',
    'high',
    DATE_ADD(CURRENT_DATE(), 2),
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP()
  ),
  (
    'task-003',
    'test-user-001',
    'Build React frontend',
    'Create UI components for task list and forms',
    'pending',
    'medium',
    DATE_ADD(CURRENT_DATE(), 7),
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP()
  )
-- Only insert if not already exists
EXCEPT
SELECT task_id, user_id, title, description, status, priority, due_date, created_at, updated_at
FROM tasks
WHERE task_id IN ('task-001', 'task-002', 'task-003');

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify setup was successful

-- Check tables exist
SHOW TABLES IN signaltogrowth.todo_app;

-- Check table schemas
DESCRIBE TABLE EXTENDED signaltogrowth.todo_app.users;
DESCRIBE TABLE EXTENDED signaltogrowth.todo_app.tasks;

-- Verify test data
SELECT * FROM signaltogrowth.todo_app.users;
SELECT * FROM signaltogrowth.todo_app.tasks ORDER BY created_at;

-- Check Delta Lake properties (CDC should be enabled)
SHOW TBLPROPERTIES signaltogrowth.todo_app.users;
SHOW TBLPROPERTIES signaltogrowth.todo_app.tasks;
