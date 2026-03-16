ALTER TABLE ai_knowledge
    ADD COLUMN parent_id VARCHAR(50) NOT NULL DEFAULT '0' COMMENT '父目录ID，根目录为0' AFTER project_id;

CREATE INDEX idx_parent_id ON ai_knowledge(parent_id);
