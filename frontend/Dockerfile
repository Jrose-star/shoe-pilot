# ---------- 阶段一：构建 Vue 应用 ----------
FROM node:20-alpine AS builder

WORKDIR /app

# 先拷贝包管理文件，利用缓存
COPY package*.json ./
RUN npm ci

# 拷贝源码并构建
COPY . .
RUN npm run build

# ---------- 阶段二：Nginx 运行 ----------
FROM nginx:alpine

# 拷贝自定义 Nginx 配置（下一步创建）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段拷贝 Vue 构建产物（Vite 默认输出到 dist 目录）
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80