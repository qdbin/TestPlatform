-- AI智能测试助手数据库脚本
-- V1.26__init_ai.sql

-- 一、AI知识库文档表
CREATE TABLE IF NOT EXISTS ai_knowledge (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '所属项目ID',
    name VARCHAR(255) NOT NULL COMMENT '文档名称',
    content TEXT COMMENT '文档内容(Markdown)',
    doc_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:使用手册 guide:引导文档 api_doc:接口文档 custom:自定义',
    source_type VARCHAR(32) DEFAULT 'manual' COMMENT 'manual:手动上传 auto:自动生成',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 deleted:已删除',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    create_user VARCHAR(32) COMMENT '创建人',
    update_user VARCHAR(32) COMMENT '更新人',
    INDEX idx_project (project_id),
    INDEX idx_type (doc_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI知识库文档表';

-- 二、AI会话历史表
CREATE TABLE IF NOT EXISTS ai_conversation (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '项目ID',
    user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
    session_type VARCHAR(32) DEFAULT 'chat' COMMENT 'chat:知识问答 case_generate:用例生成',
    title VARCHAR(255) COMMENT '会话标题',
    messages JSON NOT NULL COMMENT '对话消息JSON: [{role: user/assistant, content: 内容, time: 时间戳}]',
    context JSON COMMENT '上下文数据: {selected_apis: [], current_case: {}}',
    use_rag TINYINT(1) DEFAULT 1 COMMENT '是否启用RAG',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 closed:已关闭',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    INDEX idx_project_user (project_id, user_id),
    INDEX idx_session_type (session_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI会话历史表';

-- 三、AI配置表
CREATE TABLE IF NOT EXISTS ai_config (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    config_key VARCHAR(64) NOT NULL COMMENT '配置键: provider/model/api_key/base_url',
    config_value VARCHAR(500) COMMENT '配置值',
    is_global TINYINT(1) DEFAULT 0 COMMENT '是否全局配置(1:全局 0:项目级)',
    project_id VARCHAR(32) COMMENT '项目ID(全局配置时为空)',
    status VARCHAR(16) DEFAULT 'active' COMMENT 'active:有效 deleted:已删除',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '更新时间戳',
    UNIQUE KEY uk_key_project (config_key, project_id),
    INDEX idx_global (is_global)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI配置表';

-- 四、AI接口索引表(记录哪些接口已加入知识库)
CREATE TABLE IF NOT EXISTS ai_api_index (
    id VARCHAR(32) PRIMARY KEY COMMENT '主键ID',
    project_id VARCHAR(32) NOT NULL COMMENT '项目ID',
    api_id VARCHAR(32) NOT NULL COMMENT '接口ID',
    api_name VARCHAR(255) COMMENT '接口名称',
    api_path VARCHAR(500) COMMENT '接口路径',
    api_method VARCHAR(16) COMMENT '请求方法',
    api_info TEXT COMMENT '接口详细信息(JSON)',
    indexed_status VARCHAR(16) DEFAULT 'pending' COMMENT 'pending:待索引 ready:已索引 error:索引失败',
    error_msg VARCHAR(500) COMMENT '错误信息',
    create_time BIGINT NOT NULL COMMENT '创建时间戳',
    update_time BIGINT NOT NULL COMMENT '索引时间戳',
    INDEX idx_project (project_id),
    INDEX idx_api (api_id),
    INDEX idx_status (indexed_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI接口索引表';

-- 五、初始化默认配置(可选)
-- INSERT INTO ai_config (id, config_key, config_value, is_global, status, create_time, update_time)
-- VALUES (UUID(), 'provider', 'deepseek', 1, 'active', UNIX_TIMESTAMP()*1000, UNIX_TIMESTAMP()*1000);
