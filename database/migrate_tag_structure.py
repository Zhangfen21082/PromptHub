#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：将 prompt_tags 表从使用 tag_name 改为使用 tag_id
"""

import sqlite3
from pathlib import Path


def migrate_tag_structure(db_path: str = "data/prompthub.db"):
    """
    迁移标签表结构：
    1. 创建新的 prompt_tags 表（使用 tag_id）
    2. 迁移现有数据
    3. 删除旧表，重命名新表
    """
    print(f"开始迁移数据库: {db_path}")

    if not Path(db_path).exists():
        print(f"数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        # 禁用外键约束
        cursor.execute("PRAGMA foreign_keys = OFF")

        print("1. 创建新的 prompt_tags 表...")
        # 创建新的 prompt_tags 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_tags_new (
                prompt_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (prompt_id, tag_id),
                FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

        print("2. 迁移现有数据...")
        # 迁移数据：通过 tag_name 关联到 tag_id
        cursor.execute("""
            INSERT INTO prompt_tags_new (prompt_id, tag_id, created_at)
            SELECT pt.prompt_id, t.id, pt.created_at
            FROM prompt_tags pt
            INNER JOIN tags t ON pt.tag_name = t.name
        """)

        migrated_rows = cursor.rowcount
        print(f"   已迁移 {migrated_rows} 条记录")

        print("3. 删除旧索引...")
        # 删除旧索引
        cursor.execute("DROP INDEX IF EXISTS idx_prompt_tags_prompt_id")
        cursor.execute("DROP INDEX IF EXISTS idx_prompt_tags_tag_name")

        print("4. 删除旧表...")
        # 删除旧表
        cursor.execute("DROP TABLE IF EXISTS prompt_tags")

        print("5. 重命名新表...")
        # 重命名新表
        cursor.execute("ALTER TABLE prompt_tags_new RENAME TO prompt_tags")

        print("6. 创建新索引...")
        # 创建新索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_tags_prompt_id ON prompt_tags(prompt_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompt_tags_tag_id ON prompt_tags(tag_id)")

        # 重新启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")

        # 验证外键完整性
        print("7. 验证外键完整性...")
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if fk_errors:
            print("警告: 发现外键完整性问题:")
            for error in fk_errors:
                print(f"   {error}")
            conn.rollback()
            return False

        conn.commit()
        print("✓ 迁移成功完成！")
        return True

    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate_tag_structure()
    exit(0 if success else 1)
