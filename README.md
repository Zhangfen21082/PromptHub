# 🚀 PromptHub - 智能提示词管理平台

一个现代化的AI提示词管理平台，帮助您高效收集、分类和管理各种AI提示词，提升AI使用体验。

![PromptHub](https://img.shields.io/badge/Version-1.0.0-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.7+-orange)

## ✨ 核心特性

### 📝 智能提示词管理
- **快速收集**：一键保存和管理您的AI提示词
- **多格式支持**：纯文本、JSON、Markdown格式智能识别
- **富文本编辑**：实时预览、格式化、语法高亮
- **内容检测**：自动识别内容格式并优化编辑体验

### 🏷️ 灵活分类标签系统
- **美观分类选择**：现代化自定义下拉框，支持图标化分类显示
- **智能标签选择**：显示现有标签供快速选择，避免重复创建
- **多标签支持**：为提示词添加多个相关标签
- **智能筛选**：支持分类、标签的多维度组合筛选
- **标签搜索**：实时搜索标签，快速定位目标内容
- **使用统计**：标签按使用频率排序，常用标签优先显示

### 🔍 强大的搜索引擎
- **全文搜索**：在标题、内容、描述中进行关键词搜索
- **组合筛选**：搜索、分类、标签多条件同时筛选
- **实时统计**：筛选结果数量实时显示
- **标签折叠**：智能标签管理，支持搜索和展开收起

### 📊 数据统计仪表板
- **全局统计**：提示词总数、分类数量、标签数量
- **实时更新**：当前筛选结果数量动态显示
- **使用分析**：各分类和标签的使用情况统计
- **可视化展示**：美观的彩色统计卡片

### 📥 数据导出功能
- **筛选导出**：导出当前搜索和筛选的结果
- **完整信息**：包含标题、描述、分类、标签、内容、创建时间
- **CSV格式**：支持Excel等软件打开，完美支持中文
- **安全控制**：导出操作需要管理员权限验证

### 🔧 开发者工具
- **隐藏式设计**：页面底部低调的"⚙️ Dev"按钮
- **一键测试数据**：快速加载100条示例数据进行功能演示
- **一键清空数据**：重置到空环境状态
- **自动备份**：所有操作前自动备份原数据
- **权限保护**：开发者功能需要管理员口令验证

### 📱 现代化用户界面
- **响应式设计**：完美适配桌面、平板、手机设备
- **现代UI风格**：使用Tailwind CSS构建的精美界面
- **流畅动画**：丰富的交互动画和视觉反馈效果
- **分页浏览**：优雅的分页设计，每页9条记录

### 🔐 企业级安全管理
- **权限控制**：所有修改操作需要管理员口令验证
- **加密传输**：SHA-256加密，口令不明文传输
- **数据保护**：智能处理分类/标签删除时的数据迁移
- **操作审计**：详细的操作反馈和错误提示

## 🛠️ 技术架构

### 后端技术栈
- **Framework**: Flask (轻量级Python Web框架)
- **数据存储**: JSON文件 (无数据库依赖)
- **安全认证**: SHA-256密码哈希
- **API设计**: RESTful API架构

### 前端技术栈
- **核心技术**: HTML5 + CSS3 + JavaScript (ES6+)
- **样式框架**: Tailwind CSS (通过CDN加载)
- **交互体验**: 原生JavaScript，无框架依赖
- **图标系统**: Emoji + SVG矢量图标

### 特色优势
- **零依赖部署**: 无需数据库，单文件即可运行
- **轻量级架构**: 资源占用小，启动速度快
- **高度可定制**: 配置文件灵活，易于个性化
- **跨平台支持**: 支持Windows、macOS、Linux

## 📦 快速开始

### 系统要求

```bash
# Python版本要求
Python 3.7 或更高版本

# 浏览器支持
Chrome 70+、Firefox 65+、Safari 12+、Edge 79+
```

### 安装部署

#### 1. 获取源码
```bash
git clone https://github.com/liu-kaining/PromptHub.git
cd PromptHub
```

#### 2. 环境准备
```bash
# 创建Python虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 依赖安装
```bash
# 安装项目依赖
pip install -r requirements.txt
```

#### 4. 配置应用
创建配置文件 `config.json`（可选，不创建将使用默认配置）：

```json
{
  "admin_password": "your_secure_password_here",
  "app_name": "PromptHub",
  "app_description": "智能提示词管理平台",
  "port": 5001,
  "debug": false
}
```

#### 5. 启动服务
```bash
python app.py
```

#### 6. 访问应用
打开浏览器访问：`http://localhost:5001`

---

## 🐳 Docker 部署（推荐）

使用Docker可以快速部署PromptHub，无需手动配置Python环境。

### 方式一：使用Docker Compose（推荐）

#### 1. 克隆项目
```bash
git clone https://github.com/liu-kaining/PromptHub.git
cd PromptHub
```

#### 2. 启动服务
```bash
# 构建并启动
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f prompthub
```

#### 3. 访问应用
打开浏览器访问：`http://localhost:5001`

#### 4. 管理服务
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新服务
docker-compose down
docker-compose up -d --build
```

### 方式二：直接使用Docker

#### 1. 构建镜像
```bash
docker build -t prompthub:latest .
```

#### 2. 运行容器
```bash
# 基础运行
docker run -d \
  --name prompthub \
  -p 5001:5001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json:ro \
  --restart unless-stopped \
  prompthub:latest

# 查看运行状态
docker ps
docker logs prompthub
```

#### 3. 停止和清理
```bash
# 停止容器
docker stop prompthub

# 删除容器
docker rm prompthub

# 删除镜像
docker rmi prompthub:latest
```

### Docker 部署优势

- **🚀 快速部署**：一条命令即可启动完整服务
- **🔒 环境隔离**：不依赖主机Python环境
- **📦 轻量级**：基于Python slim镜像，体积小巧
- **🔄 自动重启**：容器异常退出自动重启
- **💾 数据持久化**：数据目录挂载到主机，升级不丢失
- **⚡ 健康检查**：自动监控服务状态

## ⚙️ 配置详解

### 配置文件说明

`config.json` 文件中的各项配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `admin_password` | string | `"admin123"` | 管理员口令，用于所有修改操作的权限验证 |
| `app_name` | string | `"PromptHub"` | 应用显示名称 |
| `app_description` | string | `"智能提示词管理平台"` | 应用描述信息 |
| `port` | number | `5001` | Web服务监听端口 |
| `debug` | boolean | `true` | 调试模式开关（生产环境建议设为false） |

### 🚨 重要安全提醒

**默认管理员口令为 `admin123`，强烈建议首次使用时立即修改！**

#### 修改管理员口令步骤：
1. 编辑或创建 `config.json` 文件
2. 修改 `admin_password` 字段为您的安全密码
3. 重启应用使配置生效

```json
{
  "admin_password": "your_very_secure_password_123"
}
```

### 数据存储结构

应用数据存储在 `data/` 目录：

```
data/
├── prompts.json          # 提示词数据（生产环境初始为空）
├── categories.json       # 分类数据（生产环境初始为空）
├── tags.json            # 标签数据（生产环境初始为空）
└── examples/            # 示例数据目录
    ├── README.md            # 示例数据使用说明
    ├── sample_prompts.json  # 示例提示词（100条测试数据）
    ├── sample_categories.json # 示例分类数据
    └── sample_tags.json     # 示例标签数据
```

### 🧪 使用示例数据

为了便于测试和演示，我们提供了完整的示例数据：

#### 快速导入示例数据
```bash
# 复制示例数据到工作目录（会覆盖现有数据）
cp data/examples/sample_prompts.json data/prompts.json
cp data/examples/sample_categories.json data/categories.json  
cp data/examples/sample_tags.json data/tags.json

# 重启应用查看效果
python app.py
```

#### 示例数据包含
- **59条精选提示词**: 覆盖编程、写作、分析、创意等场景
- **6个主要分类**: 编程、写作、分析、创意、商业、教育
- **30+个标签**: Python、React、文案、策划、数据分析等

#### 恢复空数据环境
```bash
# 清空所有数据，恢复初始状态
echo '[]' > data/prompts.json
echo '[]' > data/categories.json
echo '[]' > data/tags.json
```

## 🎯 功能使用指南

### 提示词管理

#### 添加新提示词
1. 点击右上角 "➕ 添加提示词" 按钮
2. 填写基本信息：标题、描述
3. 选择分类：点击美观的下拉框，从图标化选项中选择
4. 选择内容格式：文本/JSON/Markdown
5. 输入提示词内容（支持格式化和预览）
6. 添加标签：
   - 从现有标签中快速选择（按使用频率排序）
   - 搜索现有标签快速定位
   - 输入新标签（空格键添加）
7. 输入管理员口令并保存

#### 编辑提示词
1. 点击提示词卡片上的 "✏️" 编辑按钮
2. 修改任意信息
3. 输入管理员口令确认修改

#### 删除提示词
1. 点击提示词卡片上的 "🗑️" 删除按钮
2. 确认删除操作
3. 输入管理员口令完成删除

### 搜索与筛选

#### 文本搜索
- 在搜索框输入关键词
- 支持搜索标题、内容、描述
- 实时显示搜索结果

#### 分类筛选
- 点击分类按钮进行筛选
- 支持"全部"查看所有分类
- 可与搜索和标签筛选组合使用

#### 标签筛选
- 点击标签按钮进行筛选（支持多选）
- 使用标签搜索框快速定位标签
- 点击"全部"清除标签筛选
- 支持展开/收起标签列表

### 分类与标签管理

#### 管理分类
1. 点击分类区域的 "⚙️ 管理" 按钮
2. 添加新分类（需要口令）
3. 编辑分类名称（需要口令）
4. 删除不需要的分类（需要口令）
   - 系统会自动将关联提示词移至"其他"分类

#### 管理标签
1. 点击标签区域的 "⚙️ 管理" 按钮
2. 添加新标签（需要口令）
3. 编辑标签名称（需要口令）
4. 删除不需要的标签（需要口令）
   - 系统会自动从关联提示词中移除该标签

### 数据导出

1. 使用搜索和筛选选择要导出的提示词
2. 在统计区域点击 "📥 导出数据" 按钮
3. 输入管理员口令确认
4. 系统自动下载CSV文件

导出的CSV文件包含：
- 标题、描述、分类、标签
- 完整的提示词内容
- 创建时间信息

### 🔧 开发者工具使用

#### 访问开发者面板
1. 滚动到页面底部footer区域
2. 点击灰色的 "⚙️ Dev" 按钮
3. 展开开发者工具面板

#### 加载测试数据
1. 点击 "🚀 加载测试数据" 按钮
2. 确认操作（会覆盖当前数据）
3. 输入管理员口令验证
4. 系统自动加载59条示例数据
5. 页面自动刷新显示新数据

**包含内容：**
- 59条精选提示词（涵盖编程、写作、分析等场景）
- 6个主要分类（编程、写作、分析、创意、商业、教育）
- 30+个实用标签

#### 清空所有数据
1. 点击 "🗑️ 清空所有数据" 按钮
2. 确认清空操作（不可撤销）
3. 输入管理员口令验证
4. 系统清空所有数据
5. 页面自动刷新显示空状态

**安全保障：**
- 🔐 需要管理员口令验证
- 💾 操作前自动备份到 `data/backup/` 目录
- 📅 备份文件带时间戳，便于追溯恢复
- ⚠️ 操作前明确提示影响范围

## 🔧 高级配置

### 端口配置

如果默认端口5001被占用：

```json
{
  "port": 8080
}
```

查看端口占用情况：
```bash
# macOS/Linux
lsof -i:5001
# Windows
netstat -ano | findstr :5001
```

### 生产环境部署

#### 1. 安全配置
```json
{
  "debug": false,
  "admin_password": "complex_secure_password_here"
}
```

#### 2. 使用生产级服务器
```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

#### 3. Nginx反向代理配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 数据备份与恢复

#### 定期备份
```bash
# 创建备份
tar -czf prompthub_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ config.json

# 定时备份（添加到crontab）
0 2 * * * cd /path/to/prompthub && tar -czf backup/prompthub_$(date +\%Y\%m\%d).tar.gz data/
```

#### 数据恢复
```bash
# 从备份恢复
tar -xzf prompthub_backup_20241216_143000.tar.gz
# 重启应用
python app.py
```

## 🐛 故障排除

### 常见问题解决

#### 1. 端口被占用
**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用进程
lsof -i:5001
# 终止进程
kill -9 <PID>
# 或修改配置文件端口
```

#### 2. 权限错误
**错误信息**: `Permission denied`

**解决方案**:
```bash
# 确保data目录有写权限
chmod 755 data/
chmod 644 data/*.json
```

#### 3. 配置文件错误
**错误信息**: `JSON decode error`

**解决方案**:
- 检查config.json语法是否正确
- 确保所有字符串用双引号包围
- 验证JSON格式：https://jsonlint.com/

#### 4. 口令验证失败
**可能原因**:
- config.json中的口令与输入不匹配
- 配置文件修改后未重启应用

**解决方案**:
```bash
# 检查配置文件
cat config.json
# 重启应用
python app.py
```

#### 5. 中文显示异常
**解决方案**:
- 确保终端支持UTF-8编码
- 检查浏览器字符编码设置
- 确保CSV导出时选择UTF-8编码打开

### 数据恢复

如果数据文件损坏，应用会自动创建默认空文件：

```bash
# 手动重置数据
rm -rf data/
# 重启应用，将自动创建默认数据文件
python app.py
```

从备份恢复：
```bash
cp backup/data/* data/
```

## 📋 版本更新日志

### v1.0.0 (Current) - 2025年08月
- ✅ 完整的提示词CRUD功能
- ✅ 分类和标签管理系统
- ✅ 全文搜索和多维度筛选
- ✅ 数据导出功能（CSV格式）
- ✅ 响应式用户界面设计
- ✅ 管理员权限控制系统
- ✅ 智能标签管理（搜索、折叠、排序）
- ✅ 现代化分页控件
- ✅ 数据一致性保证
- ✅ 多格式内容编辑器
- ✅ 美观的自定义分类下拉框（图标化）
- ✅ 智能标签选择体验（现有标签展示）
- ✅ 隐藏式开发者工具（一键加载/清空测试数据）
- ✅ Docker容器化部署支持
- ✅ 示例数据管理和自动备份机制

### 即将发布的功能
- 🔄 批量操作功能
- 📁 提示词文件夹分组
- 🔄 数据同步与云存储
- 📊 使用统计和分析
- 🎨 自定义主题支持

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork 项目**
   ```bash
   git clone https://github.com/your-username/PromptHub.git
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **提交更改**
   ```bash
   git commit -m 'Add some amazing feature'
   ```

4. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **创建 Pull Request**

### 贡献类型

- 🐛 Bug修复
- ✨ 新功能开发
- 📚 文档改进
- 🎨 UI/UX优化
- 🔧 性能优化
- 🧪 测试覆盖

### 代码规范

- 使用Python PEP 8代码风格
- JavaScript使用ES6+语法
- 提交信息使用约定式提交格式
- 添加适当的注释和文档

## 📄 开源许可

本项目采用 [MIT License](LICENSE) 开源许可证。

### 许可证要点
- ✅ 商业使用
- ✅ 修改源码
- ✅ 分发软件
- ✅ 私人使用
- ❗ 需保留许可证和版权声明

## 👨‍💻 作者与维护者

**liqian_liukaining**
- GitHub: [@liu-kaining](https://github.com/liu-kaining)
- 项目主页: [PromptHub](https://github.com/liu-kaining/PromptHub)

## 🎗️ 支持与反馈

### 获取帮助
- 📖 查看文档：详细使用说明
- 🐛 报告Bug：[Issues](https://github.com/liu-kaining/PromptHub/issues)
- 💡 功能建议：[Discussions](https://github.com/liu-kaining/PromptHub/discussions)
- 📧 邮件联系：通过GitHub联系

### 社区支持
- ⭐ 给项目点Star支持开发
- 🔄 分享给更多需要的朋友
- 📝 参与文档和代码贡献
- 💬 在社区中分享使用经验

---

## 💡 特别感谢

感谢所有为这个项目提供想法、反馈和贡献的用户和开发者！

**如果这个项目对您有帮助，请给它一个 ⭐ Star！您的支持是我们持续改进的动力！**

---

<div align="center">

**PromptHub - 让AI提示词管理变得简单高效**

Made with ❤️ by [liqian_liukaining](https://github.com/liu-kaining)

</div>