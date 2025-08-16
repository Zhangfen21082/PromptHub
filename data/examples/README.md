# 📋 示例数据说明

这个目录包含了PromptHub的示例数据，可用于测试和演示。

## 📁 文件说明

- **`sample_prompts.json`**: 包含100条示例提示词数据
- **`sample_categories.json`**: 示例分类数据（编程、写作、分析、创意、商业、教育等）
- **`sample_tags.json`**: 示例标签数据（Python、React、文案、策划等）

## 🚀 如何使用示例数据

### 方式一：复制覆盖（推荐用于测试）
```bash
# 进入项目根目录
cd /path/to/PromptHub

# 复制示例数据到data目录
cp data/examples/sample_prompts.json data/prompts.json
cp data/examples/sample_categories.json data/categories.json  
cp data/examples/sample_tags.json data/tags.json

# 重启应用
python app.py
```

### 方式二：手动导入
1. 启动PromptHub应用
2. 手动添加分类和标签
3. 逐个添加提示词内容

## ⚠️ 注意事项

- 使用示例数据前请备份您现有的数据
- 示例数据将覆盖当前所有内容
- 生产环境建议使用空数据开始

## 🔄 恢复空数据

如果需要清空数据重新开始：
```bash
echo '[]' > data/prompts.json
echo '[]' > data/categories.json
echo '[]' > data/tags.json
```

## 📊 示例数据统计

- **提示词总数**: 100条
- **分类数量**: 6个主要分类
- **标签数量**: 30+个常用标签
- **覆盖场景**: 编程开发、内容创作、数据分析、商业策划等

这些示例数据展示了PromptHub的完整功能特性，适合用于：
- 功能演示
- 性能测试  
- 界面预览
- 功能验证
