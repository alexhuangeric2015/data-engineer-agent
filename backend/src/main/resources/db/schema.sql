-- 本地演示库；事实表字段严格沿用 V10 SKILL 已确认的契约。
CREATE DATABASE IF NOT EXISTS data_engineer_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE data_engineer_agent;

CREATE TABLE IF NOT EXISTS table_schema (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '本地记录主键，不作为业务表标识',
  table_name_en VARCHAR(255) NOT NULL COMMENT '表英文名',
  table_name_cn VARCHAR(255) NULL COMMENT '表中文名，NULL 表示未提供',
  column_name VARCHAR(255) NOT NULL COMMENT '字段英文名',
  column_cn_name VARCHAR(255) NULL COMMENT '字段中文名，NULL 表示未提供',
  column_type VARCHAR(128) NULL COMMENT '字段类型原值',
  is_key VARCHAR(32) NULL COMMENT '原始主键标记，值域由数据源决定',
  is_related VARCHAR(32) NULL COMMENT '原始关联标记，值域由数据源决定',
  related_column_en VARCHAR(255) NULL COMMENT '字段关联的字典类型英文名',
  related_column_cn VARCHAR(255) NULL COMMENT '字段关联的字典类型中文名',
  biz_desc TEXT NULL COMMENT '字段业务描述，不是字段注释',
  PRIMARY KEY (id), KEY idx_table_en (table_name_en), KEY idx_table_cn (table_name_cn),
  KEY idx_table_column (table_name_en, column_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='表与字段治理事实';

CREATE TABLE IF NOT EXISTS data_asset_code_kb (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '本地记录主键，允许原始业务行重复',
  code_table_cn_name VARCHAR(255) NULL COMMENT '字典类型中文名',
  code_table_en_name VARCHAR(255) NOT NULL COMMENT '字典类型英文名',
  code_value VARCHAR(255) NULL COMMENT '原始码值，字符串保留前导零和大小写',
  code_desc TEXT NULL COMMENT '原始码值含义',
  PRIMARY KEY (id), KEY idx_type_en (code_table_en_name), KEY idx_type_cn (code_table_cn_name),
  KEY idx_type_value (code_table_en_name, code_value)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据字典原始记录';

CREATE TABLE IF NOT EXISTS agent_chat_session (
  id CHAR(36) NOT NULL COMMENT '前后端共享的会话 UUID',
  mode VARCHAR(32) NOT NULL COMMENT '执行模式：REACT 或 PLAN_AND_EXECUTE',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '会话创建时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Demo 会话';

CREATE TABLE IF NOT EXISTS agent_chat_message (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息顺序主键',
  session_id CHAR(36) NOT NULL COMMENT '所属会话 UUID',
  role VARCHAR(16) NOT NULL COMMENT 'USER 或 ASSISTANT',
  content MEDIUMTEXT NOT NULL COMMENT '完整消息正文',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '消息写入时间',
  PRIMARY KEY (id), KEY idx_session_message (session_id, id),
  CONSTRAINT fk_chat_message_session FOREIGN KEY (session_id) REFERENCES agent_chat_session(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Demo 对话历史';
