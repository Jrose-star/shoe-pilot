# 👟 ShoePilot - 企业级智能知识库助手

ShoePilot 是一个专为鞋类制造与销售业务打造的企业级 AI 智能助手。基于 RAG (检索增强生成) 架构，提供精准的文档问答、智能摘要与长文本处理能力。

## ✨ 核心功能

- **💬 智能问答 (Agentic RAG)**
  - 基于 LangChain/LangGraph 的意图路由，自动判断是否需要检索知识库。
  - 强制引用溯源，回答附带原文片段，杜绝大模型幻觉。
  - **流式输出 (SSE)**，打字机效果，极低首字延迟。
- **🧠 长期记忆持久化**
  - 基于 JWT 的用户认证体系。
  - 聊天会话与上下文持久化存储于 PostgreSQL，支持多端登录同步。
  - 会话列表管理（新建、重命名、删除）。
- **📚 知识库管理**
  - 支持 PDF, Word (docx), TXT, Markdown 格式文件上传。
  - 自动提取文本、分块 (Chunking)、向量化 (Embedding) 并存入 `pgvector`。
- **📝 长文档摘要**
  - 采用 Map-Reduce 策略，支持超长文档的“一页读懂”提炼。
  - 支持会议纪要提取与工作周报生成。

## 🛠️ 技术栈

**前端:** Vue 3 + Vite + Element Plus + Pinia + Vue Router + Axios
**后端:** Python 3.10 + FastAPI + SQLAlchemy + Pydantic
**数据库:** PostgreSQL + pgvector 插件
**AI 核心:** 阿里云百炼 (Qwen 模型) + LangGraph / LangChain
**认证加密:** JWT (python-jose) + Bcrypt (passlib)

---

## 🚀 本地开发指南

### 1. 环境准备

- 安装 Python 3.10+ (推荐使用 Conda)
- 安装 Node.js 18+
- 安装 PostgreSQL 15+ 并启用 `pgvector` 扩展：
  ```sql
  CREATE DATABASE shoepilot_db;
  \c shoepilot_db
  CREATE EXTENSION IF NOT EXISTS vector;
  ```
