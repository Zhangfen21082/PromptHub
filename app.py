from flask import Flask, render_template, request, jsonify
import json
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 加载配置文件
def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        # 默认配置
        return {
            "admin_password": "admin123",
            "app_name": "PromptHub",
            "app_description": "智能提示词管理平台",
            "port": 5001,
            "debug": True
        }

def get_admin_password_hash():
    """获取管理员密码的哈希值"""
    config = load_config()
    password = config.get("admin_password", "admin123")
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password_hash):
    """验证口令"""
    return password_hash == get_admin_password_hash()

# 复用现有的存储逻辑
class FileStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.prompts_file = self.data_dir / "prompts.json"
        self.categories_file = self.data_dir / "categories.json"
        self.tags_file = self.data_dir / "tags.json"
        
        self._init_data_files()
    
    def _init_data_files(self):
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
    
    def _load_prompts(self):
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('prompts', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_prompts(self, prompts):
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            json.dump({'prompts': prompts}, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self):
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('categories', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_categories(self, categories):
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump({'categories': categories}, f, ensure_ascii=False, indent=2)
    
    def _load_tags(self):
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tags', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_tags(self, tags):
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump({'tags': tags}, f, ensure_ascii=False, indent=2)
    
    def get_all_prompts(self):
        return self._load_prompts()
    
    def create_prompt(self, prompt_data):
        prompts_data = self._load_prompts()
        
        new_prompt = {
            "id": str(uuid.uuid4()),
            "title": prompt_data['title'],
            "content": prompt_data['content'],
            "description": prompt_data.get('description', ''),
            "category": prompt_data.get('category', '其他'),
            "tags": prompt_data.get('tags', []),
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        prompts_data.append(new_prompt)
        self._save_prompts(prompts_data)
        return new_prompt
    
    def update_prompt(self, prompt_id: str, update_data):
        prompts_data = self._load_prompts()
        
        for prompt in prompts_data:
            if prompt['id'] == prompt_id:
                for key, value in update_data.items():
                    if key in prompt:
                        prompt[key] = value
                prompt['updated_at'] = datetime.now().isoformat()
                self._save_prompts(prompts_data)
                return prompt
        return None
    
    def delete_prompt(self, prompt_id: str):
        prompts_data = self._load_prompts()
        
        for i, prompt in enumerate(prompts_data):
            if prompt['id'] == prompt_id:
                prompts_data.pop(i)
                self._save_prompts(prompts_data)
                return True
        return False
    
    def increment_usage_count(self, prompt_id: str):
        prompts_data = self._load_prompts()
        
        for prompt in prompts_data:
            if prompt['id'] == prompt_id:
                prompt['usage_count'] += 1
                prompt['updated_at'] = datetime.now().isoformat()
                self._save_prompts(prompts_data)
                return True
        return False
    
    def get_all_categories(self):
        return self._load_categories()
    
    def create_category(self, category_data):
        """创建分类"""
        categories = self._load_categories()
        new_category = {
            "id": str(uuid.uuid4()),
            "name": category_data["name"],
            "color": category_data.get("color", "#3B82F6")
        }
        categories.append(new_category)
        self._save_categories(categories)
        return new_category
    
    def update_category(self, category_id, update_data):
        """更新分类"""
        categories = self._load_categories()
        for i, category in enumerate(categories):
            if category["id"] == category_id:
                categories[i].update(update_data)
                self._save_categories(categories)
                return categories[i]
        return None
    
    def delete_category(self, category_id):
        """删除分类"""
        categories = self._load_categories()
        
        # 找到要删除的分类名称
        category_to_delete = None
        for category in categories:
            if category["id"] == category_id:
                category_to_delete = category["name"]
                break
        
        if not category_to_delete:
            return False
        
        # 处理关联的提示词：将它们移动到"其他"分类
        prompts = self._load_prompts()
        updated_prompts = []
        affected_count = 0
        
        for prompt in prompts:
            if prompt.get("category") == category_to_delete:
                prompt["category"] = "其他"  # 移动到"其他"分类
                affected_count += 1
            updated_prompts.append(prompt)
        
        # 保存更新后的提示词
        if affected_count > 0:
            self._save_prompts(updated_prompts)
        
        # 删除分类
        original_length = len(categories)
        categories = [c for c in categories if c["id"] != category_id]
        
        if len(categories) < original_length:
            self._save_categories(categories)
            return {"success": True, "affected_prompts": affected_count}
        return False
    
    def get_all_tags(self):
        return self._load_tags()
    
    def create_tag(self, tag_data):
        """创建标签"""
        tags = self._load_tags()
        new_tag = {
            "id": str(uuid.uuid4()),
            "name": tag_data["name"],
            "color": tag_data.get("color", "#6B7280")
        }
        tags.append(new_tag)
        self._save_tags(tags)
        return new_tag
    
    def update_tag(self, tag_id, update_data):
        """更新标签"""
        tags = self._load_tags()
        
        # 找到要更新的标签
        old_tag_name = None
        updated_tag = None
        for i, tag in enumerate(tags):
            if tag["id"] == tag_id:
                old_tag_name = tag["name"]
                tags[i].update(update_data)
                updated_tag = tags[i]
                break
        
        if old_tag_name and "name" in update_data:
            new_tag_name = update_data["name"]
            
            # 如果标签名称改变了，需要更新所有使用该标签的提示词
            if old_tag_name != new_tag_name:
                prompts = self._load_prompts()
                updated_prompts = []
                
                for prompt in prompts:
                    if prompt.get("tags") and old_tag_name in prompt["tags"]:
                        # 替换标签名称
                        prompt["tags"] = [new_tag_name if tag == old_tag_name else tag for tag in prompt["tags"]]
                    updated_prompts.append(prompt)
                
                self._save_prompts(updated_prompts)
        
        if updated_tag:
            self._save_tags(tags)
        
        return updated_tag
    
    def delete_tag(self, tag_id):
        """删除标签"""
        tags = self._load_tags()
        
        # 找到要删除的标签名称
        tag_to_delete = None
        for tag in tags:
            if tag["id"] == tag_id:
                tag_to_delete = tag["name"]
                break
        
        if not tag_to_delete:
            return False
        
        # 处理关联的提示词：从所有提示词中移除该标签
        prompts = self._load_prompts()
        updated_prompts = []
        affected_count = 0
        
        for prompt in prompts:
            if prompt.get("tags") and tag_to_delete in prompt["tags"]:
                prompt["tags"] = [tag for tag in prompt["tags"] if tag != tag_to_delete]
                affected_count += 1
            updated_prompts.append(prompt)
        
        # 保存更新后的提示词
        if affected_count > 0:
            self._save_prompts(updated_prompts)
        
        # 删除标签
        original_length = len(tags)
        tags = [t for t in tags if t["id"] != tag_id]
        
        if len(tags) < original_length:
            self._save_tags(tags)
            return {"success": True, "affected_prompts": affected_count}
        return False
    
    def search_prompts(self, query: str = "", category: str = ""):
        prompts = self.get_all_prompts()
        
        if query:
            query = query.lower()
            prompts = [p for p in prompts if 
                      query in p['title'].lower() or 
                      query in p['content'].lower() or 
                      query in p.get('description', '').lower()]
        
        if category:
            prompts = [p for p in prompts if p['category'] == category]
        
        return prompts

# 初始化存储
storage = FileStorage()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    return jsonify(storage.get_all_prompts())

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    """创建提示词"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    prompt_data = {k: v for k, v in data.items() if k != 'password_hash'}
    new_prompt = storage.create_prompt(prompt_data)
    return jsonify(new_prompt), 201

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """更新提示词"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    update_data = {k: v for k, v in data.items() if k != 'password_hash'}
    prompt = storage.update_prompt(prompt_id, update_data)
    if prompt:
        return jsonify(prompt)
    return jsonify({"error": "提示词不存在"}), 404

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """删除提示词"""
    data = request.json
    
    # 验证口令
    if not data or 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    if storage.delete_prompt(prompt_id):
        return jsonify({"message": "删除成功"})
    return jsonify({"error": "提示词不存在"}), 404

@app.route('/api/prompts/<prompt_id>/use', methods=['POST'])
def use_prompt(prompt_id):
    if storage.increment_usage_count(prompt_id):
        return jsonify({"message": "使用次数已更新"})
    return jsonify({"error": "提示词不存在"}), 404

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(storage.get_all_categories())

@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    category_data = {k: v for k, v in data.items() if k != 'password_hash'}
    new_category = storage.create_category(category_data)
    return jsonify(new_category), 201

@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分类"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    update_data = {k: v for k, v in data.items() if k != 'password_hash'}
    category = storage.update_category(category_id, update_data)
    if category:
        return jsonify(category)
    return jsonify({"error": "分类不存在"}), 404

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类"""
    data = request.json
    
    # 验证口令
    if not data or 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    result = storage.delete_category(category_id)
    if result and result.get("success"):
        message = f"删除成功"
        if result.get("affected_prompts", 0) > 0:
            message += f"，已将 {result['affected_prompts']} 个提示词移动到'其他'分类"
        return jsonify({"message": message})
    return jsonify({"error": "分类不存在"}), 404

# 标签管理API
@app.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify(storage.get_all_tags())

@app.route('/api/tags', methods=['POST'])
def create_tag():
    """创建标签"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    tag_data = {k: v for k, v in data.items() if k != 'password_hash'}
    new_tag = storage.create_tag(tag_data)
    return jsonify(new_tag), 201

@app.route('/api/tags/<tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """更新标签"""
    data = request.json
    
    # 验证口令
    if 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    # 移除口令字段
    update_data = {k: v for k, v in data.items() if k != 'password_hash'}
    tag = storage.update_tag(tag_id, update_data)
    if tag:
        return jsonify(tag)
    return jsonify({"error": "标签不存在"}), 404

@app.route('/api/tags/<tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """删除标签"""
    data = request.json
    
    # 验证口令
    if not data or 'password_hash' not in data or not verify_password(data['password_hash']):
        return jsonify({"error": "口令验证失败"}), 401
    
    result = storage.delete_tag(tag_id)
    if result and result.get("success"):
        message = f"删除成功"
        if result.get("affected_prompts", 0) > 0:
            message += f"，已从 {result['affected_prompts']} 个提示词中移除该标签"
        return jsonify({"message": message})
    return jsonify({"error": "标签不存在"}), 404

@app.route('/api/search', methods=['GET'])
def search_prompts():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    prompts = storage.search_prompts(query, category)
    categories = storage.get_all_categories()
    tags = storage.get_all_tags()
    
    return jsonify({
        "prompts": prompts,
        "total": len(prompts),
        "categories": categories,
        "tags": tags
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    prompts = storage.get_all_prompts()
    categories = storage.get_all_categories()
    tags = storage.get_all_tags()
    
    most_used_prompt = None
    if prompts:
        most_used_prompt = max(prompts, key=lambda p: p['usage_count'])
    
    category_distribution = []
    for category in categories:
        count = len([p for p in prompts if p['category'] == category['name']])
        category_distribution.append({
            "name": category['name'],
            "count": count,
            "color": category['color']
        })
    
    return jsonify({
        "total_prompts": len(prompts),
        "total_categories": len(categories),
        "total_tags": len(tags),
        "most_used_prompt": most_used_prompt,
        "category_distribution": category_distribution
    })

@app.route('/api/auth/test', methods=['POST'])
def test_auth():
    """测试管理员口令是否正确"""
    data = request.json
    
    if not data or 'password_hash' not in data:
        return jsonify({"error": "缺少口令"}), 400
    
    if verify_password(data['password_hash']):
        return jsonify({"message": "口令正确"}), 200
    else:
        return jsonify({"error": "口令错误"}), 401

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
