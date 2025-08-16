# PromptHub

一个智能的提示词管理平台，帮助您收集、分类和快速访问常用的AI提示词。

## ✨ 核心功能

- 📝 **提示词收集** - 随时保存和管理您的提示词
- 🏷️ **智能分类** - 按用途、场景或自定义标签组织
- ⚡ **快速访问** - 一键复制，提高工作效率
- 🔍 **搜索功能** - 快速找到需要的提示词
- 📱 **响应式设计** - 支持桌面和移动设备

## 🚀 快速开始

### 环境要求

- Python 3.11+

### 启动应用

1. **克隆项目**
```bash
git clone <repository-url>
cd PromptHub
```

2. **创建虚拟环境并安装依赖**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **启动应用**
```bash
python app.py
```

4. **访问应用**
- 应用地址: http://localhost:5001

## 🏗️ 项目结构

```
PromptHub/
├── app.py                  # Flask主应用
├── requirements.txt        # Python依赖
├── templates/             # HTML模板
│   └── index.html         # 主页面
├── data/                  # JSON数据存储
│   ├── prompts.json       # 提示词数据
│   ├── categories.json    # 分类数据
│   └── tags.json         # 标签数据
└── README.md             # 项目文档
```

## 📚 API文档

### 提示词管理

- `GET /api/prompts` - 获取所有提示词
- `POST /api/prompts` - 创建提示词
- `PUT /api/prompts/<id>` - 更新提示词
- `DELETE /api/prompts/<id>` - 删除提示词
- `POST /api/prompts/<id>/use` - 使用提示词（增加使用次数）

### 分类管理

- `GET /api/categories` - 获取所有分类

### 搜索和统计

- `GET /api/search` - 搜索提示词
- `GET /api/stats` - 获取统计信息

## 🛠️ 技术栈

- **Flask** - 轻量级Python Web框架
- **JSON文件存储** - 简单可靠的数据存储
- **Tailwind CSS** - 现代化CSS框架
- **Vanilla JavaScript** - 原生JavaScript实现

## 💾 数据存储

项目使用JSON文件存储数据，文件位置：
- `data/prompts.json` - 提示词数据
- `data/categories.json` - 分类数据
- `data/tags.json` - 标签数据

## 🔧 添加新功能

1. 在 `app.py` 中添加新的API路由
2. 在 `templates/index.html` 中添加前端交互
3. 根据需要扩展数据模型

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到任何问题或有建议，请创建 Issue 或联系开发团队。