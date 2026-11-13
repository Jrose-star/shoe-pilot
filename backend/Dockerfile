# ---------- 阶段一：构建依赖 ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# 先拷贝依赖文件，利用 Docker 缓存层加速后续构建
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- 阶段二：运行环境 ----------
FROM python:3.11-slim AS runtime

# 设置环境变量，确保 Python 输出不被缓冲，便于日志查看
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 从构建阶段拷贝已安装的 Python 包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 拷贝应用代码
COPY ./app ./app

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 启动命令（生产环境建议改用 Gunicorn + UvicornWorker 获得更好并发）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]