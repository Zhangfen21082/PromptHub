from flask import Flask, render_template, request, jsonify
import json
import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil

app = Flask(__name__)

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 默认配置
        default_config = {
            "admin_password": "admin123",
            "app_name": "PromptHub",
            "app_description": "智能提示词管理平台",
            "port": 5001,
            "debug": True
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config

def get_admin_password_hash():
    """获取管理员口令的哈希值"""
    config = load_config()
    password = config.get('admin_password', 'admin123')
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password_hash):
    """验证口令"""
    return password_hash == get_admin_password_hash()

def is_debug_mode():
    """检查是否为debug模式"""
    config = load_config()
    return config.get('debug', False)

# 重构后的统一存储逻辑
class FileStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.data_file = self.data_dir / "prompts.json"
        self._init_unified_data_file()

    def _init_unified_data_file(self):
        """初始化统一数据文件"""
        if not self.data_file.exists():
            default_data = {
                "prompts": [],
                "metadata": {
                    "categories": [
                        {"id": "1", "name": "编程", "color": "#3B82F6", "description": "编程相关提示词"},
                        {"id": "2", "name": "写作", "color": "#10B981", "description": "写作相关提示词"},
                        {"id": "3", "name": "分析", "color": "#F59E0B", "description": "分析相关提示词"},
                        {"id": "4", "name": "创意", "color": "#8B5CF6", "description": "创意相关提示词"},
                        {"id": "5", "name": "商业", "color": "#EF4444", "description": "商业相关提示词"},
                        {"id": "6", "name": "教育", "color": "#06B6D4", "description": "教育相关提示词"},
                        {"id": "7", "name": "其他", "color": "#6B7280", "description": "其他类型提示词"}
                    ],
                    "tags": [],
                    "settings": {
                        "last_updated": datetime.now().isoformat(),
                        "version": "2.0"
                    }
                }
            }
            self._save_data(default_data)

    def _load_data(self):
        """加载统一数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 兼容性处理：如果是旧格式，进行迁移
                if "metadata" not in data and "prompts" in data:
                    return self._migrate_from_old_format(data)
                
                # 确保所有必需的字段都存在
                if "metadata" not in data:
                    data["metadata"] = {"categories": [], "tags": [], "settings": {}}
                if "categories" not in data["metadata"]:
                    data["metadata"]["categories"] = []
                if "tags" not in data["metadata"]:
                    data["metadata"]["tags"] = []
                if "settings" not in data["metadata"]:
                    data["metadata"]["settings"] = {"version": "2.0", "last_updated": datetime.now().isoformat()}
                    
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或损坏，重新初始化
            self._init_unified_data_file()
            return self._load_data()

    def _save_data(self, data):
        """保存统一数据"""
        # 更新最后修改时间
        data["metadata"]["settings"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _migrate_from_old_format(self, old_data):
        """从旧格式迁移数据"""
        # 检测到旧数据格式，正在迁移
        
        # 加载旧的分类和标签数据
        old_categories = []
        old_tags = []
        
        try:
            if (self.data_dir / "categories.json").exists():
                with open(self.data_dir / "categories.json", 'r', encoding='utf-8') as f:
                    old_cat_data = json.load(f)
                    if isinstance(old_cat_data, list):
                        old_categories = old_cat_data
                    else:
                        old_categories = old_cat_data.get('categories', [])
        except:
            pass
            
        try:
            if (self.data_dir / "tags.json").exists():
                with open(self.data_dir / "tags.json", 'r', encoding='utf-8') as f:
                    old_tag_data = json.load(f)
                    if isinstance(old_tag_data, list):
                        old_tags = old_tag_data
                    else:
                        old_tags = old_tag_data.get('tags', [])
        except:
            pass

        # 构建新格式数据
        new_data = {
            "prompts": old_data.get("prompts", []),
            "metadata": {
                "categories": old_categories if old_categories else [
                    {"id": "1", "name": "编程", "color": "#3B82F6", "description": "编程相关提示词"},
                    {"id": "2", "name": "写作", "color": "#10B981", "description": "写作相关提示词"},
                    {"id": "3", "name": "分析", "color": "#F59E0B", "description": "分析相关提示词"},
                    {"id": "4", "name": "创意", "color": "#8B5CF6", "description": "创意相关提示词"},
                    {"id": "5", "name": "商业", "color": "#EF4444", "description": "商业相关提示词"},
                    {"id": "6", "name": "教育", "color": "#06B6D4", "description": "教育相关提示词"},
                    {"id": "7", "name": "其他", "color": "#6B7280", "description": "其他类型提示词"}
                ],
                "tags": old_tags,
                "settings": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "2.0",
                    "migrated_from": "1.0"
                }
            }
        }
        
        # 从prompts中提取实际使用的标签，确保数据一致性
        used_tags = set()
        for prompt in new_data["prompts"]:
            if prompt.get("tags"):
                used_tags.update(prompt["tags"])
        
        # 添加缺失的标签到metadata
        existing_tag_names = {tag["name"] for tag in new_data["metadata"]["tags"]}
        for tag_name in used_tags:
            if tag_name not in existing_tag_names:
                new_data["metadata"]["tags"].append({
                    "id": str(uuid.uuid4()),
                    "name": tag_name,
                    "color": "#3B82F6"  # 默认颜色
                })
        
        # 迁移完成
        return new_data

    # 提示词相关方法
    def get_all_prompts(self):
        data = self._load_data()
        return data["prompts"]

    def create_prompt(self, prompt_data):
        data = self._load_data()
        
        new_prompt = {
            "id": str(uuid.uuid4()),
            "title": prompt_data["title"],
            "content": prompt_data["content"],
            "description": prompt_data.get("description", ""),
            "category": prompt_data.get("category", "其他"),
            "tags": prompt_data.get("tags", []),
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        data["prompts"].append(new_prompt)
        self._save_data(data)
        return new_prompt

    def update_prompt(self, prompt_id, update_data):
        data = self._load_data()
        
        for prompt in data["prompts"]:
            if prompt["id"] == prompt_id:
                prompt.update(update_data)
                prompt["updated_at"] = datetime.now().isoformat()
                self._save_data(data)
                return prompt
        return None

    def delete_prompt(self, prompt_id):
        data = self._load_data()
        
        original_length = len(data["prompts"])
        data["prompts"] = [p for p in data["prompts"] if p["id"] != prompt_id]
        
        if len(data["prompts"]) < original_length:
            self._save_data(data)
            return True
        return False

    def use_prompt(self, prompt_id):
        data = self._load_data()
        
        for prompt in data["prompts"]:
            if prompt["id"] == prompt_id:
                prompt["usage_count"] = prompt.get("usage_count", 0) + 1
                prompt["updated_at"] = datetime.now().isoformat()
                self._save_data(data)
                return prompt
        return None

    # 分类相关方法
    def get_all_categories(self):
        data = self._load_data()
        return data["metadata"]["categories"]

    def create_category(self, category_data):
        data = self._load_data()
        
        new_category = {
            "id": str(uuid.uuid4()),
            "name": category_data["name"],
            "color": category_data.get("color", "#6B7280"),
            "description": category_data.get("description", "")
        }
        
        data["metadata"]["categories"].append(new_category)
        self._save_data(data)
        return new_category

    def update_category(self, category_id, update_data):
        data = self._load_data()
        
        for category in data["metadata"]["categories"]:
            if category["id"] == category_id:
                old_name = category["name"]
                category.update(update_data)
                
                # 如果分类名称发生变化，更新所有使用该分类的提示词
                if "name" in update_data and update_data["name"] != old_name:
                    for prompt in data["prompts"]:
                        if prompt["category"] == old_name:
                            prompt["category"] = update_data["name"]
                            prompt["updated_at"] = datetime.now().isoformat()
                
                self._save_data(data)
                return category
        return None

    def delete_category(self, category_id):
        data = self._load_data()
        
        # 找到要删除的分类
        category_to_delete = None
        for category in data["metadata"]["categories"]:
            if category["id"] == category_id:
                category_to_delete = category["name"]
                break
        
        if not category_to_delete:
            return False
        
        # 处理关联的提示词：移动到"其他"分类
        affected_count = 0
        for prompt in data["prompts"]:
            if prompt["category"] == category_to_delete:
                prompt["category"] = "其他"
                prompt["updated_at"] = datetime.now().isoformat()
                affected_count += 1
        
        # 删除分类
        original_length = len(data["metadata"]["categories"])
        data["metadata"]["categories"] = [c for c in data["metadata"]["categories"] if c["id"] != category_id]
        
        if len(data["metadata"]["categories"]) < original_length:
            self._save_data(data)
            return {"success": True, "affected_prompts": affected_count}
        return False

    # 标签相关方法
    def get_all_tags(self):
        data = self._load_data()
        
        # 从prompts中提取实际使用的标签
        used_tags = set()
        for prompt in data["prompts"]:
            if prompt.get("tags"):
                used_tags.update(prompt["tags"])
        
        # 获取metadata中的标签定义
        metadata_tags = {tag["name"]: tag for tag in data["metadata"]["tags"]}
        
        # 合并：确保所有使用的标签都有定义
        result_tags = []
        for tag_name in used_tags:
            if tag_name in metadata_tags:
                # 使用metadata中的定义
                result_tags.append(metadata_tags[tag_name])
            else:
                # 为没有定义的标签创建默认定义
                import uuid
                tag_def = {
                    "id": f"auto-{str(uuid.uuid4())[:8]}",
                    "name": tag_name,
                    "color": "#3B82F6"  # 默认蓝色
                }
                result_tags.append(tag_def)
                # 同时添加到metadata中
                data["metadata"]["tags"].append(tag_def)
        
        # 如果有新标签添加到metadata，保存数据
        if len(result_tags) > len(metadata_tags):
            self._save_data(data)
        
        return result_tags

    def create_tag(self, tag_data):
        data = self._load_data()
        
        new_tag = {
            "id": str(uuid.uuid4()),
            "name": tag_data["name"],
            "color": tag_data.get("color", "#3B82F6")
        }
        
        data["metadata"]["tags"].append(new_tag)
        self._save_data(data)
        return new_tag

    def update_tag(self, tag_id, update_data):
        data = self._load_data()
        
        for tag in data["metadata"]["tags"]:
            if tag["id"] == tag_id:
                old_name = tag["name"]
                tag.update(update_data)
                
                # 如果标签名称发生变化，更新所有使用该标签的提示词
                if "name" in update_data and update_data["name"] != old_name:
                    for prompt in data["prompts"]:
                        if prompt.get("tags") and old_name in prompt["tags"]:
                            prompt["tags"] = [update_data["name"] if t == old_name else t for t in prompt["tags"]]
                            prompt["updated_at"] = datetime.now().isoformat()
                
                self._save_data(data)
                return tag
        return None

    def delete_tag(self, tag_id):
        data = self._load_data()
        
        # 找到要删除的标签
        tag_to_delete = None
        for tag in data["metadata"]["tags"]:
            if tag["id"] == tag_id:
                tag_to_delete = tag["name"]
                break
        
        if not tag_to_delete:
            return False
        
        # 处理关联的提示词：从所有提示词中移除该标签
        affected_count = 0
        for prompt in data["prompts"]:
            if prompt.get("tags") and tag_to_delete in prompt["tags"]:
                prompt["tags"] = [tag for tag in prompt["tags"] if tag != tag_to_delete]
                prompt["updated_at"] = datetime.now().isoformat()
                affected_count += 1
        
        # 删除标签
        original_length = len(data["metadata"]["tags"])
        data["metadata"]["tags"] = [t for t in data["metadata"]["tags"] if t["id"] != tag_id]
        
        if len(data["metadata"]["tags"]) < original_length:
            self._save_data(data)
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

    # 数据管理方法
    def backup_data(self):
        """备份数据"""
        backup_dir = self.data_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        shutil.copy2(self.data_file, backup_file)
        return str(backup_file)

    def clear_all_data(self):
        """清空所有数据，但保留默认分类"""
        backup_file = self.backup_data()
        
        default_data = {
            "prompts": [],
            "metadata": {
                "categories": [
                    {"id": "1", "name": "编程", "color": "#3B82F6", "description": "编程相关提示词"},
                    {"id": "2", "name": "写作", "color": "#10B981", "description": "写作相关提示词"},
                    {"id": "3", "name": "分析", "color": "#F59E0B", "description": "分析相关提示词"},
                    {"id": "4", "name": "创意", "color": "#8B5CF6", "description": "创意相关提示词"},
                    {"id": "5", "name": "商业", "color": "#EF4444", "description": "商业相关提示词"},
                    {"id": "6", "name": "教育", "color": "#06B6D4", "description": "教育相关提示词"},
                    {"id": "7", "name": "其他", "color": "#6B7280", "description": "其他类型提示词"}
                ],
                "tags": [],
                "settings": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "2.0"
                }
            }
        }
        
        self._save_data(default_data)
        return backup_file

    def load_test_data(self):
        """加载测试数据"""
        backup_file = self.backup_data()
        
        try:
            examples_dir = self.data_dir / "examples"
            example_prompts_file = examples_dir / "prompts.json"
            
            if example_prompts_file.exists():
                with open(example_prompts_file, 'r', encoding='utf-8') as f:
                    example_data = json.load(f)
                    
                # 加载测试数据，但保持当前的metadata结构
                current_data = self._load_data()
                current_data["prompts"] = example_data.get("prompts", [])
                
                # 从测试数据中提取标签并添加到metadata
                used_tags = set()
                for prompt in current_data["prompts"]:
                    if prompt.get("tags"):
                        used_tags.update(prompt["tags"])
                
                existing_tag_names = {tag["name"] for tag in current_data["metadata"]["tags"]}
                for tag_name in used_tags:
                    if tag_name not in existing_tag_names:
                        current_data["metadata"]["tags"].append({
                            "id": str(uuid.uuid4()),
                            "name": tag_name,
                            "color": "#3B82F6"
                        })
                
                self._save_data(current_data)
                return backup_file
            else:
                raise FileNotFoundError("测试数据文件不存在")
                
        except Exception as e:
            # 加载测试数据失败
            raise

# 初始化存储
storage = FileStorage()

# API 路由保持不变，但实现逻辑更新
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    return jsonify(storage.get_all_prompts())

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    """创建提示词"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        prompt_data = {
            "title": request.json.get('title'),
            "content": request.json.get('content'),
            "description": request.json.get('description', ''),
            "category": request.json.get('category', '其他'),
            "tags": request.json.get('tags', [])
        }
        
        new_prompt = storage.create_prompt(prompt_data)
        return jsonify(new_prompt), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """更新提示词"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        update_data = {
            "title": request.json.get('title'),
            "content": request.json.get('content'),
            "description": request.json.get('description', ''),
            "category": request.json.get('category', '其他'),
            "tags": request.json.get('tags', [])
        }
        
        updated_prompt = storage.update_prompt(prompt_id, update_data)
        if updated_prompt:
            return jsonify(updated_prompt)
        else:
            return jsonify({"error": "提示词不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """删除提示词"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    if storage.delete_prompt(prompt_id):
        return jsonify({"message": "提示词删除成功"})
    else:
        return jsonify({"error": "提示词不存在"}), 404

