-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low
  status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed
  deadline TIMESTAMP,
  ai_suggested_priority INTEGER,
  ai_suggested_deadline TIMESTAMP,
  context_tags TEXT[], -- Array of context tags
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

-- Create context_entries table for daily context
CREATE TABLE IF NOT EXISTS context_entries (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  entry_type VARCHAR(50) NOT NULL, -- message, email, note, meeting
  entry_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_context_entries_user_id ON context_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_context_entries_date ON context_entries(entry_date);
