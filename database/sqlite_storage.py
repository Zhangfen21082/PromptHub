#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptHub SQLite数据库存储类
替换原有的FileStorage类，提供相同接口但使用SQLite作为后端存储
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
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
                       GROUP_CONCAT(t.name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
                LEFT JOIN tags t ON pt.tag_id = t.id
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
                       GROUP_CONCAT(t.name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
                LEFT JOIN tags t ON pt.tag_id = t.id
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

        # 确保标签存在，获取或创建 tag_id
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = cursor.fetchone()

        if result:
            tag_id = result['id']
        else:
            tag_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO tags (id, name, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                tag_id,
                tag_name,
                "#3B82F6",
                now,
                now
            ))

        # 添加关联（使用 tag_id）
        cursor.execute("""
            INSERT OR IGNORE INTO prompt_tags (prompt_id, tag_id, created_at)
            VALUES (?, ?, ?)
        """, (prompt_id, tag_id, now))
    
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
    
    def _update_category_paths(self, cursor=None):
        """更新所有分类的路径"""
        # 如果没有传入cursor，创建新连接（向后兼容）
        own_connection = cursor is None
        if own_connection:
            conn = self._get_connection()
            cursor = conn.cursor()

        try:
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

            # 只有在自己创建连接时才commit和close
            if own_connection:
                conn.commit()
        finally:
            if own_connection:
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

            # 重新计算所有分类的路径（传入cursor避免创建新连接）
            self._update_category_paths(cursor)

            # 获取创建的分类（使用当前cursor）
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            created_category = self._row_to_dict(cursor.fetchone())

            conn.commit()

            # 返回创建的分类
            return created_category
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

            # 重新计算所有分类的路径（传入cursor避免创建新连接）
            self._update_category_paths(cursor)

            # 获取更新后的分类信息（使用当前cursor）
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            updated_category = self._row_to_dict(cursor.fetchone())
            new_path = updated_category["path"]

            # 更新提示词中的分类信息
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

            # 找到"未分类"分类
            cursor.execute("SELECT * FROM categories WHERE id = '0' OR name = '未分类'")
            uncategorized = cursor.fetchone()
            uncategorized = self._row_to_dict(uncategorized) if uncategorized else None

            # 移动关联的提示词到"未分类"
            affected_prompts_count = 0
            if uncategorized:
                placeholders = ','.join(['?' for _ in categories_to_delete])
                cursor.execute(f"""
                    UPDATE prompts
                    SET category_id = ?, category_name = ?, category_path = ?, updated_at = ?
                    WHERE category_id IN ({placeholders})
                """, [uncategorized["id"], uncategorized["name"], uncategorized["path"],
                       datetime.now().isoformat()] + categories_to_delete)
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

            # 直接从tags表获取所有标签
            cursor.execute("SELECT * FROM tags ORDER BY created_at DESC")
            tags = [self._row_to_dict(row) for row in cursor.fetchall()]

            return tags
        finally:
            conn.close()
    
    def create_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新标签"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            tag_name = tag_data["name"]

            # 检查标签是否已存在
            cursor.execute("SELECT * FROM tags WHERE name = ?", (tag_name,))
            existing_tag = cursor.fetchone()

            if existing_tag:
                # 如果标签已存在，返回已有标签信息
                return self._row_to_dict(existing_tag)

            tag_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO tags (id, name, color, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                tag_id,
                tag_name,
                tag_data.get("color", "#3B82F6"),
                now,
                now
            ))

            conn.commit()

            return {
                "id": tag_id,
                "name": tag_name,
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
            new_name = update_data.get("name", old_name)

            # 如果标签名称发生变化，先检查新名称是否已存在（排除当前标签）
            if new_name != old_name:
                cursor.execute("SELECT id FROM tags WHERE name = ? AND id != ?", (new_name, tag_id))
                if cursor.fetchone():
                    raise ValueError(f"标签名称 '{new_name}' 已存在")

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

            conn.commit()

            # 返回更新后的标签
            cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
            return self._row_to_dict(cursor.fetchone())
        except ValueError as e:
            conn.rollback()
            raise e
        except Exception as e:
            conn.rollback()
            raise e
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

            # 统计受影响的提示词数量（在删除前）
            cursor.execute("SELECT COUNT(DISTINCT prompt_id) FROM prompt_tags WHERE tag_id = ?", (tag_id,))
            affected_count = cursor.fetchone()[0]

            # 删除标签（由于有 ON DELETE CASCADE，会自动删除 prompt_tags 中的关联）
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
                       GROUP_CONCAT(t.name) as tags
                FROM prompts p
                LEFT JOIN prompt_tags pt ON p.id = pt.prompt_id
                LEFT JOIN tags t ON pt.tag_id = t.id
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
        """备份数据（复制数据库文件）"""
        import shutil

        # 创建备份目录
        backup_dir = Path("data/backup")
        backup_dir.mkdir(exist_ok=True)

        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"prompthub_backup_{timestamp}.db"

        # 复制数据库文件
        shutil.copy2(self.db_path, backup_file)

        return str(backup_file)

    def export_database(self) -> str:
        """导出数据库文件"""
        import shutil

        # 创建导出目录
        export_dir = Path("data/exports")
        export_dir.mkdir(exist_ok=True)

        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_dir / f"prompthub_export_{timestamp}.db"

        # 复制数据库文件
        shutil.copy2(self.db_path, export_file)

        return str(export_file)

    def import_database(self, db_file_path: str) -> str:
        """导入数据库文件（替换当前数据库）"""
        import shutil

        # 先备份当前数据库
        backup_file = self.backup_data()

        # 验证导入文件是否存在
        import_file = Path(db_file_path)
        if not import_file.exists():
            raise FileNotFoundError(f"导入文件不存在: {db_file_path}")

        # 验证是否为有效的SQLite数据库
        try:
            test_conn = sqlite3.connect(str(import_file))
            # 检查是否包含必要的表
            cursor = test_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'")
            if not cursor.fetchone():
                test_conn.close()
                raise ValueError("导入的文件不是有效的PromptHub数据库（缺少prompts表）")
            test_conn.close()
        except sqlite3.Error as e:
            raise ValueError(f"导入的文件不是有效的SQLite数据库: {str(e)}")

        # 替换当前数据库
        shutil.copy2(import_file, self.db_path)

        return backup_file

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
                ("0", "未分类", "#9CA3AF", "未分类的提示词", None, 1, "未分类")
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
        """加载测试数据 - 生成完善的测试数据用于开发"""
        # 先备份数据
        backup_file = self.backup_data()

        try:
            # 清空现有数据（保留未分类）
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM prompt_tags")
                cursor.execute("DELETE FROM prompt_versions")
                cursor.execute("DELETE FROM prompts")
                cursor.execute("DELETE FROM tags")
                cursor.execute("DELETE FROM categories WHERE id != '0'")
                conn.commit()
            finally:
                conn.close()

            # 1. 创建分类树结构
            # 一级分类
            cat_programming = self.create_category({
                "name": "编程开发",
                "color": "#3B82F6",
                "description": "编程和软件开发相关提示词"
            })

            cat_writing = self.create_category({
                "name": "写作创作",
                "color": "#10B981",
                "description": "写作、文案、内容创作"
            })

            cat_business = self.create_category({
                "name": "商业分析",
                "color": "#EF4444",
                "description": "商业、市场、数据分析"
            })

            cat_learning = self.create_category({
                "name": "学习教育",
                "color": "#8B5CF6",
                "description": "教育、学习、知识分享"
            })

            # 二级分类 - 编程开发
            cat_python = self.create_category({
                "name": "Python",
                "color": "#3776AB",
                "description": "Python 编程相关",
                "parent_id": cat_programming["id"]
            })

            cat_web = self.create_category({
                "name": "Web开发",
                "color": "#F59E0B",
                "description": "前端和后端Web开发",
                "parent_id": cat_programming["id"]
            })

            cat_ai = self.create_category({
                "name": "AI/机器学习",
                "color": "#06B6D4",
                "description": "人工智能和机器学习",
                "parent_id": cat_programming["id"]
            })

            # 三级分类 - Web开发
            cat_frontend = self.create_category({
                "name": "前端开发",
                "color": "#F97316",
                "description": "HTML/CSS/JavaScript",
                "parent_id": cat_web["id"]
            })

            cat_backend = self.create_category({
                "name": "后端开发",
                "color": "#84CC16",
                "description": "服务器端开发",
                "parent_id": cat_web["id"]
            })

            # 二级分类 - 写作创作
            cat_article = self.create_category({
                "name": "文章写作",
                "color": "#14B8A6",
                "description": "博客、技术文章等",
                "parent_id": cat_writing["id"]
            })

            cat_marketing = self.create_category({
                "name": "营销文案",
                "color": "#EC4899",
                "description": "广告、营销、推广文案",
                "parent_id": cat_writing["id"]
            })

            # 2. 创建标签
            tags_data = [
                {"name": "代码生成", "color": "#3B82F6"},
                {"name": "代码审查", "color": "#10B981"},
                {"name": "Bug修复", "color": "#EF4444"},
                {"name": "性能优化", "color": "#F59E0B"},
                {"name": "API设计", "color": "#8B5CF6"},
                {"name": "SEO优化", "color": "#06B6D4"},
                {"name": "内容创作", "color": "#EC4899"},
                {"name": "数据分析", "color": "#14B8A6"},
                {"name": "教程编写", "color": "#F97316"},
                {"name": "文档生成", "color": "#84CC16"},
            ]

            for tag_data in tags_data:
                self.create_tag(tag_data)

            # 3. 创建提示词（包含详细内容）
            prompts_data = [
                {
                    "title": "Python 代码审查助手",
                    "content": """你是一位经验丰富的 Python 开发者。请仔细审查以下代码，并提供：

1. 代码质量评估
2. 潜在的 bug 或问题
3. 性能优化建议
4. 最佳实践建议
5. 安全性问题

代码：
{code}

请提供详细的分析和改进建议。""",
                    "description": "帮助审查 Python 代码，发现问题并提供优化建议",
                    "category_id": cat_python["id"],
                    "tags": ["代码审查", "Bug修复", "性能优化"]
                },
                {
                    "title": "Python 数据分析脚本生成器",
                    "content": """请根据以下需求生成 Python 数据分析脚本：

需求：{requirements}

请使用 pandas、numpy、matplotlib 等库，生成包含以下内容的完整脚本：
1. 数据加载和预处理
2. 数据探索性分析
3. 数据可视化
4. 统计分析
5. 结果总结""",
                    "description": "自动生成数据分析脚本",
                    "category_id": cat_python["id"],
                    "tags": ["代码生成", "数据分析"]
                },
                {
                    "title": "React 组件生成器",
                    "content": """作为一名资深的 React 开发者，请根据以下需求创建一个 React 组件：

组件需求：{requirements}

请提供完整的组件代码（使用 TypeScript）和使用示例。""",
                    "description": "快速生成符合最佳实践的 React 组件",
                    "category_id": cat_frontend["id"],
                    "tags": ["代码生成", "API设计"]
                },
                {
                    "title": "CSS 性能优化顾问",
                    "content": """你是 CSS 性能优化专家。请分析以下 CSS 代码并提供优化建议：

CSS 代码：
{css_code}

请提供性能问题识别和具体优化方案。""",
                    "description": "分析和优化 CSS 性能",
                    "category_id": cat_frontend["id"],
                    "tags": ["性能优化", "代码审查"]
                },
                {
                    "title": "RESTful API 设计助手",
                    "content": """作为 API 设计专家，请为以下业务场景设计 RESTful API：

业务场景：{business_scenario}

请提供完整的 API 端点设计和文档。""",
                    "description": "设计符合最佳实践的 RESTful API",
                    "category_id": cat_backend["id"],
                    "tags": ["API设计", "文档生成"]
                },
                {
                    "title": "机器学习模型选择顾问",
                    "content": """你是机器学习专家。根据以下问题描述，推荐合适的机器学习模型并提供实现示例。

问题描述：
- 任务类型：{task_type}
- 数据规模：{data_size}""",
                    "description": "根据具体场景推荐合适的机器学习模型",
                    "category_id": cat_ai["id"],
                    "tags": ["数据分析", "代码生成"]
                },
                {
                    "title": "技术博客文章生成器",
                    "content": """你是一位优秀的技术博客作者。请根据主题创作一篇技术文章。

主题：{topic}

请包含吸引人的标题、清晰的技术讲解和实用的案例。""",
                    "description": "生成高质量的技术博客文章",
                    "category_id": cat_article["id"],
                    "tags": ["内容创作", "SEO优化", "教程编写"]
                },
                {
                    "title": "教程文档编写助手",
                    "content": """作为技术文档专家，请为技术主题创建完整的教程文档。

主题：{topic}

请提供清晰的目录结构和分步骤讲解。""",
                    "description": "创建结构化的技术教程文档",
                    "category_id": cat_article["id"],
                    "tags": ["教程编写", "文档生成", "内容创作"]
                },
                {
                    "title": "产品营销文案生成器",
                    "content": """你是创意营销文案专家。请为产品创作营销文案。

产品信息：
- 产品名称：{product_name}
- 核心卖点：{key_features}

请提供有创意、有说服力的文案。""",
                    "description": "创作有吸引力的产品营销文案",
                    "category_id": cat_marketing["id"],
                    "tags": ["内容创作", "SEO优化"]
                },
                {
                    "title": "商业数据分析报告生成器",
                    "content": """你是资深的商业数据分析师。请根据数据生成商业分析报告。

数据描述：{data_description}

请提供执行摘要、数据分析和商业建议。""",
                    "description": "生成专业的商业数据分析报告",
                    "category_id": cat_business["id"],
                    "tags": ["数据分析", "文档生成"]
                },
                {
                    "title": "概念解释专家",
                    "content": """你是优秀的教育者。请用简单易懂的方式解释概念。

概念：{concept}

请提供简明定义、通俗比喻和实际应用场景。""",
                    "description": "用通俗易懂的方式解释复杂概念",
                    "category_id": cat_learning["id"],
                    "tags": ["教程编写", "内容创作"]
                },
                {
                    "title": "问题解决框架",
                    "content": """你是问题解决专家。请使用结构化的方法分析和解决问题。

问题描述：{problem}

请按框架提供系统化、可操作的分析。""",
                    "description": "使用结构化方法分析和解决问题",
                    "category_id": "0",
                    "tags": ["数据分析"]
                },
            ]

            created_prompts = []
            for i, prompt_data in enumerate(prompts_data):
                prompt = self.create_prompt(prompt_data)
                created_prompts.append(prompt)

                # 为部分提示词添加版本历史
                if i % 3 == 0:
                    self.create_prompt_version(
                        prompt["id"],
                        {
                            "version": "1.1",
                            "title": prompt_data["title"],
                            "content": prompt_data["content"] + "\n\n更新：添加了更多细节。",
                            "description": prompt_data["description"] + "（已优化）",
                            "change_note": "优化了提示词结构"
                        }
                    )

                    self.create_prompt_version(
                        prompt["id"],
                        {
                            "version": "1.2",
                            "title": prompt_data["title"] + " Pro",
                            "content": prompt_data["content"] + "\n\n更新：增强了输出质量。",
                            "description": prompt_data["description"] + "（专业版）",
                            "change_note": "重大更新：增强了输出质量"
                        }
                    )

                    self.update_prompt(prompt["id"], {"current_version": "1.2"})

            # 4. 随机设置使用次数
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE prompts SET usage_count = ABS(RANDOM() % 50)")
                conn.commit()
            finally:
                conn.close()

            return backup_file
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