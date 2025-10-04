#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptHub SQLite数据库存储类
替换原有的FileStorage类，提供相同接口但使用SQLite作为后端存储
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from database.init_db import get_database_connection, init_database

class SQLiteStorage:
    """SQLite数据库存储类，替换原有的FileStorage类"""
    
    def __init__(self, db_path: str = "data/prompthub.db", schema_path: str = "database/schema.sql"):
        """
        初始化SQLite存储
        
        Args:
            db_path: 数据库文件路径
            schema_path: 数据库模式文件路径
        """
        self.db_path = db_path
        
        # 确保数据库已初始化
        if not Path(db_path).exists():
            init_database(db_path, schema_path)
    
    def _get_connection(self):
        """获取数据库连接"""
        return get_database_connection(self.db_path)
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        return dict(row) if row else None
    
    # 提示词相关方法
    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """获取所有提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(pt.tag_name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
                GROUP BY p.id
                ORDER BY p.updated_at DESC
            """)
            
            prompts = []
            for row in cursor.fetchall():
                prompt = self._row_to_dict(row)
                # 处理标签
                if prompt['tags']:
                    prompt['tags'] = prompt['tags'].split(',')
                else:
                    prompt['tags'] = []
                
                # 获取版本信息
                prompt['versions'] = self._get_prompt_versions(prompt['id'])
                prompts.append(prompt)
            
            return prompts
        finally:
            conn.close()
    
    def _get_prompt_versions(self, prompt_id: str) -> List[Dict[str, Any]]:
        """获取提示词的所有版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, title, content, description, change_note, created_at
                FROM prompt_versions
                WHERE prompt_id = ?
                ORDER BY created_at ASC
            """, (prompt_id,))

            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def create_prompt_version(self, prompt_id: str, version_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建新版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return None

            now = datetime.now().isoformat()

            # 插入新版本
            cursor.execute("""
                INSERT INTO prompt_versions (
                    prompt_id, version, title, content, description, change_note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                version_data.get("version"),
                version_data.get("title"),
                version_data.get("content"),
                version_data.get("description", ""),
                version_data.get("change_note", ""),
                now
            ))

            # 更新提示词的当前版本和内容
            cursor.execute("""
                UPDATE prompts
                SET current_version = ?, title = ?, content = ?, description = ?, updated_at = ?
                WHERE id = ?
            """, (
                version_data.get("version"),
                version_data.get("title"),
                version_data.get("content"),
                version_data.get("description", ""),
                now,
                prompt_id
            ))

            conn.commit()

            return {
                "version": version_data.get("version"),
                "title": version_data.get("title"),
                "content": version_data.get("content"),
                "description": version_data.get("description", ""),
                "created_at": now,
                "change_note": version_data.get("change_note", "")
            }
        finally:
            conn.close()

    def switch_prompt_version(self, prompt_id: str, version: str) -> Optional[Dict[str, Any]]:
        """切换到指定版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return None

            # 查找指定版本
            cursor.execute("""
                SELECT version, title, content, description
                FROM prompt_versions
                WHERE prompt_id = ? AND version = ?
            """, (prompt_id, version))

            target_version = cursor.fetchone()
            if not target_version:
                return None

            target_version = self._row_to_dict(target_version)

            # 更新提示词到指定版本
            cursor.execute("""
                UPDATE prompts
                SET current_version = ?, title = ?, content = ?, description = ?, updated_at = ?
                WHERE id = ?
            """, (
                version,
                target_version["title"],
                target_version["content"],
                target_version["description"],
                datetime.now().isoformat(),
                prompt_id
            ))

            conn.commit()

            # 返回更新后的提示词
            return self.get_prompt_by_id(prompt_id)
        finally:
            conn.close()

    def delete_prompt_version(self, prompt_id: str, version: str) -> Dict[str, Any]:
        """删除指定版本"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return {"success": False, "error": "提示词不存在"}

            # 检查版本数量
            cursor.execute("""
                SELECT COUNT(*) as count FROM prompt_versions WHERE prompt_id = ?
            """, (prompt_id,))
            version_count = cursor.fetchone()['count']

            if version_count <= 1:
                return {"success": False, "error": "不能删除唯一的版本"}

            # 获取当前版本
            cursor.execute("SELECT current_version FROM prompts WHERE id = ?", (prompt_id,))
            current_version = cursor.fetchone()['current_version']

            if current_version == version:
                return {"success": False, "error": "不能删除当前版本，请先切换到其他版本"}

            # 删除版本
            cursor.execute("""
                DELETE FROM prompt_versions WHERE prompt_id = ? AND version = ?
            """, (prompt_id, version))

            if cursor.rowcount == 0:
                return {"success": False, "error": "版本不存在"}

            conn.commit()
            return {"success": True}
        finally:
            conn.close()
    
    def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 获取分类信息
            category_id = prompt_data.get("category_id")
            category_name = prompt_data.get("category", "其他")
            category_path = category_name

            if category_id:
                cursor.execute("SELECT name, path FROM categories WHERE id = ?", (category_id,))
                category = cursor.fetchone()
                if category:
                    category_name = category['name']
                    category_path = category['path']
                else:
                    # 如果分类不存在，设置为NULL以满足外键约束
                    category_id = None
            
            # 生成ID和时间戳
            prompt_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # 插入提示词
            cursor.execute("""
                INSERT INTO prompts (
                    id, title, content, description, category_id, 
                    category_name, category_path, usage_count, 
                    current_version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                prompt_data["title"],
                prompt_data["content"],
                prompt_data.get("description", ""),
                category_id,
                category_name,
                category_path,
                0,
                "1.0",
                now,
                now
            ))
            
            # 插入版本信息
            cursor.execute("""
                INSERT INTO prompt_versions (
                    prompt_id, version, title, content, description, change_note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                "1.0",
                prompt_data["title"],
                prompt_data["content"],
                prompt_data.get("description", ""),
                "初始版本",
                now
            ))
            
            # 添加标签
            tags = prompt_data.get("tags", [])
            for tag_name in tags:
                self._add_tag_to_prompt(cursor, prompt_id, tag_name)
            
            conn.commit()
            
            # 返回创建的提示词
            return self.get_prompt_by_id(prompt_id)
        finally:
            conn.close()
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, 
                       GROUP_CONCAT(pt.tag_name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
                WHERE p.id = ?
                GROUP BY p.id
            """, (prompt_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            prompt = self._row_to_dict(row)
            
            # 处理标签
            if prompt['tags']:
                prompt['tags'] = prompt['tags'].split(',')
            else:
                prompt['tags'] = []
            
            # 获取版本信息
            prompt['versions'] = self._get_prompt_versions(prompt_id)
            
            return prompt
        finally:
            conn.close()
    
    def update_prompt(self, prompt_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return None
            
            # 处理分类信息更新
            if "category_id" in update_data:
                category_id = update_data["category_id"]
                if category_id:
                    cursor.execute("SELECT name, path FROM categories WHERE id = ?", (category_id,))
                    category = cursor.fetchone()
                    if category:
                        update_data["category_name"] = category['name']
                        update_data["category_path"] = category['path']
                    else:
                        # 如果分类不存在，设置为NULL以满足外键约束
                        update_data["category_id"] = None
                        update_data["category_name"] = "其他"
                        update_data["category_path"] = "其他"
            
            # 构建更新SQL
            update_fields = []
            update_values = []
            
            for field, value in update_data.items():
                if field in ["title", "content", "description", "category_id", "category_name", "category_path"]:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(prompt_id)
                
                sql = f"UPDATE prompts SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, update_values)
                
                # 如果更新了标签，需要更新prompt_tags表
                if "tags" in update_data:
                    self._update_prompt_tags(cursor, prompt_id, update_data["tags"])
            
            conn.commit()
            return self.get_prompt_by_id(prompt_id)
        finally:
            conn.close()
    
    def _prompt_exists(self, cursor: sqlite3.Cursor, prompt_id: str) -> bool:
        """检查提示词是否存在"""
        cursor.execute("SELECT 1 FROM prompts WHERE id = ?", (prompt_id,))
        return cursor.fetchone() is not None
    
    def _add_tag_to_prompt(self, cursor: sqlite3.Cursor, prompt_id: str, tag_name: str):
        """为提示词添加标签"""
        if not tag_name or not tag_name.strip():
            return

        tag_name = tag_name.strip()
        now = datetime.now().isoformat()

        # 确保标签存在
        cursor.execute("SELECT name FROM tags WHERE name = ?", (tag_name,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO tags (id, name, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                tag_name,
                "#3B82F6",
                now,
                now
            ))

        # 添加关联
        cursor.execute("""
            INSERT OR IGNORE INTO prompt_tags (prompt_id, tag_name, created_at)
            VALUES (?, ?, ?)
        """, (prompt_id, tag_name, now))
    
    def _update_prompt_tags(self, cursor: sqlite3.Cursor, prompt_id: str, tags: List[str]):
        """更新提示词的标签"""
        # 删除现有标签关联
        cursor.execute("DELETE FROM prompt_tags WHERE prompt_id = ?", (prompt_id,))
        
        # 添加新标签关联
        for tag_name in tags:
            self._add_tag_to_prompt(cursor, prompt_id, tag_name)
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """删除提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return False
            
            # 删除提示词（级联删除会自动删除版本和标签关联）
            cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
            
            conn.commit()
            return True
        finally:
            conn.close()
    
    def use_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """使用提示词（增加使用计数）"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 检查提示词是否存在
            if not self._prompt_exists(cursor, prompt_id):
                return None
            
            # 增加使用计数
            cursor.execute("""
                UPDATE prompts 
                SET usage_count = usage_count + 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), prompt_id))
            
            conn.commit()
            return self.get_prompt_by_id(prompt_id)
        finally:
            conn.close()
    
    # 分类相关方法
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """获取所有分类"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM categories
                ORDER BY level, name
            """)
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_categories_tree(self) -> List[Dict[str, Any]]:
        """获取分类树结构"""
        categories = self.get_all_categories()
        
        # 构建分类字典，便于查找
        category_dict = {cat["id"]: cat for cat in categories}
        
        # 为每个分类添加children属性
        for cat in categories:
            cat["children"] = []
        
        # 构建树结构
        root_categories = []
        for cat in categories:
            if cat["parent_id"] is None:
                root_categories.append(cat)
            else:
                parent = category_dict.get(cat["parent_id"])
                if parent:
                    parent["children"].append(cat)
        
        return root_categories
    
    def _build_category_path(self, category_id: str, categories_dict: Dict[str, Dict[str, Any]]) -> str:
        """构建分类的完整路径"""
        if category_id not in categories_dict:
            return ""
        
        category = categories_dict[category_id]
        if category["parent_id"] is None:
            return category["name"]
        
        parent_path = self._build_category_path(category["parent_id"], categories_dict)
        return f"{parent_path}/{category['name']}" if parent_path else category["name"]
    
    def _update_category_paths(self):
        """更新所有分类的路径"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 获取所有分类
            cursor.execute("SELECT * FROM categories")
            categories = [self._row_to_dict(row) for row in cursor.fetchall()]
            categories_dict = {cat["id"]: cat for cat in categories}
            
            # 更新路径
            for category in categories:
                path = self._build_category_path(category["id"], categories_dict)
                cursor.execute("""
                    UPDATE categories SET path = ? WHERE id = ?
                """, (path, category["id"]))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_category_descendants(self, category_id: str) -> List[str]:
        """获取分类的所有后代分类ID（公开方法）"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            descendants = []
            
            def find_children(parent_id):
                cursor.execute("SELECT id FROM categories WHERE parent_id = ?", (parent_id,))
                children = cursor.fetchall()
                for child in children:
                    descendants.append(child['id'])
                    find_children(child['id'])
            
            find_children(category_id)
            return descendants
        finally:
            conn.close()
    
    def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新分类"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            parent_id = category_data.get("parent_id")
            level = 1
            
            # 计算层级
            if parent_id:
                cursor.execute("SELECT level FROM categories WHERE id = ?", (parent_id,))
                parent = cursor.fetchone()
                if parent:
                    level = parent['level'] + 1
                    if level > 5:  # 最多支持5级
                        raise ValueError("分类层级不能超过5级")
            
            # 生成ID
            category_id = str(uuid.uuid4())
            
            # 插入分类
            cursor.execute("""
                INSERT INTO categories (
                    id, name, color, description, parent_id, level, path, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category_id,
                category_data["name"],
                category_data.get("color", "#6B7280"),
                category_data.get("description", ""),
                parent_id,
                level,
                "",  # 路径稍后计算
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # 重新计算所有分类的路径
            self._update_category_paths()
            
            # 返回创建的分类
            return self.get_category_by_id(category_id)
        finally:
            conn.close()
    
    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取分类"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        finally:
            conn.close()
    
    def update_category(self, category_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新分类"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 检查分类是否存在
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            category = cursor.fetchone()
            if not category:
                return None
            
            category = self._row_to_dict(category)
            old_name = category["name"]
            old_path = category.get("path", old_name)
            
            # 检查父分类变更
            if "parent_id" in update_data:
                new_parent_id = update_data["parent_id"]
                
                # 检查是否会造成循环引用
                if new_parent_id and self._would_create_cycle(category_id, new_parent_id):
                    raise ValueError("不能将分类移动到其子分类下，这会造成循环引用")
                
                # 计算新的层级
                if new_parent_id:
                    cursor.execute("SELECT level FROM categories WHERE id = ?", (new_parent_id,))
                    parent = cursor.fetchone()
                    if parent:
                        new_level = parent['level'] + 1
                        if new_level > 5:
                            raise ValueError("移动后的分类层级不能超过5级")
                        update_data["level"] = new_level
                else:
                    update_data["level"] = 1
            
            # 构建更新SQL
            update_fields = []
            update_values = []
            
            for field, value in update_data.items():
                if field in ["name", "color", "description", "parent_id", "level"]:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(category_id)
                
                sql = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, update_values)
            
            # 重新计算所有分类的路径
            self._update_category_paths()
            
            # 更新提示词中的分类信息
            updated_category = self.get_category_by_id(category_id)
            new_path = updated_category["path"]
            if old_path != new_path:
                cursor.execute("""
                    UPDATE prompts
                    SET category_name = ?, category_path = ?, updated_at = ?
                    WHERE category_id = ? OR category_name = ?
                """, (
                    updated_category["name"],
                    new_path,
                    datetime.now().isoformat(),
                    category_id,
                    old_name
                ))
            
            conn.commit()
            return updated_category
        finally:
            conn.close()
    
    def _would_create_cycle(self, category_id: str, new_parent_id: str) -> bool:
        """检查是否会造成循环引用"""
        if category_id == new_parent_id:
            return True
        
        # 获取所有后代分类
        descendants = self.get_category_descendants(category_id)
        return new_parent_id in descendants
    
    def delete_category(self, category_id: str) -> Dict[str, Any]:
        """删除分类（返回影响信息，不实际删除）"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 找到要删除的分类
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            category = cursor.fetchone()
            if not category:
                return {"success": False, "error": "分类不存在"}
            
            category = self._row_to_dict(category)
            
            # 检查是否有子分类
            cursor.execute("SELECT COUNT(*) as count FROM categories WHERE parent_id = ?", (category_id,))
            child_count = cursor.fetchone()['count']
            
            # 检查关联的提示词
            cursor.execute("""
                SELECT COUNT(*) as count FROM prompts
                WHERE category_id = ? OR category_name = ?
            """, (category_id, category["name"]))
            affected_prompts_count = cursor.fetchone()['count']
            
            # 获取子分类名称
            cursor.execute("SELECT name FROM categories WHERE parent_id = ?", (category_id,))
            child_categories = [self._row_to_dict(row)['name'] for row in cursor.fetchall()]
            
            # 返回删除影响信息，让前端决定是否继续
            return {
                "success": False,
                "requires_confirmation": True,
                "category_name": category["name"],
                "child_categories_count": child_count,
                "affected_prompts_count": affected_prompts_count,
                "child_categories": child_categories
            }
        finally:
            conn.close()
    
    def force_delete_category(self, category_id: str) -> Dict[str, Any]:
        """强制删除分类（已确认）"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 找到要删除的分类
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            category = cursor.fetchone()
            if not category:
                return {"success": False, "error": "分类不存在"}
            
            category = self._row_to_dict(category)
            
            # 获取所有子分类（包括递归的）
            all_descendants = self.get_category_descendants(category_id)
            categories_to_delete = [category_id] + all_descendants
            
            # 找到"其他"分类
            cursor.execute("SELECT * FROM categories WHERE name = '其他'")
            other_category = cursor.fetchone()
            other_category = self._row_to_dict(other_category) if other_category else None
            
            # 移动关联的提示词到"其他"分类
            affected_prompts_count = 0
            if other_category:
                placeholders = ','.join(['?' for _ in categories_to_delete])
                cursor.execute(f"""
                    UPDATE prompts
                    SET category_id = ?, category_name = ?, category_path = ?, updated_at = ?
                    WHERE category_id IN ({placeholders}) OR category_name = ?
                """, [other_category["id"], other_category["name"], other_category["path"],
                       datetime.now().isoformat()] + categories_to_delete + [category["name"]])
                affected_prompts_count = cursor.rowcount
            
            # 删除分类及其所有子分类
            placeholders = ','.join(['?' for _ in categories_to_delete])
            cursor.execute(f"DELETE FROM categories WHERE id IN ({placeholders})", categories_to_delete)
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            return {
                "success": True,
                "deleted_categories_count": deleted_count,
                "affected_prompts_count": affected_prompts_count
            }
        finally:
            conn.close()
    
    # 标签相关方法
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 从prompts中提取实际使用的标签
            cursor.execute("SELECT DISTINCT tag_name FROM prompt_tags")
            used_tags = {row['tag_name'] for row in cursor.fetchall()}
            
            # 获取metadata中的标签定义
            cursor.execute("SELECT * FROM tags")
            metadata_tags = {tag["name"]: self._row_to_dict(tag) for tag in cursor.fetchall()}
            
            # 合并：确保所有使用的标签都有定义
            result_tags = []
            for tag_name in used_tags:
                if tag_name in metadata_tags:
                    # 使用metadata中的定义
                    result_tags.append(metadata_tags[tag_name])
                else:
                    # 为没有定义的标签创建默认定义
                    tag_def = {
                        "id": f"auto-{str(uuid.uuid4())[:8]}",
                        "name": tag_name,
                        "color": "#3B82F6"  # 默认蓝色
                    }
                    result_tags.append(tag_def)
                    # 同时添加到metadata中
                    cursor.execute("""
                        INSERT INTO tags (id, name, color, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        tag_def["id"],
                        tag_def["name"],
                        tag_def["color"],
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
            
            # 如果有新标签添加到metadata，保存数据
            if len(result_tags) > len(metadata_tags):
                conn.commit()
            
            return result_tags
        finally:
            conn.close()
    
    def create_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新标签"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            tag_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO tags (id, name, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                tag_id,
                tag_data["name"],
                tag_data.get("color", "#3B82F6"),
                now,
                now
            ))
            
            conn.commit()
            
            return {
                "id": tag_id,
                "name": tag_data["name"],
                "color": tag_data.get("color", "#3B82F6"),
                "created_at": now,
                "updated_at": now
            }
        finally:
            conn.close()
    
    def update_tag(self, tag_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新标签"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 获取旧标签信息
            cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
            old_tag = cursor.fetchone()
            if not old_tag:
                return None
            
            old_tag = self._row_to_dict(old_tag)
            old_name = old_tag["name"]
            
            # 构建更新SQL
            update_fields = []
            update_values = []
            
            for field, value in update_data.items():
                if field in ["name", "color"]:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(tag_id)
                
                sql = f"UPDATE tags SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, update_values)
            
            # 如果标签名称发生变化，更新所有使用该标签的提示词
            if "name" in update_data and update_data["name"] != old_name:
                cursor.execute("""
                    UPDATE prompt_tags SET tag_name = ? WHERE tag_name = ?
                """, (update_data["name"], old_name))
            
            conn.commit()
            
            # 返回更新后的标签
            cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
            return self._row_to_dict(cursor.fetchone())
        finally:
            conn.close()
    
    def delete_tag(self, tag_id: str) -> Dict[str, Any]:
        """删除标签"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 找到要删除的标签
            cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
            tag = cursor.fetchone()
            if not tag:
                return False
            
            tag_name = tag['name']
            
            # 处理关联的提示词：从所有提示词中移除该标签
            cursor.execute("DELETE FROM prompt_tags WHERE tag_name = ?", (tag_name,))
            affected_count = cursor.rowcount
            
            # 删除标签
            cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            
            conn.commit()
            
            return {"success": True, "affected_prompts": affected_count}
        finally:
            conn.close()
    
    def search_prompts(self, query: str = "", category: str = "", category_id: str = "") -> List[Dict[str, Any]]:
        """搜索提示词"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if query:
                conditions.append("(p.title LIKE ? OR p.content LIKE ? OR p.description LIKE ?)")
                query_param = f"%{query}%"
                params.extend([query_param, query_param, query_param])
            
            if category_id:
                # 按分类ID搜索，包括其子分类
                descendants = self.get_category_descendants(category_id)
                target_category_ids = [category_id] + descendants
                placeholders = ','.join(['?' for _ in target_category_ids])
                conditions.append(f"p.category_id IN ({placeholders})")
                params.extend(target_category_ids)
            elif category:
                # 按分类名称搜索（向后兼容）
                conditions.append("p.category_name = ?")
                params.append(category)
            
            # 构建SQL
            sql = """
                SELECT p.*, 
                       GROUP_CONCAT(pt.tag_name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
            """
            
            if conditions:
                sql += f" WHERE {' AND '.join(conditions)}"
            
            sql += " GROUP BY p.id ORDER BY p.updated_at DESC"
            
            cursor.execute(sql, params)
            
            prompts = []
            for row in cursor.fetchall():
                prompt = self._row_to_dict(row)
                # 处理标签
                if prompt['tags']:
                    prompt['tags'] = prompt['tags'].split(',')
                else:
                    prompt['tags'] = []
                prompts.append(prompt)
            
            return prompts
        finally:
            conn.close()
    
    # 数据管理方法
    def backup_data(self) -> str:
        """备份数据（导出为JSON格式）"""
        conn = self._get_connection()
        try:
            # 获取所有数据
            prompts = self.get_all_prompts()
            categories = self.get_all_categories()
            tags = self.get_all_tags()
            
            # 获取设置
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            settings = {self._row_to_dict(row)['key']: self._row_to_dict(row)['value'] 
                       for row in cursor.fetchall()}
            
            # 构建备份数据
            backup_data = {
                "prompts": prompts,
                "metadata": {
                    "categories": categories,
                    "tags": tags,
                    "settings": settings
                },
                "backup_time": datetime.now().isoformat()
            }
            
            # 创建备份目录
            backup_dir = Path("data/backup")
            backup_dir.mkdir(exist_ok=True)
            
            # 保存备份文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"prompts_sqlite_backup_{timestamp}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return str(backup_file)
        finally:
            conn.close()
    
    def clear_all_data(self) -> str:
        """清空所有数据，但保留默认分类"""
        # 先备份数据
        backup_file = self.backup_data()
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 清空所有表
            cursor.execute("DELETE FROM prompt_tags")
            cursor.execute("DELETE FROM prompt_versions")
            cursor.execute("DELETE FROM prompts")
            cursor.execute("DELETE FROM tags")
            cursor.execute("DELETE FROM categories")
            
            # 重新插入默认分类
            default_categories = [
                ("1", "编程", "#3B82F6", "编程相关提示词", None, 1, "编程"),
                ("2", "写作", "#10B981", "写作相关提示词", None, 1, "写作"),
                ("3", "分析", "#F59E0B", "分析相关提示词", None, 1, "分析"),
                ("4", "创意", "#8B5CF6", "创意相关提示词", None, 1, "创意"),
                ("5", "商业", "#EF4444", "商业相关提示词", None, 1, "商业"),
                ("6", "教育", "#06B6D4", "教育相关提示词", None, 1, "教育"),
                ("7", "其他", "#6B7280", "其他类型提示词", None, 1, "其他")
            ]
            
            now = datetime.now().isoformat()
            for cat_id, name, color, description, parent_id, level, path in default_categories:
                cursor.execute("""
                    INSERT INTO categories (
                        id, name, color, description, parent_id, level, path, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (cat_id, name, color, description, parent_id, level, path, now, now))
            
            # 更新设置
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?), (?, ?, ?)
            """, (
                "version", "2.0", now,
                "last_updated", now, now
            ))
            
            conn.commit()
            return backup_file
        finally:
            conn.close()
    
    def load_test_data(self) -> str:
        """加载测试数据"""
        # 先备份数据
        backup_file = self.backup_data()

        try:
            examples_dir = Path("data/examples")
            example_prompts_file = examples_dir / "prompts.json"

            if example_prompts_file.exists():
                with open(example_prompts_file, 'r', encoding='utf-8') as f:
                    example_data = json.load(f)

                # 清空现有提示词
                conn = self._get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM prompt_tags")
                    cursor.execute("DELETE FROM prompt_versions")
                    cursor.execute("DELETE FROM prompts")
                    conn.commit()
                finally:
                    conn.close()

                # 加载测试数据
                for prompt_data in example_data.get("prompts", []):
                    self.create_prompt(prompt_data)

                return backup_file
            else:
                raise FileNotFoundError("测试数据文件不存在")
        except Exception as e:
            raise Exception(f"加载测试数据失败: {str(e)}")

    def import_prompts(self, prompts_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        导入提示词列表

        Args:
            prompts_data: 要导入的提示词列表

        Returns:
            包含统计信息的字典: {success_count, update_count, skip_count}
        """
        success_count = 0
        skip_count = 0
        update_count = 0

        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            for prompt in prompts_data:
                # 验证必需字段
                if 'id' not in prompt or 'title' not in prompt or 'content' not in prompt:
                    skip_count += 1
                    continue

                prompt_id = prompt['id']

                # 检查提示词是否存在
                existing_prompt = self.get_prompt_by_id(prompt_id)

                if existing_prompt:
                    # 更新现有提示词（保留usage_count）
                    update_data = {
                        'title': prompt['title'],
                        'content': prompt['content'],
                        'description': prompt.get('description', ''),
                        'category_id': prompt.get('category_id'),
                        'tags': prompt.get('tags', [])
                    }

                    self.update_prompt(prompt_id, update_data)

                    # 导入版本信息（如果有）
                    if 'versions' in prompt:
                        self._import_prompt_versions(cursor, prompt_id, prompt['versions'])

                    update_count += 1
                else:
                    # 创建新提示词
                    # 使用传入的ID而不是生成新ID
                    now = datetime.now().isoformat()

                    # 获取分类信息
                    category_id = prompt.get("category_id")
                    category_name = prompt.get("category", "其他")
                    category_path = category_name

                    if category_id:
                        cursor.execute("SELECT name, path FROM categories WHERE id = ?", (category_id,))
                        category = cursor.fetchone()
                        if category:
                            category_name = category['name']
                            category_path = category['path']

                    # 插入提示词
                    cursor.execute("""
                        INSERT INTO prompts (
                            id, title, content, description, category_id,
                            category_name, category_path, usage_count,
                            current_version, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prompt_id,
                        prompt["title"],
                        prompt["content"],
                        prompt.get("description", ""),
                        category_id,
                        category_name,
                        category_path,
                        prompt.get("usage_count", 0),
                        prompt.get("current_version", "1.0"),
                        prompt.get("created_at", now),
                        prompt.get("updated_at", now)
                    ))

                    # 插入版本信息
                    if 'versions' in prompt and prompt['versions']:
                        self._import_prompt_versions(cursor, prompt_id, prompt['versions'])
                    else:
                        # 创建默认版本
                        cursor.execute("""
                            INSERT INTO prompt_versions (
                                prompt_id, version, title, content, description, change_note, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            prompt_id,
                            "1.0",
                            prompt["title"],
                            prompt["content"],
                            prompt.get("description", ""),
                            "导入版本",
                            prompt.get("created_at", now)
                        ))

                    # 添加标签
                    tags = prompt.get("tags", [])
                    for tag_name in tags:
                        self._add_tag_to_prompt(cursor, prompt_id, tag_name)

                    success_count += 1

            conn.commit()

            return {
                "success_count": success_count,
                "update_count": update_count,
                "skip_count": skip_count
            }
        finally:
            conn.close()

    def _import_prompt_versions(self, cursor: sqlite3.Cursor, prompt_id: str, versions: List[Dict[str, Any]]):
        """导入提示词的版本信息"""
        # 先删除现有版本
        cursor.execute("DELETE FROM prompt_versions WHERE prompt_id = ?", (prompt_id,))

        # 插入新版本
        for version in versions:
            cursor.execute("""
                INSERT INTO prompt_versions (
                    prompt_id, version, title, content, description, change_note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt_id,
                version.get("version", "1.0"),
                version.get("title", ""),
                version.get("content", ""),
                version.get("description", ""),
                version.get("change_note", ""),
                version.get("created_at", datetime.now().isoformat())
            ))