import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .models import Prompt, Category, Tag, PromptCreate, PromptUpdate, CategoryCreate, CategoryUpdate, TagCreate, TagUpdate


class FileStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.prompts_file = self.data_dir / "prompts.json"
        self.categories_file = self.data_dir / "categories.json"
        self.tags_file = self.data_dir / "tags.json"
        
        # 初始化数据文件
        self._init_data_files()
    
    def _init_data_files(self):
        """初始化数据文件，如果不存在则创建默认数据"""
        if not self.prompts_file.exists():
            self._save_prompts([])
        
        if not self.categories_file.exists():
            default_categories = [
                {"id": "1", "name": "编程", "color": "#3B82F6", "prompt_count": 0},
                {"id": "2", "name": "写作", "color": "#10B981", "prompt_count": 0},
                {"id": "3", "name": "分析", "color": "#F59E0B", "prompt_count": 0},
                {"id": "4", "name": "创意", "color": "#8B5CF6", "prompt_count": 0},
                {"id": "5", "name": "商业", "color": "#EF4444", "prompt_count": 0},
                {"id": "6", "name": "教育", "color": "#06B6D4", "prompt_count": 0},
                {"id": "7", "name": "其他", "color": "#6B7280", "prompt_count": 0}
            ]
            self._save_categories(default_categories)
        
        if not self.tags_file.exists():
            self._save_tags([])
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        """加载提示词数据"""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('prompts', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_prompts(self, prompts: List[Dict[str, Any]]):
        """保存提示词数据"""
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self) -> List[Dict[str, Any]]:
        """加载分类数据"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('categories', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_categories(self, categories: List[Dict[str, Any]]):
        """保存分类数据"""
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump({'categories': categories}, f, ensure_ascii=False, indent=2)
    
    def _load_tags(self) -> List[Dict[str, Any]]:
        """加载标签数据"""
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tags', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_tags(self, tags: List[Dict[str, Any]]):
        """保存标签数据"""
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump({'tags': tags}, f, ensure_ascii=False, indent=2)
    
    # 提示词相关方法
    def get_all_prompts(self) -> List[Prompt]:
        """获取所有提示词"""
        prompts_data = self._load_prompts()
        return [Prompt(**prompt) for prompt in prompts_data]
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """根据ID获取提示词"""
        prompts_data = self._load_prompts()
        for prompt_data in prompts_data:
            if prompt_data['id'] == prompt_id:
                return Prompt(**prompt_data)
        return None
    
    def create_prompt(self, prompt: PromptCreate) -> Prompt:
        """创建新提示词"""
        prompts_data = self._load_prompts()
        
        new_prompt = {
            "id": str(uuid.uuid4()),
            "title": prompt.title,
            "content": prompt.content,
            "description": prompt.description,
            "category": prompt.category,
            "tags": prompt.tags,
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        prompts_data.append(new_prompt)
        self._save_prompts(prompts_data)
        
        return Prompt(**new_prompt)
    
    def update_prompt(self, prompt_id: str, prompt_update: PromptUpdate) -> Optional[Prompt]:
        """更新提示词"""
        prompts_data = self._load_prompts()
        
        for i, prompt_data in enumerate(prompts_data):
            if prompt_data['id'] == prompt_id:
                # 更新字段
                update_data = prompt_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    prompt_data[key] = value
                
                prompt_data['updated_at'] = datetime.now().isoformat()
                prompts_data[i] = prompt_data
                
                self._save_prompts(prompts_data)
                return Prompt(**prompt_data)
        
        return None
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """删除提示词"""
        prompts_data = self._load_prompts()
        
        for i, prompt_data in enumerate(prompts_data):
            if prompt_data['id'] == prompt_id:
                prompts_data.pop(i)
                self._save_prompts(prompts_data)
                return True
        
        return False
    
    def increment_usage_count(self, prompt_id: str) -> bool:
        """增加使用次数"""
        prompts_data = self._load_prompts()
        
        for prompt_data in prompts_data:
            if prompt_data['id'] == prompt_id:
                prompt_data['usage_count'] += 1
                prompt_data['updated_at'] = datetime.now().isoformat()
                self._save_prompts(prompts_data)
                return True
        
        return False
    
    # 分类相关方法
    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        categories_data = self._load_categories()
        return [Category(**category) for category in categories_data]
    
    def create_category(self, category: CategoryCreate) -> Category:
        """创建新分类"""
        categories_data = self._load_categories()
        
        new_category = {
            "id": str(uuid.uuid4()),
            "name": category.name,
            "color": category.color,
            "prompt_count": 0
        }
        
        categories_data.append(new_category)
        self._save_categories(categories_data)
        
        return Category(**new_category)
    
    def update_category(self, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
        """更新分类"""
        categories_data = self._load_categories()
        
        for i, category_data in enumerate(categories_data):
            if category_data['id'] == category_id:
                update_data = category_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    category_data[key] = value
                
                categories_data[i] = category_data
                self._save_categories(categories_data)
                return Category(**category_data)
        
        return None
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        categories_data = self._load_categories()
        
        for i, category_data in enumerate(categories_data):
            if category_data['id'] == category_id:
                categories_data.pop(i)
                self._save_categories(categories_data)
                return True
        
        return False
    
    # 标签相关方法
    def get_all_tags(self) -> List[Tag]:
        """获取所有标签"""
        tags_data = self._load_tags()
        return [Tag(**tag) for tag in tags_data]
    
    def create_tag(self, tag: TagCreate) -> Tag:
        """创建新标签"""
        tags_data = self._load_tags()
        
        new_tag = {
            "id": str(uuid.uuid4()),
            "name": tag.name,
            "color": tag.color,
            "usage_count": 0
        }
        
        tags_data.append(new_tag)
        self._save_tags(tags_data)
        
        return Tag(**new_tag)
    
    def update_tag(self, tag_id: str, tag_update: TagUpdate) -> Optional[Tag]:
        """更新标签"""
        tags_data = self._load_tags()
        
        for i, tag_data in enumerate(tags_data):
            if tag_data['id'] == tag_id:
                update_data = tag_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    tag_data[key] = value
                
                tags_data[i] = tag_data
                self._save_tags(tags_data)
                return Tag(**tag_data)
        
        return None
    
    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        tags_data = self._load_tags()
        
        for i, tag_data in enumerate(tags_data):
            if tag_data['id'] == tag_id:
                tags_data.pop(i)
                self._save_tags(tags_data)
                return True
        
        return False
    
    def search_prompts(self, query: str = "", category: str = "", tags: List[str] = None) -> List[Prompt]:
        """搜索提示词"""
        prompts = self.get_all_prompts()
        
        if query:
            query = query.lower()
            prompts = [p for p in prompts if 
                      query in p.title.lower() or 
                      query in p.content.lower() or 
                      (p.description and query in p.description.lower())]
        
        if category:
            prompts = [p for p in prompts if p.category == category]
        
        if tags:
            prompts = [p for p in prompts if any(tag in p.tags for tag in tags)]
        
        return prompts
