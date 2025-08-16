# 使用Python官方基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖（包含curl用于健康检查）
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 升级pip
RUN pip install --upgrade pip

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录和文件
RUN mkdir -p data/examples data/backup && \
    touch data/prompts.json data/categories.json data/tags.json && \
    echo '[]' > data/prompts.json && \
    echo '[]' > data/categories.json && \
    echo '[]' > data/tags.json

# 暴露端口
EXPOSE 5001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5001/ || exit 1

# 启动应用
CMD ["python", "app.py"]
