-- AI知识库文档表 - V1.26
-- 只保留知识库文档表，其他AI相关表已移除

CREATE TABLE IF NOT EXISTS ai_knowledge (
    id VARCHAR(50) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(50) NOT NULL COMMENT '所属项目ID',
    name VARCHAR(255) NOT NULL COMMENT '文档名称',
    content TEXT COMMENT '文档内容(Markdown)',
    doc_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:使用手册 guide:引导文档 api_doc:接口文档 custom:自定义',
    source_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:手动上传 auto:自动生成',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 indexed:已索引 error:索引失败',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    create_user VARCHAR(50) COMMENT '创建人',
    update_user VARCHAR(50) COMMENT '更新人',
    INDEX idx_project (project_id),
    INDEX idx_type (doc_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI知识库文档表';
