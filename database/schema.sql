-- PromptHub SQLite数据库模式
-- 创建时间: 2025-10-04

-- 分类表
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#6B7280',
    description TEXT DEFAULT '',
    parent_id TEXT,
    level INTEGER DEFAULT 1,
    path TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#3B82F6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 提示词表
CREATE TABLE IF NOT EXISTS prompts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    description TEXT DEFAULT '',
    category_id TEXT,
    category_name TEXT DEFAULT '',
    category_path TEXT DEFAULT '',
    usage_count INTEGER DEFAULT 0,
    current_version TEXT DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 提示词版本表
CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id TEXT NOT NULL,
    version TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    description TEXT DEFAULT '',
    change_note TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    UNIQUE(prompt_id, version)
);

-- 提示词标签关联表
CREATE TABLE IF NOT EXISTS prompt_tags (
    prompt_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prompt_id, tag_id),
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 系统设置表
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_prompts_category_id ON prompts(category_id);
CREATE INDEX IF NOT EXISTS idx_prompts_category_name ON prompts(category_name);
CREATE INDEX IF NOT EXISTS idx_prompts_title ON prompts(title);
CREATE INDEX IF NOT EXISTS idx_prompts_created_at ON prompts(created_at);
CREATE INDEX IF NOT EXISTS idx_prompts_updated_at ON prompts(updated_at);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_level ON categories(level);
CREATE INDEX IF NOT EXISTS idx_categories_path ON categories(path);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_tags_prompt_id ON prompt_tags(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_tags_tag_id ON prompt_tags(tag_id);

-- 插入默认分类
INSERT OR IGNORE INTO categories (id, name, color, description, parent_id, level, path) VALUES
('0', '未分类', '#9CA3AF', '未分类的提示词', NULL, 1, '未分类');

-- 插入默认设置
INSERT OR IGNORE INTO settings (key, value) VALUES
('version', '2.0'),
('last_updated', datetime('now')),
('migrated_from_json', 'false');