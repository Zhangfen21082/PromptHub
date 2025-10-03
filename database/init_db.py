#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptHub SQLite数据库初始化脚本
用于创建数据库表结构和初始化数据
"""

import sqlite3
import os
from pathlib import Path

def init_database(db_path="data/prompthub.db", schema_path="database/schema.sql"):
    """
    初始化SQLite数据库
    
    Args:
        db_path: 数据库文件路径
        schema_path: 数据库模式文件路径
    """
    # 确保数据目录存在
    db_dir = Path(db_path).parent
    db_dir.mkdir(exist_ok=True)
    
    # 读取SQL模式文件
    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise FileNotFoundError(f"数据库模式文件不存在: {schema_path}")
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 连接数据库并执行SQL
    conn = sqlite3.connect(db_path)
    try:
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        
        # 执行SQL模式
        conn.executescript(schema_sql)
        
        # 提交事务
        conn.commit()
        print(f"数据库初始化成功: {db_path}")
        
    except Exception as e:
        # 回滚事务
        conn.rollback()
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        conn.close()

def check_database_exists(db_path="data/prompthub.db"):
    """
    检查数据库是否存在
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        bool: 数据库是否存在
    """
    return Path(db_path).exists()

def get_database_connection(db_path="data/prompthub.db"):
    """
    获取数据库连接
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    # 确保数据库存在
    if not check_database_exists(db_path):
        init_database(db_path)
    
    # 创建连接并启用外键约束
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # 设置行工厂，使查询结果以字典形式返回
    conn.row_factory = sqlite3.Row
    
    return conn

if __name__ == "__main__":
    # 如果直接运行此脚本，则初始化数据库
    import argparse
    
    parser = argparse.ArgumentParser(description="PromptHub数据库初始化工具")
    parser.add_argument("--db-path", default="data/prompthub.db", help="数据库文件路径")
    parser.add_argument("--schema-path", default="database/schema.sql", help="数据库模式文件路径")
    parser.add_argument("--force", action="store_true", help="强制重新初始化数据库")
    
    args = parser.parse_args()
    
    # 如果强制重新初始化，则删除现有数据库
    if args.force and check_database_exists(args.db_path):
        os.remove(args.db_path)
        print(f"已删除现有数据库: {args.db_path}")
    
    # 初始化数据库
    try:
        init_database(args.db_path, args.schema_path)
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        exit(1)