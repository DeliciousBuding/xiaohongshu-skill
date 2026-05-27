# ============================================================
# xiaohongshu-skill Docker 镜像
# ============================================================
# 构建：docker build -t xiaohongshu-skill .
# 运行：docker compose up
# ============================================================

FROM python:3.11-slim

# 安装 Playwright + Chromium 所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright Chromium 浏览器
RUN playwright install chromium && \
    playwright install-deps chromium

# 复制项目文件
COPY . .

# 确保数据目录和 cookie 目录存在
RUN mkdir -p /app/data /root/.xiaohongshu

# 入口
ENTRYPOINT ["python", "-m", "scripts"]