@app.route('/api/prompts/<prompt_id>/use', methods=['POST'])
def use_prompt(prompt_id):
    prompt = storage.use_prompt(prompt_id)
    if prompt:
        return jsonify(prompt)
    return jsonify({"error": "提示词不存在"}), 404

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(storage.get_all_categories())

@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        category_data = {
            "name": request.json.get('name'),
            "color": request.json.get('color', '#6B7280'),
            "description": request.json.get('description', '')
        }
        
        new_category = storage.create_category(category_data)
        return jsonify(new_category), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分类"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        update_data = {
            "name": request.json.get('name'),
            "color": request.json.get('color'),
            "description": request.json.get('description', '')
        }
        
        updated_category = storage.update_category(category_id, update_data)
        if updated_category:
            return jsonify(updated_category)
        else:
            return jsonify({"error": "分类不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    result = storage.delete_category(category_id)
    if result:
        return jsonify({
            "message": f"分类删除成功，{result['affected_prompts']} 个提示词已移动到'其他'分类"
        })
    else:
        return jsonify({"error": "分类不存在"}), 404

# 标签管理API
@app.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify(storage.get_all_tags())

@app.route('/api/tags', methods=['POST'])
def create_tag():
    """创建标签"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        tag_data = {
            "name": request.json.get('name'),
            "color": request.json.get('color', '#3B82F6')
        }
        
        new_tag = storage.create_tag(tag_data)
        return jsonify(new_tag), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags/<tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """更新标签"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    try:
        update_data = {
            "name": request.json.get('name'),
            "color": request.json.get('color')
        }
        
        updated_tag = storage.update_tag(tag_id, update_data)
        if updated_tag:
            return jsonify(updated_tag)
        else:
            return jsonify({"error": "标签不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags/<tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """删除标签"""
    if not verify_password(request.json.get('password_hash')):
        return jsonify({"error": "无效的管理员口令"}), 401
    
    result = storage.delete_tag(tag_id)
    if result:
        return jsonify({
            "message": f"标签删除成功，{result['affected_prompts']} 个提示词已移除该标签"
        })
    else:
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
        most_used_prompt = max(prompts, key=lambda p: p.get('usage_count', 0))

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

@app.route('/api/debug-mode', methods=['GET'])
def get_debug_mode():
    """获取debug模式状态"""
    config = load_config()
    is_debug = config.get('debug', False)
    return jsonify({"debug": is_debug})

@app.route('/api/auth/test', methods=['POST'])
def test_auth():
    """测试管理员口令是否正确"""
    password_hash = request.json.get('password_hash')
    
    if verify_password(password_hash):
        return jsonify({"valid": True, "message": "口令验证成功"})
    else:
        return jsonify({"valid": False, "message": "口令错误"}), 401

@app.route('/api/export', methods=['GET'])
def export_data():
    """导出数据"""
    # 在debug模式下不需要密码
    if not is_debug_mode():
        # 从请求头获取密码哈希（用于API调用）
        password_hash = request.headers.get('X-Password-Hash')
        if not password_hash:
            # 从查询参数获取密码哈希（用于前端调用）
            password_hash = request.args.get('password_hash')

        if not verify_password(password_hash):
            return jsonify({"error": "无效的管理员口令"}), 401

    data = storage._load_data()

    # 根据参数过滤数据
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []

    prompts = data["prompts"]

    if search:
        search = search.lower()
        prompts = [p for p in prompts if
                  search in p['title'].lower() or
                  search in p['content'].lower() or
                  search in p.get('description', '').lower()]

    if category:
        prompts = [p for p in prompts if p['category'] == category]

    if tags:
        prompts = [p for p in prompts if
                  p.get('tags') and any(tag in p['tags'] for tag in tags)]

    # 导出格式
    export_data = []
    for prompt in prompts:
        export_data.append({
            "标题": prompt["title"],
            "描述": prompt.get("description", ""),
            "内容": prompt["content"],
            "分类": prompt["category"],
            "标签": ", ".join(prompt.get("tags", [])),
            "创建时间": prompt.get("created_at", ""),
            "更新时间": prompt.get("updated_at", "")
        })

    return jsonify({
        "data": export_data,
        "total": len(export_data),
        "exported_at": datetime.now().isoformat()
    })

# 管理员功能
@app.route('/api/admin/load-test-data', methods=['POST'])
def load_test_data():
    """加载测试数据"""
    # 在debug模式下不需要密码
    if not is_debug_mode():
        if not verify_password(request.json.get('password_hash')):
            return jsonify({"error": "无效的管理员口令"}), 401

    try:
        backup_file = storage.load_test_data()
        prompts = storage.get_all_prompts()
        return jsonify({
            "message": f"测试数据加载成功，共 {len(prompts)} 条数据。原数据已备份到 {backup_file}",
            "total_prompts": len(prompts)
        })
    except Exception as e:
        return jsonify({"error": f"加载测试数据失败: {str(e)}"}), 500

@app.route('/api/admin/clear-data', methods=['POST'])
def clear_all_data():
    """清空所有数据"""
    # 在debug模式下不需要密码
    if not is_debug_mode():
        if not verify_password(request.json.get('password_hash')):
            return jsonify({"error": "无效的管理员口令"}), 401

    try:
        backup_file = storage.clear_all_data()
        return jsonify({
            "message": f"所有数据已清空。原数据已备份到 {backup_file}"
        })
    except Exception as e:
        return jsonify({"error": f"清空数据失败: {str(e)}"}), 500

if __name__ == '__main__':
    config = load_config()
    port = config.get('port', 5001)
    debug = config.get('debug', True)
    app.run(host='0.0.0.0', port=port, debug=debug)
