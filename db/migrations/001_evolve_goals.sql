-- Migration: Align legacy 'todos' with Core V2 'Goal' domain model
ALTER TABLE todos ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 1;
ALTER TABLE todos ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE todos ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Cleanup: Set created_at from old timestamp if it exists, then remove old column
UPDATE todos SET created_at = timestamp WHERE timestamp IS NOT NULL;
-- ALTER TABLE todos DROP COLUMN timestamp; -- We keep it for safety in this phase

-- Add index for priority-based queries
CREATE INDEX IF NOT EXISTS idx_goals_priority ON todos(priority DESC, status);
