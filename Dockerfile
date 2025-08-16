# 使用Python官方基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 升级pip并复制依赖文件
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录和文件
RUN mkdir -p data/examples data/backup && \
    echo '[]' > data/prompts.json && \
    echo '[]' > data/categories.json && \
    echo '[]' > data/tags.json

# 暴露端口
EXPOSE 5001

# 启动应用
CMD ["python", "app.py"]
