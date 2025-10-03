#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptHub JSON到SQLite数据迁移脚本
将现有的JSON数据导入到SQLite数据库中
"""

import json
import sqlite3
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def migrate_from_json(json_path: str = "data/prompts.json", 
                     db_path: str = "data/prompthub.db",
                     schema_path: str = "database/schema.sql") -> Dict[str, Any]:
    """
    从JSON文件迁移数据到SQLite数据库
    
    Args:
        json_path: JSON数据文件路径
        db_path: SQLite数据库文件路径
        schema_path: 数据库模式文件路径
        
    Returns:
        Dict: 迁移结果统计
    """
    # 检查JSON文件是否存在
    if not Path(json_path).exists():
        raise FileNotFoundError(f"JSON数据文件不存在: {json_path}")
    
    # 读取JSON数据
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # 初始化数据库
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database.init_db import init_database
    init_database(db_path, schema_path)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        
        # 统计信息
        stats = {
            "categories_imported": 0,
            "tags_imported": 0,
            "prompts_imported": 0,
            "versions_imported": 0,
            "prompt_tags_imported": 0,
            "errors": []
        }
        
        # 迁移分类数据
        if "metadata" in json_data and "categories" in json_data["metadata"]:
            categories = json_data["metadata"]["categories"]
            for category in categories:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO categories (
                            id, name, color, description, parent_id, level, path, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        category.get("id", str(uuid.uuid4())),
                        category.get("name", ""),
                        category.get("color", "#6B7280"),
                        category.get("description", ""),
                        category.get("parent_id"),
                        category.get("level", 1),
                        category.get("path", category.get("name", "")),
                        category.get("created_at", datetime.now().isoformat()),
                        category.get("updated_at", datetime.now().isoformat())
                    ))
                    stats["categories_imported"] += 1
                except Exception as e:
                    stats["errors"].append(f"导入分类失败: {category.get('name', '未知')} - {str(e)}")
        
        # 迁移标签数据
        if "metadata" in json_data and "tags" in json_data["metadata"]:
            tags = json_data["metadata"]["tags"]
            for tag in tags:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO tags (
                            id, name, color, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        tag.get("id", str(uuid.uuid4())),
                        tag.get("name", ""),
                        tag.get("color", "#3B82F6"),
                        tag.get("created_at", datetime.now().isoformat()),
                        tag.get("updated_at", datetime.now().isoformat())
                    ))
                    stats["tags_imported"] += 1
                except Exception as e:
                    stats["errors"].append(f"导入标签失败: {tag.get('name', '未知')} - {str(e)}")
        
        # 迁移提示词数据
        if "prompts" in json_data:
            prompts = json_data["prompts"]
            for prompt in prompts:
                try:
                    # 插入提示词
                    cursor.execute("""
                        INSERT OR REPLACE INTO prompts (
                            id, title, content, description, category_id, 
                            category_name, category_path, usage_count, 
                            current_version, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prompt.get("id", str(uuid.uuid4())),
                        prompt.get("title", ""),
                        prompt.get("content", ""),
                        prompt.get("description", ""),
                        prompt.get("category_id"),
                        prompt.get("category", ""),
                        prompt.get("category_path", prompt.get("category", "")),
                        prompt.get("usage_count", 0),
                        prompt.get("current_version", "1.0"),
                        prompt.get("created_at", datetime.now().isoformat()),
                        prompt.get("updated_at", datetime.now().isoformat())
                    ))
                    stats["prompts_imported"] += 1
                    
                    # 插入版本数据
                    if "versions" in prompt:
                        for version in prompt["versions"]:
                            try:
                                cursor.execute("""
                                    INSERT OR REPLACE INTO prompt_versions (
                                        prompt_id, version, title, content, description, 
                                        change_note, created_at
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    prompt.get("id", ""),
                                    version.get("version", "1.0"),
                                    version.get("title", prompt.get("title", "")),
                                    version.get("content", prompt.get("content", "")),
                                    version.get("description", ""),
                                    version.get("change_note", ""),
                                    version.get("created_at", datetime.now().isoformat())
                                ))
                                stats["versions_imported"] += 1
                            except Exception as e:
                                stats["errors"].append(f"导入版本失败: {prompt.get('title', '未知')} - {str(e)}")
                    
                    # 插入标签关联
                    if "tags" in prompt and prompt["tags"]:
                        for tag_name in prompt["tags"]:
                            try:
                                # 确保标签存在
                                cursor.execute("""
                                    INSERT OR IGNORE INTO tags (id, name, color, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    str(uuid.uuid4()),
                                    tag_name,
                                    "#3B82F6",
                                    datetime.now().isoformat(),
                                    datetime.now().isoformat()
                                ))
                                
                                # 添加关联
                                cursor.execute("""
                                    INSERT OR IGNORE INTO prompt_tags (prompt_id, tag_name, created_at)
                                    VALUES (?, ?, ?)
                                """, (
                                    prompt.get("id", ""),
                                    tag_name,
                                    datetime.now().isoformat()
                                ))
                                stats["prompt_tags_imported"] += 1
                            except Exception as e:
                                stats["errors"].append(f"导入提示词标签失败: {prompt.get('title', '未知')} - {tag_name} - {str(e)}")
                except Exception as e:
                    stats["errors"].append(f"导入提示词失败: {prompt.get('title', '未知')} - {str(e)}")
        
        # 更新设置
        if "metadata" in json_data and "settings" in json_data["metadata"]:
            settings = json_data["metadata"]["settings"]
            for key, value in settings.items():
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO settings (key, value, updated_at)
                        VALUES (?, ?, ?)
                    """, (
                        key,
                        str(value),
                        datetime.now().isoformat()
                    ))
                except Exception as e:
                    stats["errors"].append(f"导入设置失败: {key} - {str(e)}")
        
        # 添加迁移标记
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (
            "migrated_from_json",
            "true",
            datetime.now().isoformat()
        ))
        
        # 提交事务
        conn.commit()
        
        return stats
    except Exception as e:
        # 回滚事务
        conn.rollback()
        raise Exception(f"数据迁移失败: {str(e)}")
    finally:
        conn.close()

def backup_json_data(json_path: str = "data/prompts.json") -> str:
    """
    备份JSON数据文件
    
    Args:
        json_path: JSON数据文件路径
        
    Returns:
        str: 备份文件路径
    """
    # 创建备份目录
    backup_dir = Path("data/backup")
    backup_dir.mkdir(exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"prompts_json_backup_{timestamp}.json"
    
    # 复制文件
    import shutil
    shutil.copy2(json_path, backup_file)
    
    return str(backup_file)

def check_migration_needed(json_path: str = "data/prompts.json", 
                          db_path: str = "data/prompthub.db") -> bool:
    """
    检查是否需要执行数据迁移
    
    Args:
        json_path: JSON数据文件路径
        db_path: SQLite数据库文件路径
        
    Returns:
        bool: 是否需要迁移
    """
    # 如果JSON文件不存在，不需要迁移
    if not Path(json_path).exists():
        return False
    
    # 如果数据库不存在，需要迁移
    if not Path(db_path).exists():
        return True
    
    # 检查数据库中是否已有迁移标记
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'migrated_from_json'")
        result = cursor.fetchone()
        
        # 如果没有迁移标记，需要迁移
        if not result or result[0] != "true":
            return True
        
        return False
    except Exception:
        # 如果查询失败，可能数据库未初始化，需要迁移
        return True
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PromptHub JSON到SQLite数据迁移工具")
    parser.add_argument("--json-path", default="data/prompts.json", help="JSON数据文件路径")
    parser.add_argument("--db-path", default="data/prompthub.db", help="SQLite数据库文件路径")
    parser.add_argument("--schema-path", default="database/schema.sql", help="数据库模式文件路径")
    parser.add_argument("--force", action="store_true", help="强制执行迁移，即使已有迁移标记")
    parser.add_argument("--no-backup", action="store_true", help="不备份JSON数据文件")
    
    args = parser.parse_args()
    
    try:
        # 检查是否需要迁移
        if not args.force and not check_migration_needed(args.json_path, args.db_path):
            print("数据已是最新，无需迁移")
            exit(0)
        
        # 备份JSON数据
        if not args.no_backup:
            backup_file = backup_json_data(args.json_path)
            print(f"JSON数据已备份到: {backup_file}")
        
        # 执行迁移
        print("开始数据迁移...")
        stats = migrate_from_json(args.json_path, args.db_path, args.schema_path)
        
        # 输出迁移结果
        print("\n数据迁移完成:")
        print(f"- 分类导入: {stats['categories_imported']} 个")
        print(f"- 标签导入: {stats['tags_imported']} 个")
        print(f"- 提示词导入: {stats['prompts_imported']} 个")
        print(f"- 版本导入: {stats['versions_imported']} 个")
        print(f"- 提示词标签关联: {stats['prompt_tags_imported']} 个")
        
        if stats["errors"]:
            print(f"\n迁移过程中发生 {len(stats['errors'])} 个错误:")
            for error in stats["errors"]:
                print(f"- {error}")
        
        print(f"\n数据已成功迁移到: {args.db_path}")
    except Exception as e:
        print(f"数据迁移失败: {e}")
        exit(1)