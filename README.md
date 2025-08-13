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
- Node.js 18+
- npm 或 yarn

### 开发环境启动

1. **克隆项目**
```bash
git clone <repository-url>
cd PromptHub
```

2. **启动后端服务**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

3. **启动前端服务**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 使用Docker启动

```bash
docker-compose up -d
```

## 🏗️ 项目结构

```
PromptHub/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── main.py         # FastAPI应用
│   │   ├── models.py       # 数据模型
│   │   ├── storage.py      # 文件存储逻辑
│   │   └── api.py          # API路由
│   ├── data/               # JSON数据文件
│   ├── requirements.txt    # Python依赖
│   └── run.py             # 启动脚本
├── frontend/               # Next.js前端
│   ├── app/
│   │   ├── layout.tsx     # 根布局
│   │   ├── page.tsx       # 主页面
│   │   └── globals.css    # 全局样式
│   ├── package.json       # Node.js依赖
│   └── tailwind.config.js # Tailwind配置
└── docker-compose.yml     # Docker配置
```

## 📚 API文档

### 提示词管理

- `GET /api/v1/prompts` - 获取所有提示词
- `GET /api/v1/prompts/{id}` - 获取单个提示词
- `POST /api/v1/prompts` - 创建提示词
- `PUT /api/v1/prompts/{id}` - 更新提示词
- `DELETE /api/v1/prompts/{id}` - 删除提示词
- `POST /api/v1/prompts/{id}/use` - 使用提示词（增加使用次数）

### 分类管理

- `GET /api/v1/categories` - 获取所有分类
- `POST /api/v1/categories` - 创建分类
- `PUT /api/v1/categories/{id}` - 更新分类
- `DELETE /api/v1/categories/{id}` - 删除分类

### 标签管理

- `GET /api/v1/tags` - 获取所有标签
- `POST /api/v1/tags` - 创建标签
- `PUT /api/v1/tags/{id}` - 更新标签
- `DELETE /api/v1/tags/{id}` - 删除标签

### 搜索和统计

- `GET /api/v1/search` - 搜索提示词
- `GET /api/v1/stats` - 获取统计信息

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **Pydantic** - 数据验证和序列化
- **JSON文件存储** - 轻量级数据存储

### 前端
- **Next.js 14** - React全栈框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 实用优先的CSS框架
- **Lucide React** - 图标库

## 🔧 开发指南

### 添加新功能

1. 在 `backend/app/models.py` 中定义数据模型
2. 在 `backend/app/storage.py` 中实现存储逻辑
3. 在 `backend/app/api.py` 中添加API端点
4. 在前端组件中实现UI交互

### 数据存储

项目使用JSON文件存储数据，文件位置：
- `backend/data/prompts.json` - 提示词数据
- `backend/data/categories.json` - 分类数据
- `backend/data/tags.json` - 标签数据

### 样式定制

项目使用Tailwind CSS，可以在 `frontend/tailwind.config.js` 中自定义主题。

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
